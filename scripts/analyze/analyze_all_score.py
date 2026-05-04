#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
OJBench 综合得分分析脚本

功能：
1. 读取 exec_score_analysis.json（执行得分）
2. 读取 cr_score_analysis.json（CR 得分）
3. 计算综合得分: all_score = 0.8 × exec_score + 0.2 × cr_score
4. 将结果保存到 results/ 目录

用法:
  python3 scripts/analyze/analyze_all_score.py
  python3 scripts/analyze/analyze_all_score.py --exec-weight 0.8 --cr-weight 0.2
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

RESULTS_DIR = 'results'

# 输入文件
INPUT_EXEC_JSON = 'exec_score_analysis.json'
INPUT_CR_JSON = 'cr_score_analysis.json'

# 输出文件
OUTPUT_ALL_JSON = 'all_score_analysis.json'
OUTPUT_ALL_CSV = 'all_score_analysis.csv'
OUTPUT_ALL_DETAIL_CSV = 'all_score_detail.csv'
OUTPUT_ALL_SUMMARY = 'all_score_summary.txt'

# 默认权重
DEFAULT_EXEC_WEIGHT = 0.8
DEFAULT_CR_WEIGHT = 0.2


# ============================================================================
# 工具函数
# ============================================================================

def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Combine exec and CR scores into final score"
    )
    parser.add_argument(
        "--results-dir",
        default=RESULTS_DIR,
        help=f"Directory containing analysis results (default: {RESULTS_DIR})",
    )
    parser.add_argument(
        "--exec-weight",
        type=float,
        default=DEFAULT_EXEC_WEIGHT,
        help=f"Weight for exec score (default: {DEFAULT_EXEC_WEIGHT})",
    )
    parser.add_argument(
        "--cr-weight",
        type=float,
        default=DEFAULT_CR_WEIGHT,
        help=f"Weight for CR score (default: {DEFAULT_CR_WEIGHT})",
    )
    return parser.parse_args()


def load_json_file(path: str) -> Optional[Dict[str, Any]]:
    """Load a JSON file, return None if not found or invalid."""
    if not os.path.isfile(path):
        return None
    try:
        with open(path, 'r', encoding='utf-8') as f:
            return json.load(f)
    except (json.JSONDecodeError, UnicodeDecodeError) as e:
        sys.stderr.write(f"[WARN] Failed to load {path}: {e}\n")
        return None


def ensure_output_dir(output_dir: str):
    """确保输出目录存在"""
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
        print(f"📁 创建输出目录: {output_dir}")


# ============================================================================
# 数据加载
# ============================================================================

def load_exec_scores(results_dir: str) -> Dict[str, Dict[str, float]]:
    """
    加载执行得分
    
    返回: {'agent+model': {'problem_id': score, ...}, ...}
    """
    path = os.path.join(results_dir, INPUT_EXEC_JSON)
    data = load_json_file(path)
    
    if data is None:
        print(f"⚠️ 未找到执行得分文件: {path}")
        return {}
    
    result = {}
    for combo_key, problems in data.items():
        if not isinstance(problems, dict):
            continue
        result[combo_key] = {}
        for problem_id, info in problems.items():
            if isinstance(info, dict):
                score = info.get('final_score')
                if score is not None:
                    result[combo_key][problem_id] = float(score)
            elif isinstance(info, (int, float)):
                result[combo_key][problem_id] = float(info)
    
    return result


def load_cr_scores(results_dir: str) -> Dict[str, Dict[str, float]]:
    """
    加载 CR 得分
    
    返回: {'agent+model': {'problem_id': score, ...}, ...}
    """
    path = os.path.join(results_dir, INPUT_CR_JSON)
    data = load_json_file(path)
    
    if data is None:
        print(f"⚠️ 未找到 CR 得分文件: {path}")
        return {}
    
    result = {}
    by_agent_model = data.get('by_agent_model', {})
    
    for combo_key, combo_data in by_agent_model.items():
        if not isinstance(combo_data, dict):
            continue
        
        problems = combo_data.get('problems', {})
        result[combo_key] = {}
        
        for problem_id, info in problems.items():
            if isinstance(info, dict):
                score = info.get('final_score')
                if score is not None:
                    result[combo_key][problem_id] = float(score)
            elif isinstance(info, (int, float)):
                result[combo_key][problem_id] = float(info)
    
    return result


# ============================================================================
# 分析
# ============================================================================

def calculate_combined_scores(
    exec_scores: Dict[str, Dict[str, float]],
    cr_scores: Dict[str, Dict[str, float]],
    exec_weight: float,
    cr_weight: float
) -> Dict[str, Any]:
    """
    计算综合得分
    
    公式: all_score = exec_weight × exec_score + cr_weight × cr_score
    
    返回完整的分析结果
    """
    # 收集所有 agent+model 和 problem
    all_combos = set(exec_scores.keys()) | set(cr_scores.keys())
    all_problems = set()
    for scores in list(exec_scores.values()) + list(cr_scores.values()):
        all_problems.update(scores.keys())
    
    analysis = {
        'config': {
            'exec_weight': exec_weight,
            'cr_weight': cr_weight,
            'formula': f'all_score = {exec_weight} × exec_score + {cr_weight} × cr_score'
        },
        'by_agent_model': {},
        'by_problem': {},
        'overall': {}
    }
    
    all_combined_scores = []
    
    for combo_key in sorted(all_combos):
        combo_exec = exec_scores.get(combo_key, {})
        combo_cr = cr_scores.get(combo_key, {})
        
        # 该组合涉及的所有问题
        combo_problems = set(combo_exec.keys()) | set(combo_cr.keys())
        
        problem_details = {}
        combo_all_scores = []
        
        for problem_id in sorted(combo_problems):
            exec_score = combo_exec.get(problem_id)
            cr_score = combo_cr.get(problem_id)
            
            # 计算综合得分
            if exec_score is not None and cr_score is not None:
                # 两者都有，正常计算
                all_score = exec_weight * exec_score + cr_weight * cr_score
                score_status = 'complete'
            elif exec_score is not None:
                # 只有 exec
                all_score = exec_weight * exec_score
                score_status = 'exec_only'
            elif cr_score is not None:
                # 只有 CR
                all_score = cr_weight * cr_score
                score_status = 'cr_only'
            else:
                all_score = None
                score_status = 'missing'
            
            problem_details[problem_id] = {
                'exec_score': round(exec_score, 2) if exec_score is not None else None,
                'cr_score': round(cr_score, 2) if cr_score is not None else None,
                'all_score': round(all_score, 2) if all_score is not None else None,
                'status': score_status,
            }
            
            if all_score is not None:
                combo_all_scores.append(all_score)
                all_combined_scores.append(all_score)
        
        # 该组合的统计
        avg_score = sum(combo_all_scores) / len(combo_all_scores) if combo_all_scores else 0
        
        analysis['by_agent_model'][combo_key] = {
            'problems': problem_details,
            'statistics': {
                'count': len(combo_all_scores),
                'total_problems': len(combo_problems),
                'average_score': round(avg_score, 2),
                'min_score': round(min(combo_all_scores), 2) if combo_all_scores else None,
                'max_score': round(max(combo_all_scores), 2) if combo_all_scores else None,
            }
        }
    
    # 每题的统计
    for problem_id in sorted(all_problems):
        problem_scores = []
        for combo_key in all_combos:
            combo_data = analysis['by_agent_model'].get(combo_key, {})
            problems = combo_data.get('problems', {})
            if problem_id in problems:
                score = problems[problem_id].get('all_score')
                if score is not None:
                    problem_scores.append(score)
        
        if problem_scores:
            analysis['by_problem'][problem_id] = {
                'count': len(problem_scores),
                'average': round(sum(problem_scores) / len(problem_scores), 2),
                'min': round(min(problem_scores), 2),
                'max': round(max(problem_scores), 2),
            }
    
    # 整体统计
    if all_combined_scores:
        analysis['overall'] = {
            'total_results': len(all_combined_scores),
            'average_score': round(sum(all_combined_scores) / len(all_combined_scores), 2),
            'min_score': round(min(all_combined_scores), 2),
            'max_score': round(max(all_combined_scores), 2),
        }
    
    return analysis


# ============================================================================
# 输出
# ============================================================================

def save_analysis_json(analysis: Dict, output_dir: str):
    """保存分析结果为 JSON"""
    json_path = os.path.join(output_dir, OUTPUT_ALL_JSON)
    
    with open(json_path, 'w', encoding='utf-8') as f:
        json.dump(analysis, f, indent=2, ensure_ascii=False)
    print(f"✅ 保存: {json_path}")


def save_analysis_csv(analysis: Dict, output_dir: str):
    """保存分析结果为 CSV（汇总表）"""
    csv_path = os.path.join(output_dir, OUTPUT_ALL_CSV)
    
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
                score = combo_data['problems'][problem_id].get('all_score')
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


def save_detail_csv(analysis: Dict, output_dir: str):
    """保存详细结果为 CSV"""
    csv_path = os.path.join(output_dir, OUTPUT_ALL_DETAIL_CSV)
    
    rows = []
    for combo_key in sorted(analysis['by_agent_model'].keys()):
        parts = combo_key.split('+', 1)
        agent = parts[0] if len(parts) > 0 else ''
        model = parts[1] if len(parts) > 1 else ''
        
        combo_data = analysis['by_agent_model'][combo_key]
        for problem_id in sorted(combo_data['problems'].keys()):
            p_data = combo_data['problems'][problem_id]
            
            rows.append({
                'agent': agent,
                'model': model,
                'problem': problem_id,
                'exec_score': p_data.get('exec_score'),
                'cr_score': p_data.get('cr_score'),
                'all_score': p_data.get('all_score'),
                'status': p_data.get('status'),
            })
    
    fieldnames = ['agent', 'model', 'problem', 'exec_score', 'cr_score', 'all_score', 'status']
    
    with open(csv_path, 'w', newline='', encoding='utf-8') as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)
    print(f"✅ 保存: {csv_path}")


def save_summary(analysis: Dict, output_dir: str):
    """保存文本摘要"""
    summary_path = os.path.join(output_dir, OUTPUT_ALL_SUMMARY)
    
    config = analysis.get('config', {})
    exec_weight = config.get('exec_weight', DEFAULT_EXEC_WEIGHT)
    cr_weight = config.get('cr_weight', DEFAULT_CR_WEIGHT)
    
    with open(summary_path, 'w', encoding='utf-8') as f:
        f.write("=" * 80 + "\n")
        f.write("OJBench Combined Score Analysis Summary\n")
        f.write("=" * 80 + "\n\n")
        
        f.write(f"Formula: all_score = {exec_weight} × exec_score + {cr_weight} × cr_score\n\n")
        
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
            
            f.write(f"  Problems: {stats['count']}/{stats['total_problems']}\n")
            f.write(f"  Average Score: {stats['average_score']:.2f}\n")
            if stats['min_score'] is not None:
                f.write(f"  Min Score: {stats['min_score']:.2f}\n")
            if stats['max_score'] is not None:
                f.write(f"  Max Score: {stats['max_score']:.2f}\n")
            f.write("\n")
            
            # 每题详情
            f.write("  Problems:\n")
            f.write(f"  {'Problem':<10} {'Exec':>10} {'CR':>10} {'All':>10} {'Status':<15}\n")
            f.write(f"  {'-' * 55}\n")
            
            for problem_id in sorted(combo_data['problems'].keys()):
                p_data = combo_data['problems'][problem_id]
                exec_s = f"{p_data['exec_score']:.2f}" if p_data['exec_score'] is not None else "N/A"
                cr_s = f"{p_data['cr_score']:.2f}" if p_data['cr_score'] is not None else "N/A"
                all_s = f"{p_data['all_score']:.2f}" if p_data['all_score'] is not None else "N/A"
                status = p_data.get('status', '')
                
                f.write(f"  {problem_id:<10} {exec_s:>10} {cr_s:>10} {all_s:>10} {status:<15}\n")
        
        # 每题的统计
        f.write("\n" + "-" * 80 + "\n")
        f.write("By Problem:\n")
        f.write("-" * 80 + "\n\n")
        
        by_problem = analysis.get('by_problem', {})
        for problem_id in sorted(by_problem.keys()):
            p_stats = by_problem[problem_id]
            f.write(f"  Problem {problem_id}:\n")
            f.write(f"    Count: {p_stats['count']}, Avg: {p_stats['average']:.2f}, ")
            f.write(f"Min: {p_stats['min']:.2f}, Max: {p_stats['max']:.2f}\n")
    
    print(f"✅ 保存: {summary_path}")


def print_statistics(analysis: Dict):
    """打印统计信息"""
    config = analysis.get('config', {})
    exec_weight = config.get('exec_weight', DEFAULT_EXEC_WEIGHT)
    cr_weight = config.get('cr_weight', DEFAULT_CR_WEIGHT)
    
    print("\n" + "=" * 60)
    print(f"📊 综合得分统计 ({exec_weight}×Exec + {cr_weight}×CR)")
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
    
    print("🚀 OJBench 综合得分分析脚本")
    print("=" * 60)
    
    results_dir = args.results_dir
    exec_weight = args.exec_weight
    cr_weight = args.cr_weight
    
    # 验证权重
    total_weight = exec_weight + cr_weight
    if abs(total_weight - 1.0) > 0.001:
        print(f"⚠️ 注意: 权重总和为 {total_weight:.2f}，不等于 1.0")
    
    print(f"\n📝 计分公式: all_score = {exec_weight} × exec_score + {cr_weight} × cr_score")
    
    # 检查目录
    if not os.path.isdir(results_dir):
        print(f"❌ 结果目录不存在: {results_dir}")
        sys.exit(1)
    
    # 加载数据
    print(f"\n📂 加载数据...")
    
    exec_scores = load_exec_scores(results_dir)
    if exec_scores:
        total_exec = sum(len(p) for p in exec_scores.values())
        print(f"   执行得分: {len(exec_scores)} 个组合，{total_exec} 个题目")
    else:
        print("   ⚠️ 未找到执行得分数据")
    
    cr_scores = load_cr_scores(results_dir)
    if cr_scores:
        total_cr = sum(len(p) for p in cr_scores.values())
        print(f"   CR 得分: {len(cr_scores)} 个组合，{total_cr} 个题目")
    else:
        print("   ⚠️ 未找到 CR 得分数据")
    
    if not exec_scores and not cr_scores:
        print("\n❌ 没有任何得分数据可分析")
        sys.exit(1)
    
    # 计算综合得分
    print("\n📈 计算综合得分...")
    analysis = calculate_combined_scores(exec_scores, cr_scores, exec_weight, cr_weight)
    
    # 保存结果
    ensure_output_dir(results_dir)
    print(f"\n💾 保存结果到 {results_dir}/...")
    save_analysis_json(analysis, results_dir)
    save_analysis_csv(analysis, results_dir)
    save_detail_csv(analysis, results_dir)
    save_summary(analysis, results_dir)
    
    # 打印统计
    print_statistics(analysis)
    
    print("\n" + "=" * 60)
    print("✅ 综合得分分析完成！")


if __name__ == "__main__":
    main()
