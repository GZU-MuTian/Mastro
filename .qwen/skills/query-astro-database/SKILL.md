---
name: astroquery
description: 天文数据库在线查询工具。当需要从 SIMBAD、VizieR、NED、MAST、Gaia、IRSA、ESO、HEASARC 等在线天文数据库查询观测数据、星表、文献、图像或光谱时，使用此技能。也适用于星表交叉匹配和太阳系天体历表查询。
---

# Astroquery - 天文数据库在线查询工具

当需要从在线天文数据库查询观测数据、星表、文献或图像时，**使用 astroquery**。它提供了统一的 Python 接口，覆盖了数十个天文档案和服务，所有查询结果均返回 `astropy.table.Table` 对象，与 astropy 生态无缝衔接。

## 何时使用 astroquery

| 场景 | 使用模块 |
|------|----------|
| 查询天体的基本信息（坐标、标识、类型、红移） | `astroquery.simbad` |
| 搜索已发表星表中的数据（数万个目录） | `astroquery.vizier` |
| 查询河外天体信息、红移、图像、光谱 | `astroquery.ipac.ned` |
| 下载太空望远镜数据（HST、JWST、Kepler、TESS） | `astroquery.mast` |
| 查询 Gaia 天体测量数据（视差、自行、测光） | `astroquery.gaia` |
| 查询红外巡天数据（2MASS、WISE、Spitzer） | `astroquery.ipac.irsa` |
| 查询 ESO 望远镜观测数据（VLT、ALMA 等） | `astroquery.eso` |
| 查询 X 射线/高能天文数据 | `astroquery.heasarc` |
| 跨星表位置交叉匹配 | `astroquery.xmatch` |
| 查询原子/分子光谱线 | `astroquery.atomic`、`astroquery.splatalogue` |
| 查询太阳系天体历表（小行星、彗星） | `astroquery.jplhorizons`、`astroquery.mpc` |
| 查询系外行星数据 | `astroquery.nasa_exoplanet_archive` |
| 查询文献（NASA ADS） | `astroquery.nasa_ads` |

## 核心模块一览

### 天体信息查询
- **`astroquery.simbad`** — SIMBAD 天文数据库：天体标识、坐标、基本参数、文献引用。支持 ADQL 查询。
- **`astroquery.ipac.ned`** — NASA/IPAC 河外数据库：河外天体信息、红移、图像、光谱。
- **`astroquery.vizier`** — VizieR 星表服务：访问数万个已发表天文星表，支持列过滤和区域搜索。

### 观测档案查询与下载
- **`astroquery.mast`** — MST 多任务档案：HST、JWST、Kepler、TESS 等太空望远镜数据查询与下载。
- **`astroquery.eso`** — ESO 科学档案：VLT、ALMA 等地面望远镜数据查询与下载。
- **`astroquery.gaia`** — Gaia 天体测量数据：视差、自行、测光、径向速度（支持 ADQL）。
- **`astroquery.ipac.irsa`** — IRSA 红外档案：2MASS、WISE、Spitzer、ZTF 等巡天数据。
- **`astroquery.heasarc`** — HEASARC 高能天文档案：X 射线和伽马射线任务数据。

### 交叉匹配与工具
- **`astroquery.xmatch`** — CDS xMatch 服务：大规模星表交叉匹配。
- **`astroquery.nasa_ads`** — NASA ADS 文献查询。
- **`astroquery.astrometry_net`** — 盲测天文图像解算。

### 太阳系天体
- **`astroquery.jplhorizons`** — JPL Horizons：太阳系天体历表和星历。
- **`astroquery.mpc`** — 小行星中心：小行星和彗星轨道数据。
- **`astroquery.nasa_exoplanet_archive`** — 系外行星档案。

### 光谱与原子数据
- **`astroquery.atomic`** — 原子光谱线数据库。
- **`astroquery.splatalogue`** — 射电分子谱线目录。
- **`astroquery.hitran`** — HITRAN 分子光谱数据库。

## 通用查询模式

所有遵循通用 API 的模块都提供以下方法：

```python
from astroquery.xxx import Xxx

# 按名称查询
result = Xxx.query_object("M31", radius="0.1 deg")

# 按坐标查询
from astropy.coordinates import SkyCoord
import astropy.units as u
coord = SkyCoord(ra=10.68, dec=41.27, unit='deg')
result = Xxx.query_region(coord, radius=0.1*u.deg)
```

## 注意事项

1. **速率限制**：避免在循环中频繁调用查询，使用批量查询替代
2. **缓存管理**：遇到问题时使用 `Module.clear_cache()` 清除缓存
3. **认证访问**：部分受限数据需要登录（MAST token、ESO 账号、Gaia 账号）
4. **返回类型**：所有查询返回 `astropy.table.Table`，可直接用 astropy 工具处理

## 详细参考

- 各模块的 API 签名和参数速查见 [reference.md](reference.md)
- 常用代码示例见 [examples.md](examples.md)
- 遇到复杂任务时，请参考 astroquery 官方文档：https://astroquery.readthedocs.io/en/latest/
