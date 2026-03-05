#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
NZMS1版本体验问卷主观题分析
"""

import pandas as pd
import numpy as np
from collections import Counter
import re
import json

# 文件路径
FILE_PATH = '/root/.openclaw/workspace/webdata-crawling/问卷清洗交付/NZMS1版本体验问卷清洗/NZMS1版本体验问卷清洗_统计信息.xlsx'
OUTPUT_PATH = '/root/.openclaw/workspace/NZMS1_主观题分析报告.md'

# 主观题字段映射
SUBJECTIVE_QUESTIONS = {
    'q3t31': '了解渠道',
    'q6t15': '满意的地方',
    'q7t20': '不满意的地方',
    'q11t9': '天赋系统不满意',
    'q13t18': '继续游玩吸引点',
    'q14t13': '未来期待',
    'q15t': '意见建议'
}

# 分析维度字段（需要根据实际数据调整）
DIMENSION_FIELDS = {
    '总体满意度': ['总体评价', 'q5', 'satisfaction'],  # 可能的字段名
    '继续意愿': ['继续意愿', 'q12', 'continue'],
    '活跃情况': ['活跃情况', 'active_type', '用户类型'],
    '端游经验': ['端游经验', 'IP用户', 'ip_type'],
    '年龄': ['年龄', 'age', 'q1']
}

print("开始读取数据...")
# 读取主观题sheet
df = pd.read_excel(FILE_PATH, sheet_name='主观题')
print(f"✓ 数据读取完成，形状: {df.shape}")
print(f"✓ 共 {len(df)} 条记录，{len(df.columns)} 个字段")

# 输出前几列名称以便调试
print(f"\n前30个列名:")
for i, col in enumerate(df.columns[:30]):
    print(f"  {i}: {col}")

# 保存列名到文件以便检查
with open('/root/.openclaw/workspace/columns_list.txt', 'w', encoding='utf-8') as f:
    for i, col in enumerate(df.columns):
        f.write(f"{i}: {col}\n")
print(f"\n✓ 完整列名已保存到: /root/.openclaw/workspace/columns_list.txt")

# 识别主观题字段
found_questions = {}
for q_code, q_name in SUBJECTIVE_QUESTIONS.items():
    # 尝试精确匹配
    if q_code in df.columns:
        found_questions[q_code] = q_name
        print(f"✓ 找到主观题: {q_code} ({q_name})")
    else:
        # 尝试模糊匹配
        matching_cols = [col for col in df.columns if q_code in str(col).lower()]
        if matching_cols:
            found_questions[matching_cols[0]] = q_name
            print(f"✓ 找到主观题: {matching_cols[0]} ({q_name})")
        else:
            print(f"✗ 未找到主观题: {q_code} ({q_name})")

print(f"\n找到 {len(found_questions)}/{len(SUBJECTIVE_QUESTIONS)} 个主观题")

# 识别维度字段
dimension_cols = {}
print(f"\n识别分析维度字段:")
for dim_name, possible_names in DIMENSION_FIELDS.items():
    found = False
    for possible_name in possible_names:
        matching_cols = [col for col in df.columns if possible_name.lower() in str(col).lower()]
        if matching_cols:
            dimension_cols[dim_name] = matching_cols[0]
            print(f"✓ {dim_name}: {matching_cols[0]}")
            found = True
            break
    if not found:
        print(f"✗ {dim_name}: 未找到")

print("\n" + "="*60)
print("第一阶段完成：数据探索")
print("="*60)
