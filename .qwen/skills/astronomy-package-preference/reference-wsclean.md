# WSClean 命令行参数参考

> 完整参数列表请运行 `wsclean`（不带参数）或查阅 [官方文档](https://wsclean.readthedocs.io/en/latest/)。

## 基本成像参数

| 参数 | 语法 | 说明 |
|------|------|------|
| `-size` | `-size <width> <height>` | 图像尺寸（像素） |
| `-scale` | `-scale <value>` | 像素大小，如 `1asec`, `0.7amin`, `2.5masec` |
| `-name` | `-name <prefix>` | 输出文件名前缀 |
| `-padding` | `-padding <factor>` | 填充因子，默认 1.2 |
| `-niter` | `-niter <N>` | 最大清洁迭代次数 |
| `-gain` | `-gain <value>` | 循环增益，每次迭代从峰值减去的比例，默认 0.1 |
| `-mgain` | `-mgain <value>` | 主循环增益（< 1 启用 Cotton-Schwab），如 0.8 |
| `-threshold` | `-threshold <Jy>` | 绝对清洁停止阈值（Jy） |
| `-auto-threshold` | `-auto-threshold <sigma>` | 自动停止阈值（残差 RMS 的 σ 倍数） |
| `-auto-mask` | `-auto-mask <sigma>` | 自动掩膜阈值（σ），首次迭代后用模型生成掩膜 |
| `-nmiter` | `-nmiter <N>` | 主循环最大迭代次数，默认 0（无限制） |
| `-fits-mask` | `-fits-mask <file>` | 使用 FITS 文件作为清洁掩膜 |
| `-local-rms` | `-local-rms` | 启用局部 RMS 自适应阈值 |
| `-local-rms-map` | `-local-rms-map <file>` | 指定预计算的局部 RMS 图 |

## 多尺度去卷积

| 参数 | 语法 | 说明 |
|------|------|------|
| `-multiscale` | `-multiscale` | 启用多尺度 CLEAN |
| `-multiscale-scales` | `-multiscale-scales <px,px,...>` | 指定尺度列表（像素），如 `0,3,10,30` |
| `-multiscale-gain` | `-multiscale-gain <value>` | 多尺度增益，默认 0.7 |
| `-multiscale-scale-bias` | `-multiscale-scale-bias <value>` | 尺度偏置，默认 0.6，越低越偏向大尺度 |
| `-iuwt` | `-iuwt` | 启用 IUWT 压缩感知去卷积 |
| `-more` | `-more` | 启用 MORESANE 去卷积 |
| `-asp` | `-asp` | 启用自适应尺度像素（较慢） |

## 宽带与多频率

| 参数 | 语法 | 说明 |
|------|------|------|
| `-channels-out` | `-channels-out <N>` | 输出通道数（宽带成像） |
| `-join-channels` | `-join-channels` | 联合所有通道去卷积（宽带 CLEAN） |
| `-channel-range` | `-channel-range <start> <end>` | 选择频率通道子集 |
| `-channel-division-freq` | `-channel-division-freq <Hz>` | 子带分割频率 |
| `-spectral-index` | `-spectral-index` | 启用频谱指数拟合 |
| `-deconvolution-channels` | `-deconvolution-channels <N>` | 去卷积使用的通道数 |

## 偏振

| 参数 | 语法 | 说明 |
|------|------|------|
| `-pol` | `-pol <stokes>` | 偏振选择：`i`, `qu`, `iquv`, `xx,yy`, `rr,ll`, `xx,xy,yx,yy` 等 |
| `-join-polarizations` | `-join-polarizations` | 联合所有偏振去卷积 |
| `-link-polarizations` | `-link-polarizations` | 链接偏振的清洁组件位置 |

## 加权与锥度

| 参数 | 语法 | 说明 |
|------|------|------|
| `-weight` | `-weight <scheme>` | 加权方案：`natural`, `uniform`, `briggs <robust>`, `super` |
| `-taper-gaussian` | `-taper-gaussian <size>` | 高斯锥度，如 `3asec` |
| `-taper-tukey` | `-taper-tukey <size>` | Tukey 锥度 |
| `-taper-edge` | `-taper-edge <size>` | 边缘锥度 |
| `-super-weight` | `-super-weight <factor>` | 超级加权因子 |
| `-weighting-rank-filter` | `-weighting-rank-filter <level>` | 权重秩滤波级别 |

## 多测量集与时间

| 参数 | 语法 | 说明 |
|------|------|------|
| `-interval` | `-interval <start> <end>` | 选择时间间隔（行号） |
| `-intervals-out` | `-intervals-out <N>` | 输出时间间隔数 |
| `-minuvw-m` | `-minuvw-m <m>` | 最小 UV 距离（米） |
| `-maxuvw-m` | `-maxuvw-m <m>` | 最大 UV 距离（米） |

## 输出控制

| 参数 | 语法 | 说明 |
|------|------|------|
| `-save-source-list` | `-save-source-list <file>` | 输出清洁组件列表 |
| `-save-weights` | `-save-weights` | 保存成像权重 |
| `-save-uv` | `-save-uv` | 保存 UV 数据 |
| `-no-dirty` | `-no-dirty` | 不生成 dirty 图像 |
| `-no-psf` | `-no-psf` | 不生成 PSF |
| `-no-restored` | `-no-restored` | 不生成 restored 图像 |
| `-no-model` | `-no-model` | 不保存模型图像 |

## 预测与自校准

| 参数 | 语法 | 说明 |
|------|------|------|
| `-predict` | `-predict` | 预测模式：用现有模型填充 MODEL_DATA |
| `-subtract-model` | `-subtract-model` | 从数据中减去模型 |
| `-model-column` | `-model-column <col>` | 指定模型数据列名 |
| `-data-column` | `-data-column <col>` | 指定输入数据列名，默认 `DATA` |
| `-skip-final-iteration` | `-skip-final-iteration` | 跳过最后一轮预测-成像迭代 |

## 性能

| 参数 | 语法 | 说明 |
|------|------|------|
| `-j` | `-j <threads>` | 并行线程数 |
| `-parallel-deconvolution` | `-parallel-deconvolution <size>` | 并行去卷积尺寸（像素） |
| `-deconvolution-threads` | `-deconvolution-threads <N>` | 去卷积线程数 |
| `-abs-mem` | `-abs-mem <GB>` | 限制内存使用（GB） |

## 网格化

| 参数 | 语法 | 说明 |
|------|------|------|
| `-gridder` | `-gridder <method>` | 网格化方法：`fft`, `idg` |
| `-wgridder-accuracy` | `-wgridder-accuracy <value>` | W 网格化精度，默认 1e-4 |
| `-wgridder-pixel-accuracy` | `-wgridder-pixel-accuracy <value>` | 像素级精度 |

## 主波束校正

| 参数 | 语法 | 说明 |
|------|------|------|
| `-apply-primary-beam` | `-apply-primary-beam` | 应用主波束校正 |
| `-reuse-primary-beam` | `-reuse-primary-beam` | 复用已计算的主波束 |
| `-primary-beam` | `-primary-beam` | 生成主波束图像 |
| `-mwa-path` | `-mwa-path <dir>` | MWA 元素增益文件路径 |
