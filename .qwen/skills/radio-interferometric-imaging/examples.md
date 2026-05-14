# WSClean 使用示例

## 基本成像

```bash
# 最简单的 CLEAN：2048×2048 像素，1 角秒像素，自然加权
wsclean -size 2048 2048 -scale 1asec -niter 1000 observation.ms

# Briggs 加权（robust=0）
wsclean -size 4096 4096 -scale 0.5asec -niter 5000 -weight briggs 0 observation.ms

# 指定输出文件名前缀
wsclean -name my_image -size 2048 2048 -scale 1asec -niter 1000 observation.ms
```

## Cotton-Schwab CLEAN（主循环）

```bash
# 启用主循环（-mgain < 1），每次主迭代重新计算残差
wsclean -size 2048 2048 -scale 1asec -niter 50000 -mgain 0.8 \
  -auto-threshold 3 -auto-mask 5 observation.ms
```

## 多尺度 CLEAN

```bash
# 自动尺度选择
wsclean -size 4096 4096 -scale 1asec -niter 50000 -mgain 0.8 \
  -multiscale -auto-threshold 3 -auto-mask 5 observation.ms

# 指定尺度列表（像素）
wsclean -size 4096 4096 -scale 1asec -niter 50000 -mgain 0.8 \
  -multiscale -multiscale-scales 0,3,10,30,100 \
  -auto-threshold 3 -auto-mask 5 observation.ms

# 调整尺度偏置（更偏向大尺度结构）
wsclean -size 4096 4096 -scale 1asec -niter 50000 -mgain 0.8 \
  -multiscale -multiscale-scale-bias 0.3 -auto-mask 5 observation.ms
```

## 宽带成像

```bash
# 8 通道宽带 CLEAN，联合去卷积
wsclean -size 4096 4096 -scale 1asec -niter 50000 -mgain 0.8 \
  -channels-out 8 -join-channels -auto-threshold 3 observation.ms

# 选择频率子集
wsclean -size 2048 2048 -scale 1asec -niter 1000 \
  -channels-out 4 -join-channels -channel-range 10 50 observation.ms
```

## 偏振成像

```bash
# Stokes I/Q/U/V 四分量成像
wsclean -size 2048 2048 -scale 1asec -niter 1000 \
  -pol iquv observation.ms

# 线偏振联合去卷积
wsclean -size 2048 2048 -scale 1asec -niter 50000 -mgain 0.8 \
  -pol iquv -join-polarizations -auto-threshold 3 observation.ms

# 圆偏振基（VLBI）
wsclean -size 4096 4096 -scale 0.5masec -niter 50000 \
  -pol rr,ll -join-polarizations observation.ms
```

## 多测量集联合成像

```bash
# 同时成像多个 MS（不同频率/望远镜）
wsclean -size 8192 8192 -scale 0.5asec -niter 100000 -mgain 0.8 \
  -channels-out 16 -join-channels -multiscale -auto-mask 5 \
  low_freq.ms high_freq.ms
```

## 自动掩膜与阈值

```bash
# 自动阈值：残差峰值 < 3σ 时停止
wsclean -size 2048 2048 -scale 1asec -niter 50000 \
  -auto-threshold 3 observation.ms

# 自动掩膜：首次迭代清理到 5σ 后生成掩膜
wsclean -size 2048 2048 -scale 1asec -niter 50000 -mgain 0.8 \
  -auto-mask 5 -auto-threshold 1.5 observation.ms

# 使用预定义 FITS 掩膜
wsclean -size 2048 2048 -scale 1asec -niter 50000 \
  -fits-mask my_mask.fits observation.ms

# 局部 RMS 自适应阈值
wsclean -size 2048 2048 -scale 1asec -niter 50000 \
  -auto-threshold 3 -local-rms observation.ms
```

## 自校准流程

```bash
# 第一轮：成像
wsclean -name round1 -size 4096 4096 -scale 1asec \
  -niter 10000 -mgain 0.8 -auto-threshold 3 observation.ms

# 用模型预测（填充 MODEL_DATA 列）
wsclean -name round1 -predict observation.ms

# （在 CASA/DPPP 中进行相位校准）

# 第二轮：更深的成像
wsclean -name round2 -size 4096 4096 -scale 1asec \
  -niter 50000 -mgain 0.8 -auto-mask 5 -auto-threshold 1.5 \
  -multiscale observation.ms
```

## 性能优化

```bash
# 多线程并行（8 线程）
wsclean -j 8 -size 4096 4096 -scale 1asec -niter 50000 observation.ms

# 并行去卷积（大视场）
wsclean -j 8 -parallel-deconvolution 4096 \
  -size 8192 8192 -scale 0.5asec -niter 100000 observation.ms

# 限制内存使用
wsclean -j 8 -abs-mem 32 -size 8192 8192 -scale 1asec \
  -niter 50000 observation.ms

# MPI 分布式成像
mpirun -np 4 wsclean -j 8 -size 8192 8192 -scale 0.5asec \
  -niter 100000 -multiscale observation.ms
```

## 主波束校正

```bash
# 应用主波束校正（如 MWA）
wsclean -size 4096 4096 -scale 1asec -niter 50000 -mgain 0.8 \
  -apply-primary-beam -mwa-path /path/to/mwa/beams observation.ms

# 生成主波束图像
wsclean -size 4096 4096 -scale 1asec -niter 1 \
  -primary-beam -mwa-path /path/to/mwa/beams observation.ms
```

## 输出控制

```bash
# 只输出残差图（不生成 restored）
wsclean -size 2048 2048 -scale 1asec -niter 1000 \
  -no-restored observation.ms

# 输出清洁组件列表
wsclean -name my_src -size 2048 2048 -scale 1asec -niter 50000 \
  -mgain 0.8 -save-source-list my_sources.txt observation.ms

# 指定输入数据列
wsclean -size 2048 2048 -scale 1asec -niter 1000 \
  -data-column CORRECTED_DATA observation.ms
```

## 加权与锥度

```bash
# Briggs 加权 + 高斯锥度
wsclean -size 4096 4096 -scale 1asec -niter 50000 \
  -weight briggs -0.5 -taper-gaussian 3asec observation.ms

# 自然加权
wsclean -size 2048 2048 -scale 1asec -niter 1000 \
  -weight natural observation.ms

# 权重秩滤波（去除异常值）
wsclean -size 4096 4096 -scale 1asec -niter 50000 \
  -weight briggs 0 -weighting-rank-filter 3 observation.ms
```
