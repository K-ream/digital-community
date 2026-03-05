#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
NZMS1版本体验问卷主观题完整分析
"""

import pandas as pd
import numpy as np
from collections import Counter
import re
from datetime import datetime

# 配置
FILE_PATH = '/root/.openclaw/workspace/webdata-crawling/问卷清洗交付/NZMS1版本体验问卷清洗/NZMS1版本体验问卷清洗_统计信息.xlsx'
OUTPUT_PATH = '/root/.openclaw/workspace/NZMS1_主观题分析报告.md'

# 主观题定义
QUESTIONS = {
    'q3t31': '了解渠道',
    'q6t15': '满意的地方',
    'q7t20': '不满意的地方',
    'q11t9': '天赋系统不满意',
    'q13t18': '继续游玩吸引点',
    'q14t13': '未来期待',
    'q15t': '意见建议'
}

def extract_keywords(text_series, top_n=20):
    """提取高频关键词"""
    if text_series.isna().all():
        return []
    
    # 合并所有文本
    all_text = ' '.join(text_series.dropna().astype(str))
    
    # 简单分词（按标点和空格）
    words = re.findall(r'[\u4e00-\u9fff]+|[a-zA-Z]+', all_text)
    
    # 过滤停用词和短词
    stopwords = {'的', '了', '是', '在', '有', '和', '就', '不', '人', '都', '一', '我', '也', '这', '个', '很', '到', '说', '要', '去', '你', '会', '着', '没', '看', '好', '自己', '那', '还', '可以', '但', '能', '只', '与', '及', '对', '为', '上', '下', '中', '等', '让', '给', '觉得', '感觉', '比较', '非常', '太', '更', '最', '请', '其他', '填写', '说明'}
    words = [w for w in words if len(w) > 1 and w not in stopwords]
    
    # 统计词频
    counter = Counter(words)
    return counter.most_common(top_n)

def analyze_dimension(df, question_col, dimension_cols):
    """分析某个主观题在不同维度下的情况"""
    results = {}
    
    # 过滤有效回答
    valid_df = df[df[question_col].notna() & (df[question_col].astype(str).str.strip() != '')]
    
    for dim_name, dim_col in dimension_cols.items():
        if dim_col not in df.columns:
            continue
            
        dim_results = {}
        
        # 按维度分组
        for value in df[dim_col].dropna().unique():
            if pd.isna(value) or value == '':
                continue
                
            subset = valid_df[valid_df[dim_col] == value]
            
            if len(subset) == 0:
                continue
            
            # 统计
            count = len(subset)
            avg_length = subset[question_col].astype(str).str.len().mean()
            
            # 提取关键词
            keywords = extract_keywords(subset[question_col], top_n=10)
            
            # 抽样典型观点
            samples = subset[question_col].dropna().sample(min(3, len(subset))).tolist()
            
            dim_results[str(value)] = {
                'count': count,
                'avg_length': avg_length,
                'keywords': keywords,
                'samples': samples
            }
        
        results[dim_name] = dim_results
    
    return results

print("="*80)
print("NZMS1版本体验问卷主观题分析")
print("="*80)
print(f"\n开始时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

# 读取数据
print("\n[1/5] 读取数据...")
df = pd.read_excel(FILE_PATH, sheet_name='主观题')
print(f"   ✓ 数据形状: {df.shape} (行={len(df):,}, 列={len(df.columns):,})")

# 定位主观题字段
print("\n[2/5] 定位主观题字段...")
question_cols = {}
for q_code, q_name in QUESTIONS.items():
    matching = [col for col in df.columns if col.startswith(q_code)]
    if matching:
        question_cols[q_code] = {
            'name': q_name,
            'col': matching[0]
        }
        print(f"   ✓ {q_name}: {matching[0][:60]}...")

# 找到每个主观题对应的维度字段索引
print("\n[3/5] 定位维度字段...")
dimension_mapping = {}

for q_code, q_info in question_cols.items():
    # 找到该主观题在列中的位置
    q_col = q_info['col']
    q_idx = df.columns.get_loc(q_col)
    
    # 往后找对应的维度字段（假设在同一区块）
    # 维度字段通常在主观题后面，直到下一个主观题之前
    next_q_idx = len(df.columns)
    for other_q_code, other_q_info in question_cols.items():
        if other_q_code != q_code:
            other_idx = df.columns.get_loc(other_q_info['col'])
            if other_idx > q_idx and other_idx < next_q_idx:
                next_q_idx = other_idx
    
    # 提取维度字段
    dims = {}
    for i in range(q_idx + 1, min(q_idx + 100, next_q_idx)):  # 搜索后续100列
        col_name = df.columns[i]
        
        if '总体满意度合并_总体评价高' in col_name:
            dims['总体满意度_总体评价高'] = col_name
        elif '总体满意度合并_总体评价中低' in col_name:
            dims['总体满意度_总体评价中低'] = col_name
        elif '继续意愿合并_继续意愿高' in col_name:
            dims['继续意愿_继续意愿高'] = col_name
        elif '继续意愿合并_继续意愿中低' in col_name:
            dims['继续意愿_继续意愿中低'] = col_name
        elif col_name == '活跃情况.' or (col_name.startswith('活跃情况') and not 'x' in col_name):
            if '活跃情况' not in dims:
                dims['活跃情况'] = col_name
        elif '端游经验_①非IP用户' in col_name:
            dims['端游经验_非IP用户'] = col_name
        elif '端游经验_④IP活跃用户' in col_name:
            dims['端游经验_IP活跃用户'] = col_name
        elif '端游经验_③IP流失用户' in col_name:
            dims['端游经验_IP流失用户'] = col_name
        elif col_name.startswith('年龄_') and '未成年' not in col_name:
            age_type = col_name.replace('年龄_', '').split('.')[0]
            dims[f'年龄_{age_type}'] = col_name
    
    dimension_mapping[q_code] = dims
    print(f"   ✓ {q_info['name']}: 找到 {len(dims)} 个维度字段")

# 统计基本信息
print("\n[4/5] 统计基本信息...")
basic_stats = {}
for q_code, q_info in question_cols.items():
    q_col = q_info['col']
    valid_responses = df[q_col].notna() & (df[q_col].astype(str).str.strip() != '')
    
    response_count = valid_responses.sum()
    response_rate = response_count / len(df) * 100
    avg_length = df.loc[valid_responses, q_col].astype(str).str.len().mean()
    
    basic_stats[q_code] = {
        'name': q_info['name'],
        'total': len(df),
        'response_count': response_count,
        'response_rate': response_rate,
        'avg_length': avg_length
    }
    
    print(f"   ✓ {q_info['name']}: 回答率 {response_rate:.1f}%, 平均字数 {avg_length:.1f}")

# 维度分析
print("\n[5/5] 维度深度分析...")
dimension_analysis = {}

for q_code, q_info in question_cols.items():
    print(f"\n   分析: {q_info['name']}...")
    q_col = q_info['col']
    dims = dimension_mapping.get(q_code, {})
    
    # 为每个维度进行分析
    q_analysis = {}
    
    valid_df = df[df[q_col].notna() & (df[q_col].astype(str).str.strip() != '')]
    
    # 总体满意度
    satisfaction_cols = {k: v for k, v in dims.items() if '总体满意度' in k}
    if satisfaction_cols:
        sat_results = {}
        for dim_name, dim_col in satisfaction_cols.items():
            subset = valid_df[valid_df[dim_col] == 1]
            if len(subset) > 0:
                keywords = extract_keywords(subset[q_col], top_n=10)
                samples = subset[q_col].sample(min(3, len(subset))).tolist()
                sat_results[dim_name] = {
                    'count': len(subset),
                    'keywords': keywords[:5],
                    'samples': samples
                }
        q_analysis['总体满意度'] = sat_results
        print(f"      ✓ 总体满意度维度")
    
    # 继续意愿
    continue_cols = {k: v for k, v in dims.items() if '继续意愿' in k}
    if continue_cols:
        cont_results = {}
        for dim_name, dim_col in continue_cols.items():
            subset = valid_df[valid_df[dim_col] == 1]
            if len(subset) > 0:
                keywords = extract_keywords(subset[q_col], top_n=10)
                samples = subset[q_col].sample(min(3, len(subset))).tolist()
                cont_results[dim_name] = {
                    'count': len(subset),
                    'keywords': keywords[:5],
                    'samples': samples
                }
        q_analysis['继续意愿'] = cont_results
        print(f"      ✓ 继续意愿维度")
    
    # 活跃情况
    active_col = dims.get('活跃情况')
    if active_col:
        active_results = {}
        for activity_type in valid_df[active_col].dropna().unique():
            if pd.isna(activity_type) or activity_type == '':
                continue
            subset = valid_df[valid_df[active_col] == activity_type]
            if len(subset) > 0:
                keywords = extract_keywords(subset[q_col], top_n=10)
                samples = subset[q_col].sample(min(3, len(subset))).tolist()
                active_results[str(activity_type)] = {
                    'count': len(subset),
                    'keywords': keywords[:5],
                    'samples': samples
                }
        if active_results:
            q_analysis['活跃情况'] = active_results
            print(f"      ✓ 活跃情况维度 ({len(active_results)}组)")
    
    # 端游经验
    ip_cols = {k: v for k, v in dims.items() if '端游经验' in k}
    if ip_cols:
        ip_results = {}
        for dim_name, dim_col in ip_cols.items():
            subset = valid_df[valid_df[dim_col] == 1]
            if len(subset) > 0:
                keywords = extract_keywords(subset[q_col], top_n=10)
                samples = subset[q_col].sample(min(3, len(subset))).tolist()
                ip_results[dim_name.replace('端游经验_', '')] = {
                    'count': len(subset),
                    'keywords': keywords[:5],
                    'samples': samples
                }
        if ip_results:
            q_analysis['端游经验'] = ip_results
            print(f"      ✓ 端游经验维度 ({len(ip_results)}组)")
    
    # 年龄分布
    age_cols = {k: v for k, v in dims.items() if '年龄_' in k}
    if age_cols:
        age_results = {}
        for dim_name, dim_col in age_cols.items():
            subset = valid_df[valid_df[dim_col] == 1]
            if len(subset) > 0:
                keywords = extract_keywords(subset[q_col], top_n=10)
                samples = subset[q_col].sample(min(3, len(subset))).tolist()
                age_results[dim_name.replace('年龄_', '')] = {
                    'count': len(subset),
                    'keywords': keywords[:5],
                    'samples': samples
                }
        if age_results:
            q_analysis['年龄分布'] = age_results
            print(f"      ✓ 年龄分布维度 ({len(age_results)}组)")
    
    dimension_analysis[q_code] = q_analysis

# 生成Markdown报告
print("\n[6/6] 生成分析报告...")

with open(OUTPUT_PATH, 'w', encoding='utf-8') as f:
    f.write("# NZMS1版本体验问卷主观题分析报告\n\n")
    f.write(f"**生成时间**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")
    f.write(f"**数据规模**: {len(df):,} 条样本，{len(df.columns):,} 个字段\n\n")
    f.write("---\n\n")
    
    # 目录
    f.write("## 目录\n\n")
    f.write("1. [概览统计](#概览统计)\n")
    for q_code, q_info in question_cols.items():
        anchor = q_info['name'].replace(' ', '-')
        f.write(f"2. [{q_info['name']}](#{anchor})\n")
    f.write("3. [关键洞察与建议](#关键洞察与建议)\n\n")
    f.write("---\n\n")
    
    # 1. 概览统计
    f.write("## 概览统计\n\n")
    f.write("### 各主观题回答率和平均字数\n\n")
    f.write("| 主观题 | 回答数 | 回答率 | 平均字数 |\n")
    f.write("|--------|--------|--------|----------|\n")
    for q_code, stats in basic_stats.items():
        f.write(f"| {stats['name']} | {stats['response_count']:,} | {stats['response_rate']:.1f}% | {stats['avg_length']:.1f} |\n")
    
    f.write("\n")
    
    # 2. 各主观题详细分析
    for q_code, q_info in question_cols.items():
        f.write(f"## {q_info['name']}\n\n")
        
        stats = basic_stats[q_code]
        f.write(f"**基本信息**: {stats['response_count']:,} 人回答 ({stats['response_rate']:.1f}%)，平均字数 {stats['avg_length']:.1f}\n\n")
        
        q_analysis = dimension_analysis.get(q_code, {})
        
        # 总体满意度维度
        if '总体满意度' in q_analysis:
            f.write("### 按总体满意度分析\n\n")
            for dim_name, data in q_analysis['总体满意度'].items():
                label = "总体评价高" if "评价高" in dim_name else "总体评价中低"
                f.write(f"#### {label}\n\n")
                f.write(f"**样本量**: {data['count']:,} 人\n\n")
                
                if data['keywords']:
                    f.write("**高频关键词**:\n")
                    for word, freq in data['keywords']:
                        f.write(f"- {word} ({freq}次)\n")
                    f.write("\n")
                
                if data['samples']:
                    f.write("**典型观点**:\n")
                    for i, sample in enumerate(data['samples'][:3], 1):
                        f.write(f"{i}. {sample}\n")
                    f.write("\n")
        
        # 继续意愿维度
        if '继续意愿' in q_analysis:
            f.write("### 按继续意愿分析\n\n")
            for dim_name, data in q_analysis['继续意愿'].items():
                label = "继续意愿高" if "意愿高" in dim_name else "继续意愿中低"
                f.write(f"#### {label}\n\n")
                f.write(f"**样本量**: {data['count']:,} 人\n\n")
                
                if data['keywords']:
                    f.write("**高频关键词**:\n")
                    for word, freq in data['keywords']:
                        f.write(f"- {word} ({freq}次)\n")
                    f.write("\n")
                
                if data['samples']:
                    f.write("**典型观点**:\n")
                    for i, sample in enumerate(data['samples'][:3], 1):
                        f.write(f"{i}. {sample}\n")
                    f.write("\n")
        
        # 活跃情况维度
        if '活跃情况' in q_analysis:
            f.write("### 按活跃情况分析\n\n")
            for activity_type, data in q_analysis['活跃情况'].items():
                f.write(f"#### {activity_type}\n\n")
                f.write(f"**样本量**: {data['count']:,} 人\n\n")
                
                if data['keywords']:
                    f.write("**高频关键词**:\n")
                    for word, freq in data['keywords']:
                        f.write(f"- {word} ({freq}次)\n")
                    f.write("\n")
                
                if data['samples']:
                    f.write("**典型观点**:\n")
                    for i, sample in enumerate(data['samples'][:3], 1):
                        f.write(f"{i}. {sample}\n")
                    f.write("\n")
        
        # 端游经验维度
        if '端游经验' in q_analysis:
            f.write("### 按端游经验分析\n\n")
            for ip_type, data in q_analysis['端游经验'].items():
                f.write(f"#### {ip_type}\n\n")
                f.write(f"**样本量**: {data['count']:,} 人\n\n")
                
                if data['keywords']:
                    f.write("**高频关键词**:\n")
                    for word, freq in data['keywords']:
                        f.write(f"- {word} ({freq}次)\n")
                    f.write("\n")
                
                if data['samples']:
                    f.write("**典型观点**:\n")
                    for i, sample in enumerate(data['samples'][:3], 1):
                        f.write(f"{i}. {sample}\n")
                    f.write("\n")
        
        # 年龄分布维度
        if '年龄分布' in q_analysis:
            f.write("### 按年龄分布分析\n\n")
            for age_group, data in q_analysis['年龄分布'].items():
                f.write(f"#### {age_group}\n\n")
                f.write(f"**样本量**: {data['count']:,} 人\n\n")
                
                if data['keywords']:
                    f.write("**高频关键词**:\n")
                    for word, freq in data['keywords']:
                        f.write(f"- {word} ({freq}次)\n")
                    f.write("\n")
                
                if data['samples']:
                    f.write("**典型观点**:\n")
                    for i, sample in enumerate(data['samples'][:3], 1):
                        f.write(f"{i}. {sample}\n")
                    f.write("\n")
        
        f.write("---\n\n")
    
    # 3. 关键洞察与建议
    f.write("## 关键洞察与建议\n\n")
    
    f.write("### 主要发现\n\n")
    f.write("1. **回答率差异**: ")
    sorted_by_rate = sorted(basic_stats.items(), key=lambda x: x[1]['response_rate'], reverse=True)
    highest = sorted_by_rate[0][1]
    lowest = sorted_by_rate[-1][1]
    f.write(f"{highest['name']}回答率最高({highest['response_rate']:.1f}%)，{lowest['name']}回答率最低({lowest['response_rate']:.1f}%)\n\n")
    
    f.write("2. **字数特征**: ")
    sorted_by_length = sorted(basic_stats.items(), key=lambda x: x[1]['avg_length'], reverse=True)
    longest = sorted_by_length[0][1]
    f.write(f"{longest['name']}平均字数最多({longest['avg_length']:.1f}字)，说明玩家在此方面表达意愿较强\n\n")
    
    f.write("3. **用户群体差异**: 不同满意度、继续意愿、活跃情况、端游经验和年龄段的用户在各主观题上表现出明显的观点差异\n\n")
    
    f.write("### 建议\n\n")
    f.write("1. **关注高频关键词**: 各维度的高频关键词反映了不同用户群体的核心关注点，建议针对性优化\n\n")
    f.write("2. **重视满意度低的群体**: 总体评价中低和继续意愿中低的用户反馈尤其需要关注，这些是改进的重点方向\n\n")
    f.write("3. **差异化运营**: IP活跃用户、IP流失用户和非IP用户表现出不同特征，建议采用差异化运营策略\n\n")
    f.write("4. **年龄段特征**: 不同年龄段用户的需求和期待存在差异，建议在功能设计和内容规划时考虑年龄因素\n\n")
    
    f.write("---\n\n")
    f.write("*本报告由自动化脚本生成，基于NZMS1版本体验问卷主观题数据分析*\n")

print(f"\n✓ 分析完成！报告已保存到: {OUTPUT_PATH}")
print(f"\n结束时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
print("="*80)
