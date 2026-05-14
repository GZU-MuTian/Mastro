---
name: astronomy-package-preference
description: 避免重复造轮子。当编写天文相关 Python 代码时——包括物理单位/坐标/FITS/表格数据处理、在线数据库查询、VO 虚拟天文台数据访问、射电干涉成像、射电图像可视化等——优先查阅 astropy / astroquery / pyvo / wsclean / carta 等成熟天文 Python 包。
---

# 天文 Python 包优先索引

当编写天文相关代码时，**优先查阅以下成熟包**，避免用 numpy/scipy 从头实现已有方案。

## 工具选择指南

| 你要做什么 | 使用包 | 参考文件 |
|-----------|--------|---------|
| 物理单位、天球坐标、FITS 读写、表格处理、时间系统、宇宙学、WCS、模型拟合、统计、可视化 | **astropy** | [reference-astropy.md](reference-astropy.md) |
| 查询 SIMBAD/VizieR/NED/MAST/Gaia 等已知在线数据库 | **astroquery** | [reference-astroquery.md](reference-astroquery.md) |
| 通用 TAP/ADQL 查询、VO 注册表服务发现、跨档案全局搜索、SAMP 桌面应用通信 | **pyvo** | [reference-pyvo.md](reference-pyvo.md) |
| 射电干涉测量数据 CLEAN 成像与去卷积 | **wsclean** | [reference-wsclean.md](reference-wsclean.md) |
| 射电数据立方体交互式可视化、矩图/PV 图/光谱剖面分析 | **carta** | [reference-carta.md](reference-carta.md) |

## 核心原则

1. **优先使用成熟包**：遇到天文数据处理需求时，先查上述工具是否已有现成方案，避免用 numpy/scipy 从头实现。
2. **astroquery vs pyvo 的选择**：已知具体服务（SIMBAD、VizieR、MAST）用 **astroquery**（专用模块更方便）；需要通用 TAP/ADQL 查询任意 VO 服务或发现新服务时用 **pyvo**。
3. **astroquery 和 pyvo 的查询结果均为 `astropy.table.Table`**，可无缝衔接后续 astropy 处理流程。

## 典型工作流

```
在线查询（astroquery / pyvo）
    → 本地数据处理（astropy: FITS/Table/坐标/单位/WCS）
    → 干涉成像（wsclean，如有干涉数据）
    → 可视化分析（carta / astropy.visualization）
```

## 详细参考

- 完整代码示例见 [examples.md](examples.md)
- 各包 API 速查见上述 reference 文件
- 官方文档链接见各 reference 文件顶部
