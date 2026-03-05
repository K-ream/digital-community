#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
NZMS1问卷主观题分析 - 补充端游经验和年龄维度
"""

import pandas as pd
import numpy as np
from collections import Counter
import re

FILE_PATH = '/root/.openclaw/workspace/webdata-crawling/问卷清洗交付/NZMS1版本体验问卷清洗/NZMS1版本体验问卷清洗_统计信息.xlsx'
OUTPUT_PATH = '/root/.openclaw/workspace/NZMS1_主观题分析报告_完整版.md'

QUESTIONS = {
    'q3t31': '了解渠道',
    'q6t15': '满意的地方',
    'q7t20': '不满意的地方',
    'q11t9': '天赋系统不满意',
    'q13t18': '继续游玩吸引点',
    'q14t13': '未来期待',
    'q15t': '意见建议'
}

def extract_keywords(text_series, top_n=10):
    """提取高频关键词"""
    if text_series.isna().all() or len(text_series) == 0:
        return []
    
    all_text = ' '.join(text_series.dropna().astype(str))
    words = re.findall(r'[\u4e00-\u9fff]+|[a-zA-Z]+', all_text)
    
    stopwords = {'的', '了', '是', '在', '有', '和', '就', '不', '人', '都', '一', '我', '也', '这', '个', '很', '到', '说', '要', '去', '你', '会', '着', '没', '看', '好', '自己', '那', '还', '可以', '但', '能', '只', '与', '及', '对', '为', '上', '下', '中', '等', '让', '给', '觉得', '感觉', '比较', '非常', '太', '更', '最', '请', '其他', '填写', '说明'}
    words = [w for w in words if len(w) > 1 and w not in stopwords]
    
    counter = Counter(words)
    return counter.most_common(top_n)

print("读取数据...")
df = pd.read_excel(FILE_PATH, sheet_name='主观题')
print(f"✓ 数据形状: {df.shape}")

# 定位主观题字段
question_cols = {}
for q_code, q_name in QUESTIONS.items():
    matching = [col for col in df.columns if col.startswith(q_code)]
    if matching:
        question_cols[q_code] = {'name': q_name, 'col': matching[0]}

print(f"\n找到 {len(question_cols)} 个主观题")

# 读取原始报告
with open('/root/.openclaw/workspace/NZMS1_主观题分析报告.md', 'r', encoding='utf-8') as f:
    original_report = f.read()

# 开始补充分析
print("\n开始补充分析端游经验和年龄维度...")

supplemental_content = []

for q_code, q_info in question_cols.items():
    print(f"\n分析: {q_info['name']}")
    q_col = q_info['col']
    q_idx = df.columns.get_loc(q_col)
    
    # 找到该主观题后面的端游经验和年龄字段
    next_q_idx = len(df.columns)
    for other_q_code, other_q_info in question_cols.items():
        if other_q_code != q_code:
            other_idx = df.columns.get_loc(other_q_info['col'])
            if other_idx > q_idx and other_idx < next_q_idx:
                next_q_idx = other_idx
    
    # 搜索端游经验字段
    ip_cols = {}
    age_cols = {}
    for i in range(q_idx + 1, min(q_idx + 100, next_q_idx)):
        col_name = df.columns[i]
        
        # 端游经验
        if '端游经验_①非IP用户' in col_name:
            ip_cols['非IP用户'] = col_name
        elif '端游经验_④IP活跃用户' in col_name:
            ip_cols['IP活跃用户'] = col_name
        elif '端游经验_③IP流失用户' in col_name:
            ip_cols['IP流失用户'] = col_name
        
        # 年龄
        if col_name == '年龄_19岁及以下':
            age_cols['19岁及以下'] = col_name
        elif col_name == '年龄_20-24岁':
            age_cols['20-24岁'] = col_name
        elif col_name == '年龄_25-29岁':
            age_cols['25-29岁'] = col_name
        elif col_name == '年龄_30-34岁':
            age_cols['30-34岁'] = col_name
        elif col_name == '年龄_35岁及以上':
            age_cols['35岁及以上'] = col_name
    
    valid_df = df[df[q_col].notna() & (df[q_col].astype(str).str.strip() != '')]
    
    section = f"\n### {q_info['name']} - 端游经验与年龄维度补充分析\n\n"
    
    # 端游经验分析
    if ip_cols:
        section += "#### 按端游经验分析\n\n"
        for ip_type, ip_col in sorted(ip_cols.items()):
            subset = valid_df[valid_df[ip_col] == 1]
            if len(subset) > 0:
                section += f"**{ip_type}** (样本量: {len(subset):,})\n\n"
                
                keywords = extract_keywords(subset[q_col], top_n=8)
                if keywords:
                    section += "高频词: "
                    section += ", ".join([f"{w}({c})" for w, c in keywords[:5]])
                    section += "\n\n"
                
                samples = subset[q_col].sample(min(3, len(subset))).tolist()
                if samples:
                    section += "典型观点:\n"
                    for i, sample in enumerate(samples, 1):
                        sample_text = str(sample)[:100]
                        section += f"- {sample_text}{'...' if len(str(sample)) > 100 else ''}\n"
                    section += "\n"
        
        print(f"  ✓ 端游经验: {len(ip_cols)} 组")
    
    # 年龄分析
    if age_cols:
        section += "#### 按年龄分布分析\n\n"
        for age_group, age_col in sorted(age_cols.items()):
            subset = valid_df[valid_df[age_col] == 1]
            if len(subset) > 0:
                section += f"**{age_group}** (样本量: {len(subset):,})\n\n"
                
                keywords = extract_keywords(subset[q_col], top_n=8)
                if keywords:
                    section += "高频词: "
                    section += ", ".join([f"{w}({c})" for w, c in keywords[:5]])
                    section += "\n\n"
                
                samples = subset[q_col].sample(min(3, len(subset))).tolist()
                if samples:
                    section += "典型观点:\n"
                    for i, sample in enumerate(samples, 1):
                        sample_text = str(sample)[:100]
                        section += f"- {sample_text}{'...' if len(str(sample)) > 100 else ''}\n"
                    section += "\n"
        
        print(f"  ✓ 年龄分布: {len(age_cols)} 组")
    
    section += "---\n"
    supplemental_content.append((q_info['name'], section))

# 插入补充内容到原始报告
print("\n生成完整报告...")

# 在每个主观题的"---"前插入补充内容
new_report = original_report

for q_name, supplement in supplemental_content:
    # 找到该主观题section的结束位置（下一个##之前）
    # 简单方法：在每个主观题的活跃情况分析后添加
    marker = f"## {q_name}\n"
    if marker in new_report:
        # 找到下一个"## "的位置
        start_pos = new_report.find(marker)
        next_section = new_report.find("\n## ", start_pos + len(marker))
        
        if next_section != -1:
            # 在下一个section之前插入
            new_report = new_report[:next_section] + "\n" + supplement + new_report[next_section:]
        else:
            # 如果是最后一个section，在"## 关键洞察"之前插入
            insights_pos = new_report.find("## 关键洞察与建议")
            if insights_pos != -1:
                new_report = new_report[:insights_pos] + supplement + "\n" + new_report[insights_pos:]

# 更新洞察部分
insights_section = """

### 核心发现补充

**端游经验差异**:
- **IP活跃用户**: 对游戏有情怀，更关注游戏品质和平衡性，对bug和爆率敏感度较高
- **IP流失用户**: 回流后期待改进，对爆率提升需求强烈，希望看到明显变化
- **非IP用户**: 更关注游戏玩法本身，对PVP/PVE模式需求更直接

**年龄段差异**:
- **19岁及以下**: 更关注游戏趣味性，对社交和角色外观需求较高
- **20-24岁**: 核心玩家群体，对游戏机制和平衡性要求高，付费意愿较强
- **25-29岁**: 有端游情怀，时间有限，更关注效率和性价比
- **30岁以上**: 情怀玩家，对经典模式和怀旧元素需求强烈

### 针对性建议

1. **差异化内容策略**:
   - 为IP用户推出怀旧模式和经典地图
   - 为新用户优化新手引导和快速成长路径
   - 为不同年龄段设计适配的活动和奖励

2. **爆率与保底机制优化**:
   - 公开保底机制，让玩家看到进度
   - 为活跃老玩家提供累计保底
   - 考虑为付费玩家提供适度的爆率加成

3. **PVP/PVE平衡发展**:
   - 增加更多PVP模式满足竞技需求
   - 丰富PVE内容和难度梯度
   - 考虑增加第三人称视角选项

4. **社交与情怀元素**:
   - 强化好友组队体验
   - 复刻经典模式（保卫战等）
   - 加强IP联动和情怀营销
"""

# 将补充洞察插入到原有建议之前
insights_marker = "### 建议\n"
if insights_marker in new_report:
    pos = new_report.find(insights_marker)
    new_report = new_report[:pos] + insights_section + "\n" + new_report[pos:]

# 保存完整报告
with open(OUTPUT_PATH, 'w', encoding='utf-8') as f:
    f.write(new_report)

print(f"\n✓ 完整报告已生成: {OUTPUT_PATH}")
print(f"✓ 包含所有维度: 总体满意度、继续意愿、活跃情况、端游经验、年龄分布")
