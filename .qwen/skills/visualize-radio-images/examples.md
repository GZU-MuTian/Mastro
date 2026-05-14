# CARTA 使用示例

## 基本连接与图像打开

```python
from carta.session import Session
from carta.image import Image

# 连接到 CARTA 后端（需要 CARTA 服务已启动）
session = Session("localhost:1234")
session.connect()

# 打开 FITS 图像
image = session.open_image("/data/observation.fits")

# 打开 CASA 图像
image = session.open_image("/data/observation.image")

# 打开 HDF5 图像（IDIA 模式）
image = session.open_image("/data/cube.hdf5", hdu=0)

# 获取图像信息
info = image.file_info
print(f"维度: {info['dimensions']}")
print(f"坐标系: {info['coordinateType']}")
```

## 渲染控制

```python
# 设置颜色映射表
image.set_colormap("viridis")   # 可选: viridis, jet, hot, inferno, magma, plasma

# 设置缩放函数
image.set_scaling("linear")     # 可选: linear, log, sqrt, square, gamma

# 设置显示值范围
image.set_value_range(-0.001, 0.005)  # min, max (Jy/beam)

# 设置偏压和对比度
image.set_bias_contrast(0.5, 1.0)

# 设置 NaN 颜色
image.set_nan_color("#000000")
```

## 等值线叠加

```python
# 在栅格图像上叠加等值线
levels = [0.001, 0.002, 0.004, 0.008, 0.016]  # Jy/beam
image.set_contours(enabled=True, levels=levels, color="#FFFFFF")
```

## 区域操作

```python
from carta.region import Region

# 创建圆形区域
region = Region(image)
region.create_ellipse(x=1024, y=1024, r1=50, r2=50)  # 圆形

# 创建矩形区域
region.create_rect(x=1024, y=1024, w=100, h=80)

# 创建多边形区域
vertices = [(100, 100), (200, 150), (250, 300), (150, 280)]
region.create_polygon(vertices)

# 导入 DS9 区域文件
region.import_regions("/data/source.reg")

# 导出为 CASA CRTF 格式
region.export_regions("/output/regions.crtf", format="crtf")

# 获取区域统计
stats = image.get_stats(region)
print(f"均值: {stats['mean']:.6f} Jy/beam")
print(f"标准差: {stats['stdDev']:.6f} Jy/beam")
print(f"通量密度: {stats['fluxDensity']:.4f} Jy")
```

## 光谱剖面提取

```python
from carta.region import Region

# 创建区域
region = Region(image)
region.create_ellipse(x=1024, y=1024, r1=30, r2=30)

# 提取 Stokes I 光谱剖面
profile = image.get_spectral_profile(region, stokes="I")

# profile 包含频率和强度数据
freqs = profile['xValues']      # 频率轴（MHz 或 GHz）
intensity = profile['yValues']  # 强度值

# 提取多偏振剖线
for stokes in ["I", "Q", "U", "V"]:
    profile = image.get_spectral_profile(region, stokes=stokes)
    print(f"Stokes {stokes}: 峰值 = {max(profile['yValues']):.4f}")
```

## 空间剖面提取

```python
# 沿线段提取空间剖面
start = (512, 512)
end = (1536, 1536)
spatial_profile = image.get_spatial_profile(start, end)

# 沿折线提取剖面
waypoints = [(100, 100), (500, 300), (800, 600)]
# 需要先创建折线区域，再提取剖面
```

## 矩图生成

```python
# 生成 0 阶矩图（积分强度）
moment0 = image.get_moment_map(moment=0, range=(1420.0, 1421.0))

# 生成 1 阶矩图（速度场）
moment1 = image.get_moment_map(moment=1, range=(1420.0, 1421.0))

# 生成 2 阶矩图（速度弥散）
moment2 = image.get_moment_map(moment=2, range=(1420.0, 1421.0))
```

## PV 图提取

```python
# 沿指定路径提取 PV 图
start = (512, 512)    # 起点像素坐标
end = (1536, 1536)    # 终点像素坐标
width = 10            # 积分宽度（像素）

pv_slice = image.get_pv_slice(start, end, width)
```

## 在线数据查询

```python
# SIMBAD 查询
image.query_simbad("Cas A")

# VizieR 查询（在指定天区搜索星表）
image.query_vizier(
    catalog="VII/237",    # NVSS 目录
    ra=83.633,            # 赤经 (deg)
    dec=22.014,           # 赤纬 (deg)
    radius=0.5            # 搜索半径 (deg)
)

# HiPS2FITS 查询
image.query_hips(
    hips_id="CDS/P/DSS2/color",
    ra=83.633, dec=22.014,
    fov=1.0  # 视场 (deg)
)

# 谱线查询（Splatalogue）
image.query_splatalogue(freq_range=(1420.0, 1422.0))  # MHz
```

## 多图像操作

```python
# 打开多个图像
img1 = session.open_image("/data/continuum.fits")
img2 = session.open_image("/data/HI_cube.fits")
img3 = session.open_image("/data/CO_cube.fits")

# 图像匹配（空间对齐）
# 在 CARTA 前端中通过 UI 操作，或通过 API 设置匹配模式

# 导出当前视图
img1.export_image("/output/continuum_view.png", format="png")
```

## 目录操作

```python
# 加载 VOTable 目录
session.load_votable("/data/catalog.vot")

# 加载 CSV 目录
session.load_catalog("/data/sources.csv")

# 打开 FITS 目录
session.open_catalog_file("/data/catalog.fits", file_type=0)
```

## 图像拟合

```python
# 2D 高斯拟合（需在目标区域上执行）
region = Region(image)
region.create_rect(x=1024, y=1024, w=100, h=100)

# 获取区域统计（包含拟合参数）
stats = image.get_stats(region)
# 拟合结果包含峰值位置、FWHM、位置角等
```

## 斯托克斯偏振分析

```python
# 打开偏振立方体
stokes_image = session.open_image("/data/stokes_cube.fits")

# 提取各 Stokes 分量的剖线
for stokes in ["I", "Q", "U", "V"]:
    profile = stokes_image.get_spectral_profile(region, stokes=stokes)
    print(f"Stokes {stokes} 峰值: {max(profile['yValues']):.4f}")

# 矢量场叠加（偏振方向与强度）
# 需要分别打开强度和角度图像
intensity_img = session.open_image("/data/pol_intensity.fits")
angle_img = session.open_image("/data/pol_angle.fits")
stokes_image.set_vector_overlay(intensity_img, angle_img, threshold=0.001)
```
