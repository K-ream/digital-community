# mur-data-common 配置完成报告

## ✅ 安装状态

### 已完成项
1. ✅ 克隆 mur-data-common 仓库
   - 路径: `/root/.openclaw/workspace/mur-data-common/`
   - 来源: https://git.woa.com/mur-de/mur-data-common

2. ✅ 安装 pip
   - 版本: pip 23.3.1
   - 路径: `/root/.local/bin/pip3`

3. ✅ 安装所有依赖包
   已安装的包括:
   - pandas (3.0.1)
   - numpy (2.4.2)
   - pyarrow (23.0.1)
   - beautifulsoup4 (4.14.3)
   - requests-toolbelt
   - cos_python_sdk_v5
   - coscmd
   - tencentcloud_sdk_python
   - tdwTauthAuthentication
   - 以及其他所有 requirements.txt 中的依赖

4. ✅ 添加环境变量
   - 已将 `/root/.local/bin` 添加到 PATH
   - 已写入 ~/.bashrc

## ⚠️ 待配置项

### 需要腾讯云 Key 配置

`mur-data-common` 需要腾讯云的 COS（对象存储）配置才能运行。

**配置方式有两种：**

### 方法1: 使用 coscmd 配置（推荐）

```bash
# 安装 coscmd（已完成）
pip install coscmd -U

# 配置腾讯云 key
coscmd config -a <你的SecretId> -s <你的SecretKey> \
  -b mur-personal-data-1255655535 \
  -r ap-guangzhou
```

配置文件会保存在: `~/.cos.conf`

### 方法2: 设置环境变量

```bash
export TENCENTCLOUD_RUNENV=SCF
export TENCENTCLOUD_REGION=ap-guangzhou
export TENCENTCLOUD_SECRETID=<你的SecretId>
export TENCENTCLOUD_SECRETKEY=<你的SecretKey>
```

## 📋 获取腾讯云 Key

你需要联系以下人员获取腾讯云 key:
- 用研数据平台管理员
- xingxpan (项目所有者)
- mur-de 团队成员

## 🧪 测试导入

配置完成后，可以测试导入:

```python
from mur_data_common import LakeReader, LakeWriter
from datetime import datetime
import pandas as pd

reader = LakeReader()
writer = LakeWriter()

# 测试读取数据
# df = reader.load_dremio_table("space.folder.table")

# 测试写入数据
# df = pd.DataFrame({'a': [1,2,3], 'b': [4,5,6]})
# writer.write(df, "test_table", datetime.now())
```

## 📦 已安装的组件

- ✅ mur-data-common (本地开发模式)
- ✅ cosfs (COS 文件系统)
- ✅ coscmd (COS 命令行工具)
- ✅ cos_python_sdk_v5 (COS Python SDK)
- ✅ pandas, numpy, pyarrow (数据处理)
- ✅ beautifulsoup4, lxml (网页解析)
- ✅ tdwTauthAuthentication (TDW 认证)

## 🔗 相关文档

- COS CLI 配置: https://cloud.tencent.com/document/product/436/63144
- mur-data-common README: /root/.openclaw/workspace/mur-data-common/README.md
- 工蜂项目: https://git.woa.com/mur-de/mur-data-common

## 下一步

1. 联系管理员获取腾讯云 SecretId 和 SecretKey
2. 使用 coscmd 配置腾讯云 key
3. 测试 mur-data-common 导入和基本功能
4. 在 webdata-crawling 项目中运行爬虫脚本
