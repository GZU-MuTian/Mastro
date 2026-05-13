---
name: wsclean
description: 射电干涉数据成像与去卷积工具。当需要对射电干涉测量数据进行 CLEAN 成像、多尺度去卷积、宽带成像、偏振成像、自动掩膜/阈值、多测量集联合成像或自校准流程时，使用此技能。
---

# WSClean - 射电干涉数据成像与去卷积

[WSClean](https://wsclean.readthedocs.io/en/latest/)（W-stacking Clean）是一款高效的射电干涉数据成像与去卷积命令行工具。采用创新的 w-stacking 算法替代传统 w-projection，在保证成像精度的同时大幅提升计算效率，处理 MWA 数据时比 CASA 的 w-projection 快一个数量级。

## 何时使用 WSClean

- 对射电干涉测量 MS 数据进行 CLEAN 成像
- 多尺度去卷积（分离不同尺度的源结构）
- 宽带（多频率）合成成像
- 偏振成像（I/Q/U/V、RR/LL/RL/LR、XX/YY/XY/YX）
- 旋转测量（RM）合成
- 自动掩膜与自动阈值去卷积
- 多测量集联合成像（不同频率/时间/望远镜）
- 自校准流程中的模型预测
- 分布式大规模成像（MPI）

## 功能模块

### 1. 成像算法

- **W-stacking**：FFT 后乘法校正，比卷积方式快得多
- **图像域网格化**：支持 A 项方向相关校正
- **快照成像**：处理天空弯曲效应
- **基线相关平均（BDA）**：提升计算效率

### 2. 去卷积方法

| 方法 | 说明 |
|------|------|
| Högbom CLEAN | 经典点源去卷积 |
| Cotton-Schwab CLEAN | 主循环去卷积（`-mgain < 1`） |
| Multi-scale CLEAN | 多尺度源结构分离 |
| IUWT | 压缩感知去卷积 |
| MORESANE | 模拟元素去卷积 |
| ASP | 自适应尺度像素（较慢） |

### 3. 自动化处理

- **自动阈值**：每次主迭代前自动估算残差噪声水平
- **自动掩膜**：基于信噪比动态生成去卷积掩膜
- **局部 RMS**：基于局部噪声的自适应阈值

### 4. 多频率与偏振

- **宽带成像**：全带宽联合去卷积，支持子带分割输出
- **多频率加权**：优化宽带成像权重
- **偏振联合去卷积**：I/Q/U/V 联合清理
- **RM 合成**：旋转测量分析

### 5. 数据融合

- **多测量集**：同时整合不同频率、时间、望远镜的数据
- **相位中心调整**：不同指向观测间旋转相位中心
- **主波束校正**：ATDB 波束模型修正（如 MWA）

### 6. 加权与网格化

| 加权方案 | 语法 |
|----------|------|
| Natural | `-weight natural` |
| Uniform | `-weight uniform` |
| Briggs | `-weight briggs <robust>` |
| Super-uniform | `-weight super` |

- 锥度（taper）：`-taper-gaussian <size>`
- 权重秩滤波：去除异常值

### 7. 计算性能

- **多线程**：`-j <threads>`
- **MPI 分布式**：`mpirun -np <N> wsclean ...`
- **并行去卷积**：`-parallel-deconvolution <size>`

### 8. 输出格式

- FITS 图像（dirty/clean/restored/model/residual）
- 源组件列表：`-save-source-list <file>`
- 成像权重：`-save-weights <file>`

## 基本用法

```bash
wsclean [options] <ms1.ms> [<ms2.ms> ...]
```

运行 `wsclean`（不带参数）可查看所有参数的简要说明。

## 详细参考

- [命令行参数参考](reference.md)
- [代码示例](examples.md)

## 相关资源

- 官方文档：<https://wsclean.readthedocs.io/en/latest/>
- Offringa et al. 2014, MNRAS, 444, 606
