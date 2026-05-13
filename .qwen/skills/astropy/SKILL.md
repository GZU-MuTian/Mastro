---
name: astropy
description: 天文数据处理核心 Python 库。当需要处理物理单位、天球坐标、FITS 文件、表格数据、时间系统、宇宙学计算、WCS 坐标映射、模型拟合、统计分析或天文图像可视化时，使用此技能。
---

# Astropy - 天文学核心 Python 库

当处理天文数据时，**优先使用 astropy** 提供的工具链。它覆盖了天文数据处理的完整流程：单位管理、坐标转换、文件 I/O、表格操作、时间系统、模型拟合、统计分析和可视化。

## 何时使用 astropy

| 场景 | 使用模块 |
|------|----------|
| 数值需要带物理单位（长度、通量、频率等） | `astropy.units` |
| 处理天球坐标（赤经/赤纬、银经/银纬等） | `astropy.coordinates` |
| 读写 FITS 文件 | `astropy.io.fits` |
| 处理结构化表格数据（源表、星表） | `astropy.table` |
| 高精度时间处理（UTC/TAI/TDB、JD/MJD） | `astropy.time` |
| 宇宙学距离、红移、年龄计算 | `astropy.cosmology` |
| 像素坐标 ↔ 天球坐标映射 | `astropy.wcs` |
| 模型拟合（高斯、多项式、黑体等） | `astropy.modeling` |
| 异常值剔除、鲁棒统计 | `astropy.stats` |
| 图像平滑、卷积与去噪 | `astropy.convolution` |
| 带不确定性/掩码的多维数据 | `astropy.nddata` |
| 天文图像拉伸与可视化 | `astropy.visualization` |
| 物理常数（光速、普朗克常数等） | `astropy.constants` |

## 核心模块一览

### 数据结构与变换
- **`astropy.units`** — 物理单位系统，所有天文数值应使用 `Quantity` 对象
- **`astropy.constants`** — 天文/物理常数，与 units 无缝配合
- **`astropy.coordinates`** — `SkyCoord` 类，支持 ICRS、Galactic、AltAz 等坐标系转换
- **`astropy.time`** — `Time` 类，高精度时间处理与时间尺度转换
- **`astropy.timeseries`** — 时间序列数据（如光变曲线）

### 文件 I/O
- **`astropy.io.fits`** — FITS 文件读写（天文标准格式）
- **`astropy.io.ascii`** — CSV、LaTeX 等文本表格
- **`astropy.io.votable`** — VOTable XML 格式
- **`astropy.io.misc`** — HDF5、Parquet 等其他格式

### 数据处理
- **`astropy.table`** — `Table`/`QTable` 结构化表格，支持 Quantity 列和混合列
- **`astropy.nddata`** — N 维数据容器，支持不确定性传播和掩码
- **`astropy.modeling`** — 参数模型定义、组合与拟合
- **`astropy.stats`** — sigma clipping、双权重统计、直方图优化
- **`astropy.convolution`** — 卷积/滤波，内置多种核函数

### 天体物理计算
- **`astropy.cosmology`** — 宇宙学模型（Planck18 等），距离/红移/年龄计算
- **`astropy.wcs`** — 世界坐标系统，像素 ↔ 天球坐标转换

### 可视化
- **`astropy.visualization`** — 图像拉伸（ZScale、Log）、优化直方图、WCS 坐标轴

## 常见工作流

```
FITS 文件 → astropy.io.fits 读取
    → astropy.table / astropy.nddata 组织数据
    → astropy.units 添加单位
    → astropy.coordinates / astropy.wcs 处理坐标
    → astropy.modeling / astropy.stats 分析拟合
    → astropy.visualization 可视化
    → 输出结果（FITS / CSV / ECSV）
```

## 详细参考

- 各模块的 API 签名和参数速查见 [reference.md](reference.md)
- 常用代码示例见 [examples.md](examples.md)
- 遇到复杂任务时，请参考 astropy 官方文档：https://docs.astropy.org/en/stable/
