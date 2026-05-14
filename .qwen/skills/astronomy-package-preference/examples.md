# 天文数据处理代码示例

> 各包按工作流排列：在线查询 → 数据处理 → 成像 → 可视化。更多用法参考各包官方文档。

---

## 第一部分：Astropy — 核心数据处理

### 物理单位 (astropy.units)

```python
from astropy import units as u

# 创建带单位的量
distance = 4.2 * u.lightyear
flux = 1e-12 * u.erg / (u.s * u.cm**2 * u.AA)

# 单位转换
distance.to(u.pc)     # 光年 → 秒差距
distance.to(u.km)     # 光年 → 公里

# 等价转换（波长 ↔ 频率）
wavelength = 500 * u.nm
frequency = wavelength.to(u.Hz, equivalencies=u.spectral())

# 获取数值和单位
distance.value, distance.unit
distance.decompose()  # → SI 基本单位
```

### 天球坐标 (astropy.coordinates)

```python
from astropy.coordinates import SkyCoord
import astropy.units as u

# 创建坐标
c = SkyCoord(ra=10.6847*u.degree, dec=41.2688*u.degree, frame='icrs')
c = SkyCoord('00h42m44.33s +41d16m07.5s', frame='icrs')

# 坐标系转换
c.galactic                 # → 银道坐标
c.transform_to('fk5')      # → FK5

# 三维坐标（带距离）
c_3d = SkyCoord(ra=10*u.degree, dec=20*u.degree, distance=100*u.pc)

# 角距计算
c1.separation(c2)          # 天球投影角距
c1.separation_3d(c2)       # 三维空间距离

# 从名称解析坐标
m31 = SkyCoord.from_name('M31')

# 数组坐标（高性能）
coords = SkyCoord(ra=[10, 11, 12]*u.degree, dec=[41, -5, 42]*u.degree)
```

### FITS 文件 (astropy.io.fits)

```python
from astropy.io import fits

# 读取
with fits.open('image.fits') as hdul:
    hdul.info()
    data = hdul[0].data
    header = hdul[0].header
    header['OBJECT']       # 读取关键字
    header['EXPTIME'] = 120  # 修改

# 大文件内存映射
with fits.open('large.fits', memmap=True) as hdul:
    data = hdul[0].data

# 便捷读取
data = fits.getdata('image.fits')
header = fits.getheader('image.fits')

# 写入图像
hdu = fits.PrimaryHDU(data=my_array)
hdu.header['OBJECT'] = 'M31'
hdu.writeto('output.fits', overwrite=True)

# 写入二进制表
col1 = fits.Column(name='name', format='20A', array=['srcA', 'srcB'])
col2 = fits.Column(name='flux', format='E', array=[1.2, 3.4])
fits.BinTableHDU.from_columns([col1, col2]).writeto('catalog.fits', overwrite=True)

# 更新已有文件
with fits.open('file.fits', mode='update') as hdul:
    hdul[0].header['OBJECT'] = 'updated'
    hdul.flush()
```

### 表格数据 (astropy.table)

```python
from astropy.table import Table, QTable, join, vstack
import astropy.units as u

# 创建表格
t = Table()
t['name'] = ['srcA', 'srcB', 'srcC']
t['flux'] = [1.2, 3.4, 0.8]

# QTable 支持 Quantity 列
qt = QTable()
qt['flux'] = [1.2, 3.4, 0.8] * u.Jy
qt['freq'] = [1.4, 5.0, 8.4] * u.GHz

# 访问与筛选
t['flux'], t[0], t[0]['flux'], t[t['flux'] > 2]

# 操作
t['new_col'] = [1, 2, 3]
del t['name']
join(t1, t2, keys='name')
vstack([t1, t2])

# 读写
t.write('output.fits', format='fits', overwrite=True)
t.write('output.ecsv')  # ECSV 保留元数据和单位
t2 = Table.read('output.fits')
df = t.to_pandas()
```

### 时间系统 (astropy.time)

```python
from astropy.time import Time
import astropy.units as u

t1 = Time('2024-01-15T12:30:00', scale='utc')
t2 = Time(59000.0, format='mjd', scale='utc')
t4 = Time.now()

t1.iso, t1.jd, t1.mjd, t1.datetime
t1.tai, t1.tt, t1.tdb        # 时间尺度转换
t_future = t1 + 3 * u.day
dt = t2 - t1                   # TimeDelta
```

### 宇宙学 (astropy.cosmology)

```python
from astropy.cosmology import Planck18

z = 0.5
Planck18.luminosity_distance(z)
Planck18.angular_diameter_distance(z)
Planck18.comoving_distance(z)
Planck18.age(z)
Planck18.lookback_time(z)
Planck18.distmod(z)
```

### WCS 坐标映射 (astropy.wcs)

```python
from astropy.wcs import WCS
from astropy.io import fits

wcs = WCS(fits.getheader('image.fits'))
sky = wcs.pixel_to_world(100, 200)  # 像素 → 天球 → SkyCoord
x, y = wcs.world_to_pixel(target)   # 天球 → 像素

# Matplotlib 中使用 WCS 投影
import matplotlib.pyplot as plt
ax = plt.subplot(projection=wcs)
ax.imshow(data, origin='lower')
ax.coords.grid(color='gray', alpha=0.5)
```

### 模型拟合 (astropy.modeling)

```python
from astropy.modeling import models, fitting

g = models.Gaussian1D(amplitude=3, mean=1, stddev=0.8)
combined = g + models.Linear1D(0.5, 0)

fitter = fitting.LevMarLSQFitter()
fitted = fitter(g, x_data, y_data)
fitted = fitter(g, x_data, y_data, weights=1/sigma**2)

fitted.amplitude.value, fitted.mean.value
y_fit = fitted(x_eval)
```

### 统计工具 (astropy.stats)

```python
from astropy.stats import sigma_clip, sigma_clipped_stats
from astropy.stats import biweight_location, biweight_scale

filtered = sigma_clip(data, sigma=3, maxiters=5)
mean, median, std = sigma_clipped_stats(data, sigma=3.0)
robust_mean = biweight_location(data)
robust_std = biweight_scale(data)
```

### 可视化 (astropy.visualization)

```python
from astropy.visualization import simple_norm, ImageNormalize, LogStretch

norm = simple_norm(data, 'zscale')
plt.imshow(data, norm=norm, origin='lower', cmap='gray')

norm = ImageNormalize(stretch=LogStretch())
plt.imshow(data, norm=norm)
```

---

## 第二部分：Astroquery — 在线数据库查询

### SIMBAD

```python
from astroquery.simbad import Simbad
import astropy.units as u

result = Simbad.query_object("m1")
result = Simbad.query_object("M [1-9]", wildcard=True)
ids = Simbad.query_objectids("Polaris")
result = Simbad.query_region(coord, radius=0.5*u.degree)

# 批量查询（避免循环）
result = Simbad.query_region(coords_array, radius=radius_array)

# ADQL 高级查询
query = """SELECT TOP 5 ra, dec, main_id, nbref
           FROM basic WHERE otype != 'Cl*..' AND rvz_redshift < 1
           ORDER BY nbref DESC"""
result = Simbad.query_tap(query)

# 自定义字段
simbad = Simbad()
simbad.add_votable_fields("otype", "mesplx")
simbad.ROW_LIMIT = 10
```

### VizieR

```python
from astroquery.vizier import Vizier
import astropy.units as u

Vizier.find_catalogs('hot jupiter exoplanet')
Vizier.ROW_LIMIT = -1
result = Vizier.get_catalogs("J/ApJ/788/39")
result = Vizier(row_limit=10).query_object("sirius")
result = Vizier.query_region("3C 273", radius=0.1*u.deg, catalog='GSC')

# 列过滤
vizier = Vizier(columns=['_RAJ2000', '_DEJ2000', 'Vmag', 'Plx'],
                column_filters={"Vmag": ">10"})
result = vizier.query_object("HD 226868", catalog=["NOMAD", "UCAC"])
```

### NED

```python
from astroquery.ipac.ned import Ned

result = Ned.query_object("NGC 224")
result = Ned.query_region("3c 273", radius=0.05*u.deg)
table = Ned.get_table("3C 273", table='redshifts')
images = Ned.get_images("m1")
spectra = Ned.get_spectra('3c 273')
```

### MAST

```python
from astroquery.mast import Observations, Catalogs

hst_obs = Observations.query_criteria(
    obs_collection="HST", dataproduct_type="image",
    coordinates=coord, radius="0.1 deg"
)
catalog_data = Catalogs.query_object("M10", radius="0.1 deg", catalog="Pan-STARRS")
products = Observations.get_product_list(hst_obs)
filtered = Observations.filter_products(products, productType="SCIENCE", extension="fits")
manifest = Observations.download_products(filtered, download_dir="./mast_downloads")
```

### Gaia

```python
from astroquery.gaia import Gaia

Gaia.MAIN_GAIA_TABLE = "gaiadr3.gaia_source"
Gaia.ROW_LIMIT = 50

# 锥形搜索
result = Gaia.cone_search_async(coord, radius=u.Quantity(1.0, u.deg)).get_results()

# ADQL 查询（推荐）
job = Gaia.launch_job_async(
    "SELECT TOP 100 source_id, ra, dec, parallax, phot_g_mean_mag "
    "FROM gaiadr3.gaia_source "
    "WHERE parallax > 10 AND phot_g_mean_mag < 12.0 "
    "ORDER BY phot_g_mean_mag"
)
result = job.get_results()
```

### IRSA

```python
from astroquery.ipac.irsa import Irsa
import astropy.units as u

Irsa.list_catalogs(filter='spitzer')
result = Irsa.query_region(coordinates=coord, spatial='Cone',
                           catalog='fp_psc', radius=2*u.arcmin)
result = Irsa.query_region("M81", catalog="allwise_p3as_psd", spatial="Cone")
```

### ESO

```python
from astroquery.eso import Eso

eso = Eso()
eso.list_instruments()
table = eso.query_instrument('midi', column_filters={'object': 'NGC4151'})
data_files = eso.retrieve_data(table['dp_id'][:2], destination="./data")
```

### 交叉匹配 (xmatch)

```python
from astroquery.xmatch import XMatch
import astropy.units as u

result = XMatch.query(
    cat1=input_table, cat2='vizier:II/246/out',
    max_distance=5*u.arcsec, colRA1='ra', colDec1='dec'
)
```

### NASA ADS

```python
from astroquery.nasa_ads import ADS

results = ADS.query_simple("supernova remnant X-ray")
results = ADS.query_simple("author:Hubble galaxy redshift")
```

### JPL Horizons

```python
from astroquery.jplhorizons import Horizons

obj = Horizons(id='Ceres', location='500', epochs=2459000.5)
eph = obj.ephemerids()
obj = Horizons(id='1P', epochs={'start':'2024-01-01', 'stop':'2024-12-31', 'step':'1d'})
```

---

## 第三部分：PyVO — VO 虚拟天文台数据访问

### TAP 表访问协议

```python
import pyvo as vo

tap = vo.dal.TAPService("https://dc.zah.uni-heidelberg.de/tap")

# 同步查询
result = tap.search("SELECT TOP 10 * FROM ivoa.obscore")

# 异步作业（分步控制）
job = tap.submit_job("SELECT * FROM huge_table")
job.executionduration = 700
job.run()
job.wait()
job.raise_if_error()
result = job.fetch_result()
job.delete()

# 上下文管理器（退出时自动删除）
with tap.submit_job("SELECT * FROM ivoa.obscore") as job:
    job.run()
    result = job.fetch_result()

# 上传本地表（TAP 1.1+）
result = tap.search(query, uploads={"my_table": "/path/to/data.csv"})
```

### SIA 简单图像访问

```python
import pyvo as vo
from astropy.coordinates import SkyCoord

sia = vo.dal.SIAService("http://dc.g-vo.org/hppunion/q/im/siap.xml")
pos = SkyCoord.from_name('NGC 4993')
results = sia.search(pos=pos, size=0.5 * u.deg, format='image/fits')
results = sia.search(pos=pos, size=0.5 * u.deg, intersect='covers', verbosity=3)
```

### SSA 简单光谱访问

```python
ssa = vo.dal.SSAService("http://archive.stsci.edu/ssap/search2.php?id=BEFS&")
results = ssa.search(pos=SkyCoord.from_name('Vega'), diameter=0.01*u.deg,
                     time=Time((53000, 54000), format='mjd'))
```

### SCS 锥形搜索

```python
scs = vo.dal.SCSService('http://dc.g-vo.org/arihip/q/cone/scs.xml')
results = scs.search(pos=SkyCoord(ra=10.68, dec=41.27, unit='deg'),
                     radius=0.1*u.deg, verbosity=3)
table = results.to_table()
```

### Registry 注册表查询

```python
from pyvo import registry

# 服务发现
for res in registry.search(waveband="infrared", servicetype="ssa"):
    result = res.service.search(pos=SkyCoord.from_name("Bellatrix"), size=0.001)

# 组合约束
resources = registry.search(
    registry.Freetext("supernova remnant"),
    registry.Waveband("X-ray"),
    registry.Servicetype("tap")
)

resources.to_table()
res = resources[0]
tap = res.service
result = tap.run_sync("SELECT TOP 5 * FROM ivoa.obscore")
```

### 跨档案全局发现

```python
from pyvo import discover
from astropy.time import Time

datasets, log = discover.images_globally(
    space=(273.5, -12.1, 0.1),
    spectrum=1 * u.nm,
    time=(Time('1995-01-01'), Time('1995-12-31'))
)
```

### SAMP 桌面应用通信

```python
with pyvo.samp.connection(client_name="my_script") as conn:
    pyvo.samp.send_table_to(conn, my_table, name="my-results", client_name="topcat")
    pyvo.samp.send_image_to(conn, image_url, name="my-image", client_name="aladin")
```

---

## 第四部分：WSClean — 射电干涉成像

### 基本成像

```bash
# 最简单：2048×2048, 1角秒像素, 自然加权
wsclean -size 2048 2048 -scale 1asec -niter 1000 observation.ms

# Briggs 加权
wsclean -size 4096 4096 -scale 0.5asec -niter 5000 -weight briggs 0 observation.ms
```

### Cotton-Schwab CLEAN

```bash
wsclean -size 2048 2048 -scale 1asec -niter 50000 -mgain 0.8 \
  -auto-threshold 3 -auto-mask 5 observation.ms
```

### 多尺度 CLEAN

```bash
wsclean -size 4096 4096 -scale 1asec -niter 50000 -mgain 0.8 \
  -multiscale -multiscale-scales 0,3,10,30,100 \
  -auto-threshold 3 -auto-mask 5 observation.ms
```

### 宽带成像

```bash
wsclean -size 4096 4096 -scale 1asec -niter 50000 -mgain 0.8 \
  -channels-out 8 -join-channels -auto-threshold 3 observation.ms
```

### 偏振成像

```bash
# IQUV 联合去卷积
wsclean -size 2048 2048 -scale 1asec -niter 50000 -mgain 0.8 \
  -pol iquv -join-polarizations -auto-threshold 3 observation.ms
```

### 多测量集联合成像

```bash
wsclean -size 8192 8192 -scale 0.5asec -niter 100000 -mgain 0.8 \
  -channels-out 16 -join-channels -multiscale -auto-mask 5 \
  low_freq.ms high_freq.ms
```

### 自校准流程

```bash
# 第一轮成像
wsclean -name round1 -size 4096 4096 -scale 1asec \
  -niter 10000 -mgain 0.8 -auto-threshold 3 observation.ms

# 预测模型
wsclean -name round1 -predict observation.ms

# (在 CASA/DPPP 中进行校准)

# 第二轮深度成像
wsclean -name round2 -size 4096 4096 -scale 1asec \
  -niter 50000 -mgain 0.8 -auto-mask 5 -auto-threshold 1.5 \
  -multiscale observation.ms
```

### 性能优化

```bash
# 多线程
wsclean -j 8 -size 4096 4096 -scale 1asec -niter 50000 observation.ms

# 限制内存
wsclean -j 8 -abs-mem 32 -size 8192 8192 -scale 1asec -niter 50000 observation.ms

# MPI 分布式
mpirun -np 4 wsclean -j 8 -size 8192 8192 -scale 0.5asec \
  -niter 100000 -multiscale observation.ms
```

---

## 第五部分：CARTA — 射电图像可视化

### 基本连接

```python
from carta.session import Session

session = Session("localhost:1234")
session.connect()
image = session.open_image("/data/observation.fits")
info = image.file_info
```

### 渲染控制

```python
image.set_colormap("viridis")        # viridis, jet, hot, inferno
image.set_scaling("linear")          # linear, log, sqrt, gamma
image.set_value_range(-0.001, 0.005)
image.set_bias_contrast(0.5, 1.0)
```

### 光谱剖面

```python
region = Region(image)
region.create_ellipse(x=1024, y=1024, r1=30, r2=30)
profile = image.get_spectral_profile(region, stokes="I")
freqs = profile['xValues']
intensity = profile['yValues']
```

### 矩图生成

```python
moment0 = image.get_moment_map(moment=0, range=(1420.0, 1421.0))  # 积分强度
moment1 = image.get_moment_map(moment=1, range=(1420.0, 1421.0))  # 速度场
moment2 = image.get_moment_map(moment=2, range=(1420.0, 1421.0))  # 速度弥散
```

### PV 图提取

```python
pv_slice = image.get_pv_slice(start=(512, 512), end=(1536, 1536), width=10)
```

### 区域统计

```python
stats = image.get_stats(region)
print(f"均值: {stats['mean']:.6f} Jy/beam")
print(f"通量密度: {stats['fluxDensity']:.4f} Jy")
```
