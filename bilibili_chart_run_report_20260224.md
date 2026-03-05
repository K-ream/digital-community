# bilibili_chart 爬虫运行报告
## 执行时间
2026-02-24 11:17:55 - 11:18:09

## 运行状态
✅ **执行成功**

## 爬取数据概览

### 📺 B站番剧 (gc)
成功爬取 **200** 部番剧数据

包括：
1. 凡人修仙传
2. 伍六七之记忆碎片
3. 伍六七之暗影宿命
4. 镇魂街 第五季
5. 灵笼 第二季
6. 仙王的日常生活 第五季
7. 时光代理人 第三季
8. 镇魂街 第四季
9. 伍六七之玄武国篇
10. 时光代理人
... 共200部

## 数据存储位置

### 1️⃣ 腾讯云 COS 对象存储

**原始 JSON 数据：**
- **Bucket**: `mur-ingestion-dev-1255655535`
- **路径**: `user_download/bilibiligc/upload_date=20260224/data.json`
- **文件大小**: 1,542,326 bytes (约 1.5 MB)
- **上传时间**: 2026-02-24 11:18:52
- **完整路径**: `cosn://mur-ingestion-dev-1255655535/user_download/bilibiligc/upload_date=20260224/data.json`

### 2️⃣ 数据湖 (Lake) Parquet 表

**表1: 番剧列表**
- **表名**: `mur_t_stg_kunpeng_bilibiligclist_d_f`
- **记录数**: 200 行
- **字段**: spidertime, nsort, name, chasing, link, info_a, info_b
- **分区**: upload_date=20260224

**表2: 番剧详情**
- **表名**: `mur_t_stg_kunpeng_bilibiligcdetail_d_f`
- **记录数**: 200 行
- **字段**: gc_id, gc_name, gc_tags, gc_playcount, gc_chasingcount, gc_danmucount, gc_starttime, gc_show, gc_desc, gc_longcomment, gc_shortcomment, gc_role, gc_staff, gc_score, gc_sourcepcount, gc_url
- **分区**: upload_date=20260224

## 如何访问数据

### 方法1: Python 代码读取

```python
from mur_data_common import LakeReader
from datetime import datetime

reader = LakeReader()

# 读取番剧列表
df_list = reader.read('mur_t_stg_kunpeng_bilibiligclist_d_f', date=datetime(2026, 2, 24))
print(f'番剧列表: {len(df_list)} 条')

# 读取番剧详情
df_detail = reader.read('mur_t_stg_kunpeng_bilibiligcdetail_d_f', date=datetime(2026, 2, 24))
print(f'番剧详情: {len(df_detail)} 条')
```

### 方法2: 通过 Dremio 查询 (如果已配置)

```sql
-- 查询番剧列表
SELECT * FROM mur_t_stg_kunpeng_bilibiligclist_d_f 
WHERE upload_date = '20260224';

-- 查询番剧详情
SELECT * FROM mur_t_stg_kunpeng_bilibiligcdetail_d_f 
WHERE upload_date = '20260224';
```

### 方法3: 直接从 COS 下载 JSON

```bash
# 配置 coscmd 到 ingestion bucket
coscmd config -a <SecretId> -s <SecretKey> \
  -b mur-ingestion-dev-1255655535 \
  -r ap-guangzhou

# 下载文件
coscmd download user_download/bilibiligc/upload_date=20260224/data.json ./bilibili_gc_data.json
```

## 数据字段说明

### 番剧列表表 (list)
- `spidertime`: 爬取时间 (格式: YYYYMMDDhhmmss)
- `nsort`: 排名
- `name`: 番剧名称
- `chasing`: 追番人数
- `link`: 番剧链接
- `info_a`: 更新信息A
- `info_b`: 标签信息

### 番剧详情表 (detail)
- `gc_id`: 番剧ID (media_id)
- `gc_name`: 番剧名称
- `gc_tags`: 标签列表
- `gc_playcount`: 播放量
- `gc_chasingcount`: 追番人数
- `gc_danmucount`: 弹幕数
- `gc_starttime`: 开播时间
- `gc_show`: 更新信息
- `gc_desc`: 简介
- `gc_role`: 角色信息
- `gc_staff`: 制作人员
- `gc_score`: 评分
- `gc_sourcepcount`: 评分人数
- `gc_url`: 详情链接

## 注意事项

1. **漫画数据**: 本次运行没有爬取漫画数据（mh），因为今天不是周日（脚本设定只在周日爬取漫画）
2. **数据更新**: 表按日期分区，每天生成新的分区数据
3. **权限要求**: 需要有 `mur-ingestion-dev-1255655535` bucket 的读写权限

## 相关文件

- 爬虫脚本: `/root/.openclaw/workspace/webdata-crawling/mur_crawlers/bilibili/bilibili_chart.py`
- COS配置: `~/.cos.conf`
- mur-data-common: `/root/.openclaw/workspace/mur-data-common/`

---
生成时间: 2026-02-24 11:19
