#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
OJBench 执行得分分析脚本

功能：
1. 遍历 logs 目录，提取 submission ID
2. 调用 OJ API 获取提交详情（状态、得分等）
3. 根据 problem_registry.json 的 max_submissions 限制过滤超限提交
4. 使用加权公式计算最终得分: final_score = Σ(得分/满分 × 权重) / 总权重 × 100
5. 将结果保存到 results/ 目录

用法:
  python3 scripts/analyze/analyze_exec_score.py
"""

import os
import pathlib
import re
import json
import csv
import sys
import time
import requests
from typing import Dict, Any, Optional, Tuple, List
from collections import defaultdict
from concurrent.futures import ThreadPoolExecutor, as_completed

# ============================================================================
# 配置
# ============================================================================

LOGS_DIR = 'logs'
REGISTRY_FILE = 'config/problem_registry.json'
API_BASE_URL = "https://acm.sjtu.edu.cn"

# 输出目录
OUTPUT_DIR = 'results'

# 输出文件（会自动加上 OUTPUT_DIR 前缀）
OUTPUT_RESULTS_JSON = 'exec_results.json'
OUTPUT_RESULTS_CSV = 'exec_results.csv'
OUTPUT_SCORES_JSON = 'exec_score_analysis.json'
OUTPUT_SCORES_CSV = 'exec_score_analysis.csv'
OUTPUT_SUMMARY = 'exec_score_summary.txt'

# API 限流配置
MAX_WORKERS = 2
REQUEST_DELAY = 0.5
MAX_RETRIES = 3
RETRY_BASE_DELAY = 2

REPO_URL_PATTERN = re.compile(r'✅\s*Repository created:\s*(https://github\.com/[^\s]+)')

# ============================================================================
# 特殊评分配置
# ============================================================================

# 006 Minesweeper Advanced (2877) 特殊评分
# 根据 README：使用 baseline 线性插值
MINESWEEPER_ADVANCED_BASELINES = {
    'rubbish': 39625,      # 最低阈值，低于此得 0 分
    'baseline1': 100449,   # 达到此得 10/35 = 28.57%
    'baseline2': 136481,   # 达到此得 30/35 = 85.71%，超过此得满分
}

def calculate_minesweeper_advanced_score(raw_score: float) -> float:
    """
    计算 006 Advanced (2877) 的归一化分数
    
    评分规则（按 README）：
    - 低于 Rubbish (39625): 0%
    - Rubbish → Baseline1: 0% → 28.57% (10/35) 线性插值
    - Baseline1 → Baseline2: 28.57% → 85.71% (30/35) 线性插值
    - 超过 Baseline2: 100% (35/35) 满分
    
    返回: 0-100 的归一化分数
    """
    rubbish = MINESWEEPER_ADVANCED_BASELINES['rubbish']
    baseline1 = MINESWEEPER_ADVANCED_BASELINES['baseline1']
    baseline2 = MINESWEEPER_ADVANCED_BASELINES['baseline2']
    
    # 各阶段对应的百分比 (满分35%，换算到100)
    pct_rubbish = 0
    pct_baseline1 = 10 / 35 * 100   # 28.57%
    pct_baseline2 = 30 / 35 * 100   # 85.71%
    pct_max = 100                    # 100%
    
    if raw_score < rubbish:
        return 0
    elif raw_score < baseline1:
        # Rubbish → Baseline1: 线性插值
        ratio = (raw_score - rubbish) / (baseline1 - rubbish)
        return pct_rubbish + ratio * (pct_baseline1 - pct_rubbish)
    elif raw_score < baseline2:
        # Baseline1 → Baseline2: 线性插值
        ratio = (raw_score - baseline1) / (baseline2 - baseline1)
        return pct_baseline1 + ratio * (pct_baseline2 - pct_baseline1)
    else:
        # 超过 Baseline2: 直接满分
        return pct_max

# ============================================================================
# 工具函数
# ============================================================================

def load_oj_token() -> str:
    """从 config/environment.env 加载 OJ_TOKEN"""
    env_path = 'config/environment.env'
    if os.path.isfile(env_path):
        try:
            with open(env_path, 'r', encoding='utf-8') as f:
                for line in f:
                    line = line.strip()
                    if line and not line.startswith('#') and line.startswith('OJ_TOKEN='):
                        token = line.split('=', 1)[1].strip().strip('"').strip("'")
                        print(f"🔑 从 {env_path} 加载 OJ_TOKEN")
                        return token
        except Exception as e:
            print(f"❌ 读取 {env_path} 失败: {e}")
    return ''


def load_problem_registry() -> Dict:
    """加载问题注册表"""
    if not os.path.isfile(REGISTRY_FILE):
        print(f"❌ 未找到 {REGISTRY_FILE}")
        sys.exit(1)
    
    with open(REGISTRY_FILE, 'r', encoding='utf-8') as f:
        return json.load(f)


def get_max_submissions(registry: Dict) -> Dict[str, int]:
    """获取每个问题的最大提交次数"""
    result = {}
    default_max = registry.get('default', {}).get('max_submissions', 3)
    for problem_id, info in registry.get('problems', {}).items():
        result[problem_id] = info.get('max_submissions', default_max)
    return result


def get_problem_api_ids(registry: Dict) -> Dict[str, List[str]]:
    """获取每个问题对应的 API ID 列表"""
    result = {}
    for problem_id, info in registry.get('problems', {}).items():
        oj_id = info.get('oj_id', '')
        api_ids = [id.strip() for id in oj_id.split(',') if id.strip()]
        result[problem_id] = api_ids
    return result


def get_problem_scoring_config(registry: Dict) -> Dict[str, Dict]:
    """
    获取每个问题的得分配置
    返回: {
        'problem_id': {
            'score_weight': {'api_id': weight, ...},
            'score_full': {'api_id': full_score, ...}
        }
    }
    """
    result = {}
    for problem_id, info in registry.get('problems', {}).items():
        result[problem_id] = {
            'score_weight': info.get('score_weight', {}),
            'score_full': info.get('score_full', {})
        }
    return result


def extract_repo_url(content: str) -> str:
    """从日志中提取 GitHub 仓库 URL"""
    match = REPO_URL_PATTERN.search(content)
    return match.group(1) if match else 'N/A'


# ============================================================================
# API 客户端
# ============================================================================

class OJApiClient:
    def __init__(self, access_token: str):
        self.api_base = API_BASE_URL
        self.session = requests.Session()
        self.session.headers.update({
            "Authorization": f"Bearer {access_token}",
            "User-Agent": "OJ-Python-Client/3.0"
        })

    def _request(self, url: str, is_json: bool = True) -> Optional[Any]:
        for attempt in range(MAX_RETRIES):
            try:
                if attempt > 0:
                    delay = RETRY_BASE_DELAY * (2 ** (attempt - 1))
                    print(f"  [~] 重试 {attempt + 1}/{MAX_RETRIES}，等待 {delay}s...")
                    time.sleep(delay)
                else:
                    time.sleep(REQUEST_DELAY)
                
                response = self.session.get(url, timeout=15)
                response.raise_for_status()
                return response.json() if is_json else response.text

            except requests.exceptions.HTTPError as e:
                if e.response.status_code == 429:
                    if attempt < MAX_RETRIES - 1:
                        print(f"  [!] 429 限流，重试中...")
                        continue
                    print(f"  [!] 429 限流，已达最大重试次数")
                else:
                    print(f"  [!] HTTP {e.response.status_code}: {url}")
                return None
            except requests.exceptions.RequestException as e:
                print(f"  [!] 请求失败: {e}")
                if attempt < MAX_RETRIES - 1:
                    continue
                return None
        return None

    def get_submission(self, submission_id: int) -> Optional[Dict]:
        url = f"{self.api_base}/OnlineJudge/api/v1/submission/{submission_id}"
        return self._request(url, is_json=True)

    def get_code(self, code_url_path: str) -> Optional[str]:
        if not code_url_path or code_url_path == 'N/A':
            return 'N/A'
        url = f"{self.api_base}{code_url_path}"
        return self._request(url, is_json=False) or 'Fetch_Failed'


# ============================================================================
# 数据收集
# ============================================================================

def collect_submissions_from_logs() -> Dict[str, List[Dict]]:
    """
    从日志收集所有提交信息，按 agent+model+problem 分组
    注意：不在这里过滤，因为需要先知道 status 才能判断 abort
    返回: {(agent, model, problem): [{'sub_id': ..., 'repo_url': ..., 'log_file': ...}, ...]}
    """
    submissions = defaultdict(list)
    
    for root, dirs, files in os.walk(LOGS_DIR):
        path = pathlib.Path(root)
        if len(path.parts) != 4:
            continue
        
        agent = path.parts[1]
        model = path.parts[2]
        problem_id = path.parts[3]
        key = (agent, model, problem_id)
        
        # 提取 repo_url
        repo_url = 'N/A'
        for file_name in files:
            if file_name.startswith('oj_eval_') and file_name.endswith('.log'):
                try:
                    with open(os.path.join(root, file_name), 'r', encoding='utf-8') as f:
                        repo_url = extract_repo_url(f.read())
                        break
                except:
                    pass
        
        # 收集所有 submission_id
        for file_name in files:
            if file_name.startswith('submission_ids_') and file_name.endswith('.log'):
                log_file_path = os.path.join(root, file_name)
                try:
                    with open(log_file_path, 'r', encoding='utf-8') as f:
                        for line in f:
                            line = line.strip()
                            if not line:
                                continue
                            try:
                                record = json.loads(line)
                                sub_id = record.get('submission_id')
                                if sub_id:
                                    submissions[key].append({
                                        'sub_id': str(sub_id),
                                        'sub_id_int': int(sub_id),
                                        'repo_url': repo_url,
                                        'log_file': log_file_path
                                    })
                            except:
                                pass
                except:
                    pass
    
    # 去重并排序（但不截取，因为需要先知道 status）
    result = {}
    total = 0
    
    for key, subs in submissions.items():
        seen = set()
        unique_subs = []
        for s in subs:
            if s['sub_id'] not in seen:
                seen.add(s['sub_id'])
                unique_subs.append(s)
        
        unique_subs.sort(key=lambda x: x['sub_id_int'])
        result[key] = unique_subs
        total += len(unique_subs)
    
    print(f"\n📊 统计: 共发现 {total} 个提交")
    return result


def fetch_submission_details(client: OJApiClient, sub_info: Dict, 
                             agent: str, model: str, problem_id: str) -> Dict:
    """获取单个提交的详细信息"""
    sub_id = sub_info['sub_id']
    print(f"    -> 查询 ID: {sub_id}...")
    
    data = client.get_submission(int(sub_id))
    if not data:
        return {
            'agent': agent, 'model': model, 'problem': problem_id,
            'submission_id': sub_id, 'status': 'API_Request_Failed',
            'score': 'N/A', 'code_url': 'N/A', 'code_content': 'N/A',
            'repo_url': sub_info['repo_url'], 'api_problem_id': 'N/A',
            'log_file': sub_info['log_file']
        }
    
    status = data.get('status', 'Unknown')
    score = data.get('score', 0)
    code_url = data.get('code_url', 'N/A')
    api_problem_id = data.get('problem', {}).get('id', 'N/A')
    code_content = client.get_code(code_url)
    
    print(f"    -> 结果: Status={status}, Score={score}, API_ID={api_problem_id}")
    
    return {
        'agent': agent, 'model': model, 'problem': problem_id,
        'submission_id': sub_id, 'status': status, 'score': score,
        'code_url': code_url, 'code_content': code_content,
        'repo_url': sub_info['repo_url'], 'api_problem_id': api_problem_id,
        'log_file': sub_info['log_file']
    }


# ============================================================================
# 得分分析
# ============================================================================

def analyze_scores(results: List[Dict], problem_to_api_ids: Dict[str, List[str]], 
                   max_submissions: Dict[str, int], scoring_config: Dict[str, Dict]) -> Dict:
    """
    分析得分（加权计算）
    
    计算公式: final_score = Σ(得分/满分 × 权重) / 总权重 × 100
    
    - abort 状态的提交不计入提交次数
    - 只取前 max_submissions 个非 abort 提交计算得分
    """
    # 第一步：按 agent+model+problem 分组，收集所有提交
    submissions_by_group = defaultdict(list)
    
    for record in results:
        agent = record.get('agent', 'N/A')
        model = record.get('model', 'N/A')
        problem = record.get('problem', 'N/A')
        
        if agent == 'N/A' or model == 'N/A' or problem == 'N/A':
            continue
        
        key = (agent, model, problem)
        submissions_by_group[key].append(record)
    
    # 第二步：对每个组合，过滤 abort 并限制数量，然后加权计算得分
    analysis = {}
    
    for (agent, model, problem), records in submissions_by_group.items():
        combo_key = f"{agent}+{model}"
        if combo_key not in analysis:
            analysis[combo_key] = {}
        
        max_subs = max_submissions.get(problem, 3)
        config = scoring_config.get(problem, {})
        score_weight = config.get('score_weight', {})
        score_full = config.get('score_full', {})
        
        # 按 submission_id 排序
        try:
            records_sorted = sorted(records, key=lambda x: int(x.get('submission_id', 0)))
        except:
            records_sorted = records
        
        # 统计
        total_submissions = len(records_sorted)
        abort_count = 0
        non_abort_records = []
        
        for r in records_sorted:
            status = r.get('status', '').lower()
            # abort/aborted 不计入提交次数
            if status in ['abort', 'aborted']:
                abort_count += 1
                continue
            non_abort_records.append(r)
        
        # 只取前 max_subs 个非 abort 提交
        valid_records = non_abort_records[:max_subs]
        excluded_count = len(non_abort_records) - len(valid_records)
        
        if excluded_count > 0:
            print(f"  ⚠️  {combo_key} Problem {problem}: 排除 {excluded_count} 个超限提交 "
                  f"(非abort共 {len(non_abort_records)}, 限制 {max_subs}, abort {abort_count} 个)")
        
        # 收集每个 api_problem_id 的原始分数
        api_scores_list = defaultdict(list)
        for r in valid_records:
            api_problem_id = str(r.get('api_problem_id', 'N/A'))
            score = r.get('score', 0)
            
            try:
                score = float(score) if score not in ['N/A', None] else 0
            except:
                score = 0
            
            api_scores_list[api_problem_id].append(score)
        
        # 每个 api_problem_id 取最高分（原始分数）
        api_max_scores = {}
        for api_id, score_list in api_scores_list.items():
            if score_list:
                api_max_scores[api_id] = max(score_list)
        
        # 计算加权得分
        # final_score = Σ(得分/满分 × 权重) / 总权重 × 100
        total_weight = sum(float(score_weight.get(api_id, 1)) for api_id in problem_to_api_ids.get(problem, []))
        if total_weight == 0:
            total_weight = len(problem_to_api_ids.get(problem, [])) or 1
        
        weighted_sum = 0
        api_normalized_scores = {}  # 归一化后的分数（用于显示）
        
        for api_id, raw_score in api_max_scores.items():
            full = float(score_full.get(api_id, 100))
            weight = float(score_weight.get(api_id, 1))
            
            # 特殊处理: 006 Minesweeper Advanced (2877)
            if problem == '006' and api_id == '2877':
                normalized = calculate_minesweeper_advanced_score(raw_score)
                api_normalized_scores[api_id] = round(normalized, 2)
                # 加权累加（归一化分数已经是0-100，需要转换回比例）
                weighted_sum += (normalized / 100) * weight
            else:
                # 标准归一化到 0-100
                normalized = (raw_score / full * 100) if full > 0 else 0
                normalized = min(normalized, 100)  # 不超过 100
                api_normalized_scores[api_id] = round(normalized, 2)
                
                # 加权累加
                weighted_sum += (raw_score / full) * weight if full > 0 else 0
        
        final_score = (weighted_sum / total_weight) * 100 if total_weight > 0 else 0
        
        analysis[combo_key][problem] = {
            'api_scores': api_normalized_scores,  # 归一化后的分数
            'api_raw_scores': api_max_scores,     # 原始分数
            'final_score': round(final_score, 2),
            'total_weight': total_weight,
            'total_submissions': total_submissions,
            'abort_count': abort_count,
            'valid_submissions': len(valid_records),
            'excluded_submissions': excluded_count,
            'max_allowed': max_subs,
            'expected_api_ids': problem_to_api_ids.get(problem, [])
        }
    
    return analysis


# ============================================================================
# 输出
# ============================================================================

def ensure_output_dir():
    """确保输出目录存在"""
    if not os.path.exists(OUTPUT_DIR):
        os.makedirs(OUTPUT_DIR)
        print(f"📁 创建输出目录: {OUTPUT_DIR}")


def get_output_path(filename: str) -> str:
    """获取输出文件的完整路径"""
    return os.path.join(OUTPUT_DIR, filename)


def save_results(results: List[Dict]):
    """保存原始结果"""
    ensure_output_dir()
    
    # JSON
    json_path = get_output_path(OUTPUT_RESULTS_JSON)
    with open(json_path, 'w', encoding='utf-8') as f:
        json.dump(results, f, indent=2, ensure_ascii=False)
    print(f"✅ 保存: {json_path}")
    
    # CSV
    csv_path = get_output_path(OUTPUT_RESULTS_CSV)
    fieldnames = ['agent', 'model', 'problem', 'submission_id', 'status', 
                  'score', 'api_problem_id', 'repo_url', 'log_file']
    with open(csv_path, 'w', newline='', encoding='utf-8') as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames, extrasaction='ignore')
        writer.writeheader()
        writer.writerows(results)
    print(f"✅ 保存: {csv_path}")


def save_scores(analysis: Dict):
    """保存得分分析"""
    ensure_output_dir()
    
    # JSON
    json_path = get_output_path(OUTPUT_SCORES_JSON)
    with open(json_path, 'w', encoding='utf-8') as f:
        json.dump(analysis, f, indent=2, ensure_ascii=False)
    print(f"✅ 保存: {json_path}")
    
    # CSV
    csv_path = get_output_path(OUTPUT_SCORES_CSV)
    all_problems = sorted(set(p for combo in analysis.values() for p in combo.keys()))
    rows = []
    for combo in sorted(analysis.keys()):
        row = {'agent+model': combo}
        for problem in all_problems:
            if problem in analysis[combo]:
                row[problem] = analysis[combo][problem]['final_score']
            else:
                row[problem] = ''
        rows.append(row)
    
    with open(csv_path, 'w', newline='', encoding='utf-8') as f:
        writer = csv.DictWriter(f, fieldnames=['agent+model'] + all_problems)
        writer.writeheader()
        writer.writerows(rows)
    print(f"✅ 保存: {csv_path}")


def save_summary(analysis: Dict):
    """保存文本摘要"""
    ensure_output_dir()
    summary_path = get_output_path(OUTPUT_SUMMARY)
    with open(summary_path, 'w', encoding='utf-8') as f:
        f.write("=" * 80 + "\n")
        f.write("OJBench Score Analysis Summary\n")
        f.write("=" * 80 + "\n\n")
        
        for combo in sorted(analysis.keys()):
            f.write(f"\n{'=' * 60}\n")
            f.write(f"Agent+Model: {combo}\n")
            f.write(f"{'=' * 60}\n\n")
            
            all_scores = [d['final_score'] for d in analysis[combo].values()]
            avg = sum(all_scores) / len(all_scores) if all_scores else 0
            f.write(f"Average Score: {avg:.2f}\n")
            f.write(f"Problems: {len(analysis[combo])}\n\n")
            
            for problem in sorted(analysis[combo].keys()):
                data = analysis[combo][problem]
                valid = data.get('valid_submissions', data.get('submissions', 0))
                total = data.get('total_submissions', valid)
                abort = data.get('abort_count', 0)
                excluded = data.get('excluded_submissions', 0)
                max_allowed = data.get('max_allowed', 'N/A')
                total_weight = data.get('total_weight', 'N/A')
                
                f.write(f"  Problem {problem}: {data['final_score']:.2f} (加权, 总权重={total_weight})\n")
                f.write(f"    Valid: {valid}/{total} (limit: {max_allowed})")
                if abort > 0:
                    f.write(f", abort: {abort}")
                if excluded > 0:
                    f.write(f", excluded: {excluded}")
                f.write("\n")
                
                # 显示每个子问题的得分
                api_scores = data.get('api_scores', {})
                api_raw = data.get('api_raw_scores', {})
                if len(api_scores) > 1 or api_raw:
                    for api_id in sorted(api_scores.keys()):
                        norm_score = api_scores.get(api_id, 0)
                        raw_score = api_raw.get(api_id, 'N/A')
                        f.write(f"    - API {api_id}: {norm_score:.2f}% (raw: {raw_score})\n")
    
    print(f"✅ 保存: {summary_path}")


def print_statistics(analysis: Dict):
    """打印统计信息"""
    print("\n" + "=" * 60)
    print("📊 得分统计")
    print("=" * 60)
    
    for combo in sorted(analysis.keys()):
        scores = [d['final_score'] for d in analysis[combo].values()]
        avg = sum(scores) / len(scores) if scores else 0
        print(f"  {combo:40s} - 平均: {avg:6.2f} ({len(scores)} 题)")
    
    all_avgs = []
    for combo in analysis:
        scores = [d['final_score'] for d in analysis[combo].values()]
        if scores:
            all_avgs.append(sum(scores) / len(scores))
    
    if all_avgs:
        print(f"\n  整体平均: {sum(all_avgs) / len(all_avgs):.2f}")


# ============================================================================
# 主函数
# ============================================================================

def main():
    print("🚀 OJBench 综合分析脚本")
    print("=" * 60)
    
    # 检查目录
    if not os.path.isdir(LOGS_DIR):
        print(f"❌ 未找到 logs 目录")
        sys.exit(1)
    
    # 加载配置
    print("\n📖 加载配置...")
    token = load_oj_token()
    if not token:
        print("❌ 未配置 OJ_TOKEN")
        sys.exit(1)
    
    registry = load_problem_registry()
    max_submissions = get_max_submissions(registry)
    problem_to_api_ids = get_problem_api_ids(registry)
    scoring_config = get_problem_scoring_config(registry)
    
    print(f"   已加载 {len(max_submissions)} 个问题的配置")
    print(f"   计分方式: 加权平均 (final = Σ(得分/满分×权重) / 总权重 × 100)")
    
    # 初始化 API 客户端
    print("\n🔌 初始化 API 客户端...")
    client = OJApiClient(token)
    test = client.get_submission(1)
    if test is None:
        print("❌ API 验证失败")
        sys.exit(1)
    print("   API 验证通过")
    
    # 收集所有提交（不在这里过滤，因为需要先知道 status）
    print(f"\n📂 扫描 {LOGS_DIR} 目录...")
    submissions = collect_submissions_from_logs()
    
    # 爬取详情
    print("\n🌐 开始爬取提交详情...")
    all_results = []
    
    for (agent, model, problem_id), subs in submissions.items():
        if not subs:
            continue
        print(f"\n📄 {agent}/{model}/{problem_id} ({len(subs)} 个提交)")
        
        with ThreadPoolExecutor(max_workers=MAX_WORKERS) as executor:
            futures = {
                executor.submit(fetch_submission_details, client, sub, agent, model, problem_id): sub
                for sub in subs
            }
            for future in as_completed(futures):
                try:
                    result = future.result()
                    all_results.append(result)
                except Exception as e:
                    print(f"  [!] 错误: {e}")
    
    if not all_results:
        print("\n⚠️ 未收集到任何结果")
        return
    
    # 保存原始结果
    print(f"\n💾 保存结果到 {OUTPUT_DIR}/ ({len(all_results)} 条)...")
    save_results(all_results)
    
    # 分析得分（在这里过滤 abort 和超限提交）
    print("\n📈 分析得分（加权计算，abort 不计次数，超限提交会被排除）...")
    analysis = analyze_scores(all_results, problem_to_api_ids, max_submissions, scoring_config)
    save_scores(analysis)
    save_summary(analysis)
    
    # 打印统计
    print_statistics(analysis)
    
    print("\n" + "=" * 60)
    print("✅ 分析完成！")


if __name__ == "__main__":
    try:
        import requests
    except ImportError:
        print("❌ 请安装 requests: pip install requests")
        sys.exit(1)
    
    main()
