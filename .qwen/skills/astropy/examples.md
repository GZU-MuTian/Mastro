# Astropy 代码示例

> 更多高级用法请参考 [astropy 官方文档](https://docs.astropy.org/en/stable/)。

---

## 1. 物理单位 (astropy.units)

```python
from astropy import units as u

# 创建带单位的量
distance = 4.2 * u.lightyear
flux = 1e-12 * u.erg / (u.s * u.cm**2 * u.AA)

# 单位转换
distance.to(u.pc)          # 光年 → 秒差距
distance.to(u.km)          # 光年 → 公里

# 等价转换（波长 ↔ 频率）
wavelength = 500 * u.nm
frequency = wavelength.to(u.Hz, equivalencies=u.spectral())

# 获取数值和单位
distance.value   # 数值
distance.unit    # 单位

# 分解为基本单位
distance.decompose()  # → SI 基本单位
distance.cgs          # → CGS 制
```

---

## 2. 天球坐标 (astropy.coordinates)

```python
from astropy.coordinates import SkyCoord
import astropy.units as u

# 创建坐标（ICRS 赤道系）
c = SkyCoord(ra=10.6847*u.degree, dec=41.2688*u.degree, frame='icrs')
c = SkyCoord('00h42m44.33s +41d16m07.5s', frame='icrs')  # 字符串

# 创建银道坐标
c_gal = SkyCoord(l=121.174*u.degree, b=-21.573*u.degree, frame='galactic')

# 坐标系转换
c.galactic           # → 银道坐标
c.transform_to('fk5')  # → FK5

# 三维坐标（带距离）
c_3d = SkyCoord(ra=10*u.degree, dec=20*u.degree, distance=100*u.pc)

# 角距计算
c1.separation(c2)       # 天球投影角距
c1.separation_3d(c2)    # 三维空间距离

# 从名称解析坐标
m31 = SkyCoord.from_name('M31')

# 数组坐标（高性能）
coords = SkyCoord(ra=[10, 11, 12]*u.degree, dec=[41, -5, 42]*u.degree)
```

---

## 3. FITS 文件 (astropy.io.fits)

```python
from astropy.io import fits

# 读取
with fits.open('image.fits') as hdul:
    hdul.info()              # 查看文件结构
    data = hdul[0].data      # 图像数据 (numpy.ndarray)
    header = hdul[0].header  # 头信息

    # 头信息操作
    header['OBJECT']         # 读取关键字
    header['EXPTIME'] = 120  # 修改关键字
    header['OBSERVER'] = 'Hubble'  # 添加关键字

# 大文件内存映射
with fits.open('large.fits', memmap=True) as hdul:
    data = hdul[0].data

# 便捷函数
data = fits.getdata('image.fits')
header = fits.getheader('image.fits')

# 写入图像
hdu = fits.PrimaryHDU(data=my_array)
hdu.header['OBJECT'] = 'M31'
hdu.writeto('output.fits', overwrite=True)

# 写入二进制表
col1 = fits.Column(name='name', format='20A', array=['srcA', 'srcB'])
col2 = fits.Column(name='flux', format='E', array=[1.2, 3.4])
table_hdu = fits.BinTableHDU.from_columns([col1, col2])
table_hdu.writeto('catalog.fits', overwrite=True)

# 多扩展文件
hdul = fits.HDUList([
    fits.PrimaryHDU(),
    fits.ImageHDU(data=image, name='SCI'),
    fits.BinTableHDU.from_columns([col1, col2], name='CATALOG')
])
hdul.writeto('multiext.fits', overwrite=True)

# 更新已有文件
with fits.open('file.fits', mode='update') as hdul:
    hdul[0].header['OBJECT'] = 'updated'
    hdul.flush()
```

---

## 4. 表格数据 (astropy.table)

```python
from astropy.table import Table, QTable, join, vstack
import astropy.units as u
import numpy as np

# 创建表格
t = Table()
t['name'] = ['srcA', 'srcB', 'srcC']
t['flux'] = [1.2, 3.4, 0.8]
t['ra'] = [10.1, 11.2, 12.3] * u.degree

# QTable 支持 Quantity 列（保留单位信息）
qt = QTable()
qt['flux'] = [1.2, 3.4, 0.8] * u.Jy
qt['freq'] = [1.4, 5.0, 8.4] * u.GHz

# 访问
t['flux']         # 整列
t[0]              # 整行
t[0]['flux']      # 单元格
t[t['flux'] > 2]  # 条件筛选

# 列操作
t['new_col'] = [1, 2, 3]       # 添加列
del t['name']                   # 删除列
t.rename_column('flux', 'f')   # 重命名

# 行操作
t.add_row({'flux': 5.0, 'ra': 13.0})  # 添加行

# 表格操作
join(t1, t2, keys='name')   # 类似 SQL JOIN
vstack([t1, t2])             # 纵向拼接
t.group_by('name')           # 分组

# 读写
t.write('output.fits', format='fits', overwrite=True)
t.write('output.ecsv')       # ECSV（ASCII，保留元数据和单位）
t.write('output.csv', format='csv')
t2 = Table.read('output.fits')

# 与 Pandas 互转
df = t.to_pandas()
t_from_df = Table.from_pandas(df)
```

---

## 5. 时间系统 (astropy.time)

```python
from astropy.time import Time
import astropy.units as u

# 创建时间对象
t1 = Time('2024-01-15T12:30:00', scale='utc')  # ISO 字符串
t2 = Time(59000.0, format='mjd', scale='utc')   # 修正儒略日
t3 = Time(2459500.5, format='jd')               # 儒略日
t4 = Time.now()                                   # 当前时间

# 格式转换
t1.iso      # '2024-01-15 12:30:00.000'
t1.jd       # 儒略日
t1.mjd      # 修正儒略日
t1.datetime # Python datetime

# 时间尺度转换
t1.tai      # 国际原子时
t1.tt       # 地球时
t1.tdb      # 质心动力学时

# 时间算术
delta = 3 * u.day
t_future = t1 + delta
dt = t2 - t1           # TimeDelta 对象
dt.sec                 # 秒数差
dt.jd                  # 日数差
```

---

## 6. 宇宙学 (astropy.cosmology)

```python
from astropy.cosmology import Planck18, FlatLambdaCDM
import astropy.units as u

# 使用预定义宇宙模型
z = 0.5
Planck18.luminosity_distance(z)        # 光度距离
Planck18.angular_diameter_distance(z)  # 角直径距离
Planck18.comoving_distance(z)          # 共动距离
Planck18.age(z)                        # 该红移处宇宙年龄
Planck18.lookback_time(z)             # 回顾时间
Planck18.distmod(z)                    # 距离模数
Planck18.comoving_volume(z)           # 共动体积

# 自定义宇宙模型
cosmo = FlatLambdaCDM(H0=70, Om0=0.3, Tcmb0=2.725)
```

---

## 7. WCS 坐标映射 (astropy.wcs)

```python
from astropy.wcs import WCS
from astropy.io import fits
from astropy.coordinates import SkyCoord
import astropy.units as u

# 从 FITS 头加载 WCS
header = fits.getheader('image.fits')
wcs = WCS(header)

# 像素 → 天球坐标
sky = wcs.pixel_to_world(100, 200)  # 返回 SkyCoord

# 天球 → 像素坐标
target = SkyCoord(ra=5.528*u.degree, dec=-72.052*u.degree)
x, y = wcs.world_to_pixel(target)

# 在 Matplotlib 中使用 WCS 投影
import matplotlib.pyplot as plt
ax = plt.subplot(projection=wcs)
ax.imshow(data, origin='lower')
ax.set_xlabel('RA')
ax.set_ylabel('Dec')
ax.coords.grid(color='gray', alpha=0.5)
```

---

## 8. 模型拟合 (astropy.modeling)

```python
from astropy.modeling import models, fitting
import numpy as np

# 预定义模型
g = models.Gaussian1D(amplitude=3, mean=1, stddev=0.8)
p = models.Polynomial1D(degree=2, c0=1, c1=0.5, c2=0.1)
bb = models.BlackBody(temperature=5800 * u.K)
g2d = models.Gaussian2D(amplitude=1, x_mean=0, y_mean=0)

# 模型组合
combined = models.Gaussian1D(1, 0, 0.5) + models.Linear1D(0.5, 0)

# 拟合数据
fitter = fitting.LevMarLSQFitter()       # Levenberg-Marquardt
fitted = fitter(g, x_data, y_data)

# 带权重拟合
fitted = fitter(g, x_data, y_data, weights=1/sigma**2)

# 访问拟合参数
fitted.amplitude.value
fitted.mean.value
fitted.stddev.value

# 评估模型
y_fit = fitted(x_eval)
```

---

## 9. 统计工具 (astropy.stats)

```python
from astropy.stats import sigma_clip, sigma_clipped_stats
from astropy.stats import biweight_location, biweight_scale
import numpy as np

# Sigma clipping（剔除异常值）
filtered = sigma_clip(data, sigma=3, maxiters=5)

# 便捷函数：一次获取均值、中位数、标准差
mean, median, std = sigma_clipped_stats(data, sigma=3.0)

# 鲁棒统计量（对异常值不敏感）
robust_mean = biweight_location(data)
robust_std = biweight_scale(data)

# 高斯 σ ↔ FWHM 转换
from astropy.stats import gaussian_sigma_to_fwhm, gaussian_fwhm_to_sigma
fwhm = sigma * gaussian_sigma_to_fwhm  # 常量 2.3548
```

---

## 10. 卷积与核 (astropy.convolution)

```python
from astropy.convolution import convolve, convolve_fft
from astropy.convolution import Gaussian2DKernel, Box2DKernel, Tophat2DKernel

# 高斯平滑
kernel = Gaussian2DKernel(x_stddev=3)
smoothed = convolve(image, kernel)

# 快速卷积（FFT，适合大图像）
smoothed = convolve_fft(image, kernel, boundary='wrap')

# 预定义核
Box2DKernel(width=5)          # 均匀方盒
Tophat2DKernel(radius=3)      # 圆形

# 自定义核
from astropy.convolution import CustomKernel
custom = CustomKernel(array=[0.1, 0.2, 0.4, 0.2, 0.1])
```

---

## 11. N 维数据 (astropy.nddata)

```python
from astropy.nddata import NDData, StdDevUncertainty, CCDData

# 创建带不确定性的数据
ndd = NDData(data_array, uncertainty=StdDevUncertainty(sigma_array))

# 带掩码
ndd = NDData(data_array, uncertainty=unc, mask=mask_array)

# 不确定性传播的算术运算
result = ndd + ndd   # uncertainty 自动传播

# CCDData（FITS 集成）
ccd = CCDData.read('image.fits', unit='adu')
ccd.write('output.fits')
```

---

## 12. 可视化 (astropy.visualization)

```python
from astropy.visualization import simple_norm, ImageNormalize, ZScaleInterval, LogStretch
import matplotlib.pyplot as plt

# ZScale 拉伸（天文图像标准）
norm = simple_norm(data, 'zscale')
plt.imshow(data, norm=norm, origin='lower', cmap='gray')

# Log 拉伸
norm = ImageNormalize(stretch=LogStretch())
plt.imshow(data, norm=norm)

# 自定义拉伸
from astropy.visualization import AsinhStretch
norm = ImageNormalize(vmin=0, vmax=1000, stretch=AsinhStretch())

# WCS 坐标轴
from astropy.wcs import WCS
ax = plt.subplot(projection=WCS(header))
```

---

## 13. 物理常数 (astropy.constants)

```python
from astropy import constants as c
from astropy import units as u

c.c        # 光速
c.G        # 引力常数
c.M_sun    # 太阳质量
c.R_sun    # 太阳半径
c.k_B      # 玻尔兹曼常数
c.h        # 普朗克常数
c.m_p      # 质子质量
c.sigma_sb # 斯特藩-玻尔兹曼常数

# 与单位配合
energy = c.h * frequency   # 带单位的计算
```
