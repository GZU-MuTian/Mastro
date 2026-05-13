---
name: carta
description: 射电天文图像可视化与分析工具。当需要可视化 FITS/CASA/HDF5 图像、交互式浏览数据立方体、提取空间/光谱剖面、生成矩图、创建 PV 图、进行区域统计、偏振分析或远程操控 CARTA 前端时，使用此技能。
---

# CARTA - 射电天文图像可视化与分析

[CARTA](https://carta.readthedocs.io/en/latest/)（Cube Analysis and Rendering Tool for Astronomy）是一款面向射电天文的开源图像可视化与分析工具，专为 GB–TB 级数据立方体设计。采用客户端-服务器架构，前端通过 WebGL2 进行 GPU 加速渲染，后端处理数据 I/O。

## 何时使用 CARTA

- 可视化 FITS / CASA / HDF5 图像和数据立方体
- 交互式浏览多通道、多偏振数据
- 提取空间剖面（线、折线）和光谱剖面
- 生成矩图（moment map）和位置-速度（PV）图
- 区域统计、直方图、图像拟合
- 偏振（Stokes）分析与矢量场叠加
- 星表叠加、SIMBAD/VizieR 在线查询
- 通过 Python 脚本远程控制 CARTA 前端

## 功能模块

### 1. 数据格式

| 类别 | 支持格式 |
|------|----------|
| 图像 | FITS, CASA image, HDF5 (IDIA 模式), PV 图, LEL 表达式, 复数值图像 |
| 目录 | VOTable, CSV, TSV, FITS 表 |
| 区域 | CASA (.crtf), DS9 (.reg), CARTA |

### 2. 可视化渲染

- **栅格渲染**：多种颜色映射表、缩放函数、偏压/对比度调节
- **等值线渲染**：多层等值线叠加
- **矢量场**：偏振方向与强度可视化
- **多色混合**：多图像 RGB 合成
- **通道图网格**：同时显示立方体多个通道
- **动画**：通道/偏振分量切换动画

### 3. 分析工具

- **统计**：选定区域的像素统计（均值、标准差、通量密度）
- **直方图**：交互式像素值分布
- **空间剖面器**：沿点、线、折线路径提取剖面
- **光谱剖面器**：单点或区域平均光谱，支持拟合
- **矩图生成器**：0 阶、1 阶、2 阶矩图
- **PV 图生成器**：从 3D 立方体提取位置-速度图
- **图像拟合**：2D 高斯等模型拟合
- **Stokes 分析**：偏振诊断图

### 4. 区域与标注

- 区域类型：圆、椭圆、矩形、多边形、点、线、折线
- 区域可在多图像间共享（保持角大小或像素长度）
- 导入/导出：CASA (.crtf)、DS9 (.reg)
- 标注：文本、线段、箭头

### 5. 在线数据查询

| 服务 | 功能 |
|------|------|
| SIMBAD | 天体标识与基本参数查询 |
| VizieR | 星表查询与叠加 |
| HiPS2FITS | HiPS 图像查询与加载 |
| Splatalogue | 谱线数据库查询与叠加 |

### 6. 图像匹配

- **空间匹配**：不同 WCS 的图像自动对齐
- **光谱匹配**：不同频率轴的图像同步
- **渲染匹配**：颜色映射、缩放函数同步

### 7. 工作区管理

- 布局保存/恢复
- 工作区持久化（图像、区域、布局）
- 会话断开后恢复

### 8. 部署模式

| 模式 | 说明 |
|------|------|
| 站点部署 | 机构级中央服务器，多用户访问 |
| 用户部署 | 本地或远程服务器，浏览器访问 |

## carta-python — Python 脚本接口

`carta-python` 通过 HTTP 接口控制 CARTA 前端，实现脚本化操作。

> **注意**：API 处于实验阶段，尚未发布到 PyPI，需从 [GitHub](https://github.com/CARTAvis/carta-python) 安装。需要 Python ≥ 3.10。

### 核心类

| 类 | 说明 |
|----|------|
| `Session` | 管理与 CARTA 前端的连接 |
| `Image` | 代表前端打开的图像 |
| `Region` | 代表图像上的区域 |

### 详细参考

- [API 签名与参数](reference.md)
- [代码示例](examples.md)

## 相关资源

- 官方文档：<https://carta.readthedocs.io/en/latest/>
- carta-python：<https://github.com/CARTAvis/carta-python>
- carta-python 文档：<https://carta-python.readthedocs.io/en/latest/>
