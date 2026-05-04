#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
OJBench Code Review 得分分析脚本

功能：
1. 遍历 cr_result 目录，读取 all_result.json 文件
2. 汇总每个 agent+model 组合的 CR 得分
3. 计算统计数据（平均分、完成题数等）
4. 将结果保存到 results/ 目录

用法:
  python3 scripts/analyze/analyze_cr_score.py
  python3 scripts/analyze/analyze_cr_score.py --cr-result-root /path/to/cr_result
"""

import os
import json
import csv
import sys
import argparse
from typing import Dict, Any, List, Optional
from collections import defaultdict
from pathlib import Path


# ============================================================================
# 配置
# ============================================================================

CR_RESULT_DIR = 'cr_result'
OUTPUT_DIR = 'results'

# 输出文件
OUTPUT_CR_JSON = 'cr_score_analysis.json'
OUTPUT_CR_CSV = 'cr_score_analysis.csv'
OUTPUT_CR_DETAIL_CSV = 'cr_score_detail.csv'
OUTPUT_CR_SUMMARY = 'cr_score_summary.txt'


# ============================================================================
# 工具函数
# ============================================================================

def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Analyze Code Review scores from cr_result directory"
    )
    parser.add_argument(
        "--cr-result-root",
        default=CR_RESULT_DIR,
        help=f"Root directory containing CR results (default: {CR_RESULT_DIR})",
    )
    parser.add_argument(
        "--output-dir",
        default=OUTPUT_DIR,
        help=f"Output directory for analysis results (default: {OUTPUT_DIR})",
    )
    return parser.parse_args()


def load_json_file(path: Path) -> Optional[Dict[str, Any]]:
    """Load a JSON file, return None if not found or invalid."""
    if not path.is_file():
        return None
    try:
        with path.open(encoding="utf-8") as fh:
            return json.load(fh)
    except (json.JSONDecodeError, UnicodeDecodeError) as e:
        sys.stderr.write(f"[WARN] Failed to load {path}: {e}\n")
        return None


def ensure_output_dir(output_dir: str):
    """确保输出目录存在"""
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
        print(f"📁 创建输出目录: {output_dir}")


# ============================================================================
# 数据收集
# ============================================================================

def collect_cr_results(cr_result_root: Path) -> Dict[str, Dict[str, Dict]]:
    """
    从 cr_result 目录收集所有 CR 结果
    
    返回: {
        'agent+model': {
            'problem_id': {
                'final_score': float,
                'cr_evaluation': {...},
                'llm_review': {...},
                'repo_url': str,
                ...
            }
        }
    }
    """
    results = defaultdict(dict)
    
    if not cr_result_root.is_dir():
        print(f"❌ CR 结果目录不存在: {cr_result_root}")
        return results
    
    # 遍历 cr_result/{agent}/{model}/{problem_id}/all_result.json
    for agent_dir in sorted(cr_result_root.iterdir()):
        if not agent_dir.is_dir():
            continue
        agent = agent_dir.name
        
        for model_dir in sorted(agent_dir.iterdir()):
            if not model_dir.is_dir():
                continue
            model = model_dir.name
            combo_key = f"{agent}+{model}"
            
            for problem_dir in sorted(model_dir.iterdir()):
                if not problem_dir.is_dir():
                    continue
                problem_id = problem_dir.name
                
                # 读取 all_result.json
                all_result_path = problem_dir / "all_result.json"
                data = load_json_file(all_result_path)
                
                if data is None:
                    # 尝试读取单独的 cr_evaluation.json 或 result.json
                    cr_eval = load_json_file(problem_dir / "cr_evaluation.json")
                    llm_result = load_json_file(problem_dir / "result.json")
                    
                    if cr_eval is None and llm_result is None:
                        continue
                    
                    # 简单合并（没有 all_result.json 的情况）
                    data = {
                        'cr_evaluation': cr_eval,
                        'llm_review': llm_result,
                        'score_calculation': {
                            'final_score_0_100': None  # 无法计算
                        }
                    }
                
                # 提取分数
                score_calc = data.get('score_calculation', {})
                final_score = score_calc.get('final_score_0_100')
                
                # 兼容旧的 20 分制
                if final_score is None:
                    final_score_20 = score_calc.get('final_score_0_20')
                    if final_score_20 is not None:
                        final_score = final_score_20 * 5  # 转换为 100 分制
                
                results[combo_key][problem_id] = {
                    'final_score': final_score,
                    'score_calculation': score_calc,
                    'cr_evaluation': data.get('cr_evaluation'),
                    'llm_review': data.get('llm_review'),
                    'mapped_scores': data.get('mapped_scores', []),
                    'repo_url': data.get('repo_url', 'N/A'),
                    'all_result_path': str(all_result_path),
                }
    
    return results


# ============================================================================
# 分析
# ============================================================================

def analyze_cr_scores(results: Dict[str, Dict[str, Dict]]) -> Dict[str, Any]:
    """
    分析 CR 得分
    
    返回汇总统计
    """
    analysis = {
        'by_agent_model': {},
        'by_problem': defaultdict(list),
        'overall': {}
    }
    
    all_scores = []
    
    for combo_key, problems in results.items():
        combo_scores = []
        combo_details = {}
        
        for problem_id, data in problems.items():
            score = data.get('final_score')
            
            if score is not None:
                combo_scores.append(score)
                all_scores.append(score)
                analysis['by_problem'][problem_id].append({
                    'agent_model': combo_key,
                    'score': score
                })
            
            combo_details[problem_id] = {
                'final_score': score,
                'repo_url': data.get('repo_url', 'N/A'),
                'cr_approved': data.get('cr_evaluation', {}).get('approved') if data.get('cr_evaluation') else None,
                'cr_total': data.get('cr_evaluation', {}).get('total') if data.get('cr_evaluation') else None,
                'commit_count': data.get('cr_evaluation', {}).get('commit_count') if data.get('cr_evaluation') else None,
            }
        
        # 计算该组合的统计
        avg_score = sum(combo_scores) / len(combo_scores) if combo_scores else 0
        
        analysis['by_agent_model'][combo_key] = {
            'problems': combo_details,
            'statistics': {
                'count': len(combo_scores),
                'total_problems': len(problems),
                'average_score': round(avg_score, 2),
                'min_score': round(min(combo_scores), 2) if combo_scores else None,
                'max_score': round(max(combo_scores), 2) if combo_scores else None,
                'scores_list': [round(s, 2) for s in sorted(combo_scores)]
            }
        }
    
    # 整体统计
    if all_scores:
        analysis['overall'] = {
            'total_results': len(all_scores),
            'average_score': round(sum(all_scores) / len(all_scores), 2),
            'min_score': round(min(all_scores), 2),
            'max_score': round(max(all_scores), 2),
        }
    
    # 每题的统计
    problem_stats = {}
    for problem_id, entries in analysis['by_problem'].items():
        scores = [e['score'] for e in entries]
        if scores:
            problem_stats[problem_id] = {
                'count': len(scores),
                'average': round(sum(scores) / len(scores), 2),
                'min': round(min(scores), 2),
                'max': round(max(scores), 2),
            }
    analysis['problem_statistics'] = problem_stats
    
    return analysis


# ============================================================================
# 输出
# ============================================================================

def save_analysis_json(analysis: Dict, output_dir: str):
    """保存分析结果为 JSON"""
    json_path = os.path.join(output_dir, OUTPUT_CR_JSON)
    
    # 转换 defaultdict 为普通 dict
    output = {
        'by_agent_model': analysis['by_agent_model'],
        'problem_statistics': analysis.get('problem_statistics', {}),
        'overall': analysis['overall'],
    }
    
    with open(json_path, 'w', encoding='utf-8') as f:
        json.dump(output, f, indent=2, ensure_ascii=False)
    print(f"✅ 保存: {json_path}")


def save_analysis_csv(analysis: Dict, output_dir: str):
    """保存分析结果为 CSV（汇总表）"""
    csv_path = os.path.join(output_dir, OUTPUT_CR_CSV)
    
    # 收集所有问题 ID
    all_problems = set()
    for combo_data in analysis['by_agent_model'].values():
        all_problems.update(combo_data['problems'].keys())
    all_problems = sorted(all_problems)
    
    rows = []
    for combo_key in sorted(analysis['by_agent_model'].keys()):
        combo_data = analysis['by_agent_model'][combo_key]
        row = {
            'agent+model': combo_key,
            'average': combo_data['statistics']['average_score'],
            'count': combo_data['statistics']['count'],
        }
        
        for problem_id in all_problems:
            if problem_id in combo_data['problems']:
                score = combo_data['problems'][problem_id].get('final_score')
                row[problem_id] = score if score is not None else ''
            else:
                row[problem_id] = ''
        
        rows.append(row)
    
    fieldnames = ['agent+model', 'average', 'count'] + all_problems
    
    with open(csv_path, 'w', newline='', encoding='utf-8') as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)
    print(f"✅ 保存: {csv_path}")


def save_detail_csv(results: Dict[str, Dict[str, Dict]], output_dir: str):
    """保存详细结果为 CSV"""
    csv_path = os.path.join(output_dir, OUTPUT_CR_DETAIL_CSV)
    
    rows = []
    for combo_key, problems in sorted(results.items()):
        parts = combo_key.split('+', 1)
        agent = parts[0] if len(parts) > 0 else ''
        model = parts[1] if len(parts) > 1 else ''
        
        for problem_id, data in sorted(problems.items()):
            cr_eval = data.get('cr_evaluation') or {}
            score_calc = data.get('score_calculation') or {}
            
            rows.append({
                'agent': agent,
                'model': model,
                'problem': problem_id,
                'final_score': data.get('final_score'),
                'cr_approved': cr_eval.get('approved'),
                'cr_total': cr_eval.get('total'),
                'commit_count': cr_eval.get('commit_count'),
                'llm_achieved': score_calc.get('llm_review', {}).get('total_achieved_score') if isinstance(score_calc.get('llm_review'), dict) else None,
                'llm_possible': score_calc.get('llm_review', {}).get('total_possible_score') if isinstance(score_calc.get('llm_review'), dict) else None,
                'repo_url': data.get('repo_url', 'N/A'),
            })
    
    fieldnames = ['agent', 'model', 'problem', 'final_score', 
                  'cr_approved', 'cr_total', 'commit_count',
                  'llm_achieved', 'llm_possible', 'repo_url']
    
    with open(csv_path, 'w', newline='', encoding='utf-8') as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)
    print(f"✅ 保存: {csv_path}")


def save_summary(analysis: Dict, output_dir: str):
    """保存文本摘要"""
    summary_path = os.path.join(output_dir, OUTPUT_CR_SUMMARY)
    
    with open(summary_path, 'w', encoding='utf-8') as f:
        f.write("=" * 80 + "\n")
        f.write("OJBench Code Review Score Analysis Summary\n")
        f.write("=" * 80 + "\n\n")
        
        # 整体统计
        overall = analysis.get('overall', {})
        if overall:
            f.write("Overall Statistics:\n")
            f.write(f"  Total Results: {overall.get('total_results', 0)}\n")
            f.write(f"  Average Score: {overall.get('average_score', 0):.2f}\n")
            f.write(f"  Min Score: {overall.get('min_score', 0):.2f}\n")
            f.write(f"  Max Score: {overall.get('max_score', 0):.2f}\n")
            f.write("\n")
        
        # 每个 agent+model 的统计
        f.write("-" * 80 + "\n")
        f.write("By Agent+Model:\n")
        f.write("-" * 80 + "\n\n")
        
        for combo_key in sorted(analysis['by_agent_model'].keys()):
            combo_data = analysis['by_agent_model'][combo_key]
            stats = combo_data['statistics']
            
            f.write(f"\n{'=' * 60}\n")
            f.write(f"Agent+Model: {combo_key}\n")
            f.write(f"{'=' * 60}\n\n")
            
            f.write(f"  Problems with CR: {stats['count']}/{stats['total_problems']}\n")
            f.write(f"  Average Score: {stats['average_score']:.2f}\n")
            if stats['min_score'] is not None:
                f.write(f"  Min Score: {stats['min_score']:.2f}\n")
            if stats['max_score'] is not None:
                f.write(f"  Max Score: {stats['max_score']:.2f}\n")
            f.write("\n")
            
            # 每题详情
            f.write("  Problems:\n")
            for problem_id in sorted(combo_data['problems'].keys()):
                p_data = combo_data['problems'][problem_id]
                score = p_data.get('final_score')
                score_str = f"{score:.2f}" if score is not None else "N/A"
                
                cr_info = ""
                if p_data.get('cr_approved') is not None:
                    cr_info = f" (CR: {p_data['cr_approved']}/{p_data['cr_total']}"
                    if p_data.get('commit_count') is not None:
                        cr_info += f", commits: {p_data['commit_count']}"
                    cr_info += ")"
                
                f.write(f"    Problem {problem_id}: {score_str}{cr_info}\n")
        
        # 每题的统计
        f.write("\n" + "-" * 80 + "\n")
        f.write("By Problem:\n")
        f.write("-" * 80 + "\n\n")
        
        problem_stats = analysis.get('problem_statistics', {})
        for problem_id in sorted(problem_stats.keys()):
            p_stats = problem_stats[problem_id]
            f.write(f"  Problem {problem_id}:\n")
            f.write(f"    Count: {p_stats['count']}, Avg: {p_stats['average']:.2f}, ")
            f.write(f"Min: {p_stats['min']:.2f}, Max: {p_stats['max']:.2f}\n")
    
    print(f"✅ 保存: {summary_path}")


def print_statistics(analysis: Dict):
    """打印统计信息"""
    print("\n" + "=" * 60)
    print("📊 CR 得分统计")
    print("=" * 60)
    
    for combo_key in sorted(analysis['by_agent_model'].keys()):
        stats = analysis['by_agent_model'][combo_key]['statistics']
        count = stats['count']
        total = stats['total_problems']
        avg = stats['average_score']
        print(f"  {combo_key:40s} - 平均: {avg:6.2f} ({count}/{total} 题)")
    
    overall = analysis.get('overall', {})
    if overall:
        print(f"\n  整体平均: {overall.get('average_score', 0):.2f}")
        print(f"  总结果数: {overall.get('total_results', 0)}")


# ============================================================================
# 主函数
# ============================================================================

def main():
    args = parse_args()
    
    print("🚀 OJBench Code Review 得分分析脚本")
    print("=" * 60)
    
    cr_result_root = Path(args.cr_result_root).resolve()
    output_dir = args.output_dir
    
    # 检查目录
    if not cr_result_root.is_dir():
        print(f"❌ CR 结果目录不存在: {cr_result_root}")
        sys.exit(1)
    
    print(f"\n📂 扫描目录: {cr_result_root}")
    
    # 收集结果
    results = collect_cr_results(cr_result_root)
    
    if not results:
        print("\n⚠️ 未找到任何 CR 结果")
        return
    
    total_combos = len(results)
    total_problems = sum(len(p) for p in results.values())
    print(f"   找到 {total_combos} 个 agent+model 组合，共 {total_problems} 个题目结果")
    
    # 分析
    print("\n📈 分析 CR 得分...")
    analysis = analyze_cr_scores(results)
    
    # 保存结果
    ensure_output_dir(output_dir)
    print(f"\n💾 保存结果到 {output_dir}/...")
    save_analysis_json(analysis, output_dir)
    save_analysis_csv(analysis, output_dir)
    save_detail_csv(results, output_dir)
    save_summary(analysis, output_dir)
    
    # 打印统计
    print_statistics(analysis)
    
    print("\n" + "=" * 60)
    print("✅ CR 得分分析完成！")


if __name__ == "__main__":
    main()
