---
name: pyvo
description: 天文虚拟天文台 (VO) 数据访问。当需要通过 TAP/ADQL 查询任意 VO 服务、搜索 VO 注册表发现服务、跨多个档案全局搜索图像/光谱、与 TOPCAT/Aladin 等桌面应用通信 (SAMP)、或处理 VOTable 数据模型注解 (MIVOT) 时，使用此技能。
---

# PyVO - 虚拟天文台 (VO) 数据访问

当需要通过 **IVOA 标准协议** 访问天文数据、查询 VO 注册表发现服务、或与其他天文桌面应用通信时，**使用 PyVO**。它是访问 VO 生态系统的 Python 原生接口，适用于跨档案统一查询和服务发现场景。

## 何时使用 PyVO vs astroquery

| 场景 | 推荐工具 |
|------|----------|
| 查询特定已知服务（SIMBAD、VizieR、MAST 等） | **astroquery**（专用模块更方便） |
| 需要通过 TAP/ADQL 查询任意 VO 服务 | **PyVO**（通用 TAP 客户端） |
| 发现和搜索 VO 注册表中的服务 | **PyVO**（registry 模块） |
| 跨多个档案全局搜索图像/光谱 | **PyVO**（discover 模块） |
| 与 TOPCAT、Aladin 等桌面应用通信 | **PyVO**（SAMP 模块） |
| 处理 VOTable 中的数据模型注解 | **PyVO**（MIVOT 模块） |
| 查询特定任务数据并下载 | **astroquery**（有专用下载接口） |

**原则**：已知服务用 astroquery，通用 VO 协议/服务发现用 PyVO。

## 核心模块一览

### 数据访问 (pyvo.dal)

| 协议 | 类 | 用途 | 搜索形状 |
|------|-----|------|---------|
| **TAP** | `TAPService` | 通过 ADQL 查询天文数据源目录和观测数据 | ADQL 定义 |
| **SIA** | `SIAService` | 在数据档案中搜索和获取图像数据（SIAv1/v2） | 矩形 (`pos`, `size`) |
| **SSA** | `SSAService` | 在数据档案中搜索和获取光谱数据 | 圆形 (`pos`, `diameter`) |
| **SCS** | `SCSService` | 基于位置的锥形搜索（源目录/观测日志） | 圆形 (`pos`, `radius`) |
| **SLAP** | `SLAService` | 查询谱线数据（静止频率等） | 仅波长 (`wavelength`) |

**TAP 支持同步和异步查询**：`search()` 为同步，`run_async()` 为一步异步，`submit_job()` 为分步异步作业控制（PENDING→QUEUED→EXECUTING→COMPLETED）。

**SIA 支持空间覆盖关系过滤**：`intersect` 参数可选 `COVERS`（覆盖搜索区）、`ENCLOSED`（被搜索区包含）、`OVERLAPS`（重叠，默认）、`CENTER`（中心在区内）。

**SSA vs SIA**：SSA 搜索圆形区域（`diameter`），支持 `band`（波段）和 `time`（时间）约束；SIA 搜索矩形区域（`size`），无波段/时间约束。

### 注册表 (pyvo.registry)

| 能力 | 说明 |
|------|------|
| 服务发现 | 按服务类型（TAP/SIA/SSA/SCS）查找所有可用服务 |
| 数据发现 | 按关键词、波段、UCD、数据模型等条件搜索资源 |
| 空间搜索 | 按天区覆盖范围过滤资源 |
| 服务获取 | 从搜索结果直接获取可查询的服务对象 |

### 全局发现 (pyvo.discover)

| 功能 | 说明 |
|------|------|
| `images_globally()` | 跨多个档案全局搜索图像数据集 |
| 约束条件 | 支持空间、光谱、时间约束 |
| 去重合并 | 自动过滤重复服务和重复结果 |

### SAMP 通信 (pyvo.samp)

| 功能 | 说明 |
|------|------|
| 表格发送 | 将 `astropy.table.Table` 发送到 TOPCAT 等应用 |
| 图像/光谱发送 | 将图像或光谱 URL 发送到 Aladin 等应用 |
| 客户端管理 | 查找已连接的天文应用客户端 |

### MIVOT 注解 (pyvo.mivot)

| 功能 | 说明 |
|------|------|
| 注解查看 | 读取和解析 VOTable 中的 MIVOT 数据模型注解 |
| 注解写入 | 创建或修改 VOTable 中的 MIVOT 注解块 |

> **注意**：MIVOT 和部分 DAL 功能（如表操作）为原型特性，需调用 `activate_features("MIVOT")` 激活。

### 结果集通用接口

所有 DAL 服务的 `search()` 返回相同接口的结果集：

| 方法/属性 | 说明 |
|-----------|------|
| `result.fieldnames` | 列名元组 |
| `result.to_table()` / `result.to_qtable()` | 转为 `astropy.table.Table` / `QTable` |
| `result.fieldname_with_ucd('phot.mag')` | 按 UCD 查找列名 |
| `result.fieldname_with_utype('obscore:...')` | 按 utype 查找列名 |
| `result['col']` / `result[0]` / `result['col', 0]` | 整列/单行/单值 |
| `result.votable` | 底层 VOTableFile |

### 天文参数约定

所有 DAL 服务的位置/区域参数统一接受 Astropy 类型：

```python
SkyCoord.from_name('NGC 4993')   # 名称解析
SkyCoord(ra=257.41, dec=64.3, unit='deg')  # 坐标
(257.41, 64.3)                   # (ra, dec) 度数元组
0.5 * u.deg                      # Quantity 角度
Time((53000, 54000), format='mjd')  # 时间范围
```

### 认证 (pyvo.auth)

| 类 | 用途 |
|----|------|
| `AuthSession` | 支持身份验证的请求会话 |
| `CredentialStore` | 管理凭据并创建认证会话 |

### 异常类

| 异常 | 说明 |
|------|------|
| `DALQueryError` | ADQL 查询语法或语义错误 |
| `DALServiceError` | 服务通信失败 |
| `DALFormatError` | 响应格式错误 |
| `DALOverflowWarning` | 结果被截断（`e.result` 仍可访问部分结果） |
| `DALRateLimitError` | HTTP 429 限速 |

### 辅助函数

顶级快捷函数，无需手动创建服务对象：

| 函数 | 等价于 |
|------|--------|
| `pyvo.dal.imagesearch(url, pos, size)` | `SIAService(url).search(pos, size)` |
| `pyvo.dal.spectrumsearch(url, pos, diameter)` | `SSAService(url).search(pos, diameter)` |
| `pyvo.dal.conesearch(url, pos, radius)` | `SCSService(url).search(pos, radius)` |
| `pyvo.dal.tablesearch(url, query)` | `TAPService(url).search(query)` |
| `pyvo.dal.linesearch(url, wavelength)` | `SLAService(url).search(wavelength)` |

## 通用查询模式

```python
import pyvo as vo

# 1. 直接使用已知服务 URL
tap = vo.dal.TAPService("https://some.archive.org/tap")
result = tap.search("SELECT TOP 10 * FROM ivoa.obscore")

# 2. 通过注册表发现服务后查询
for svc in vo.registry.search(waveband="X-ray", servicetype="tap"):
    result = svc.service.run_sync("SELECT TOP 5 * FROM ivoa.obscore")

# 3. 全局数据集发现
datasets, log = vo.discover.images_globally(
    space=(273.5, -12.1, 0.1), spectrum=1e-10)
```

## 详细参考

- 各模块的 API 签名和参数速查见 [reference.md](reference.md)
- 常用代码示例见 [examples.md](examples.md)
- 遇到复杂任务时，请参考 PyVO 官方文档：https://pyvo.readthedocs.io/en/latest/
