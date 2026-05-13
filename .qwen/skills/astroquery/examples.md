# Astroquery 代码示例

> 更多高级用法请参考 [astroquery 官方文档](https://astroquery.readthedocs.io/en/latest/)。

---

## 1. SIMBAD 天文数据库

```python
from astroquery.simbad import Simbad
from astropy.coordinates import SkyCoord
import astropy.units as u

# 按名称查询
result = Simbad.query_object("m1")  # 蟹状星云
result = Simbad.query_object("M [1-9]", wildcard=True)  # 通配符

# 查询天体所有标识符
ids = Simbad.query_objectids("Polaris")

# 按坐标区域查询
coord = SkyCoord(ra=10.68*u.degree, dec=41.27*u.degree)
result = Simbad.query_region(coord, radius=0.5*u.degree)

# 批量查询多个区域（避免循环调用）
coords = SkyCoord(ra=[10, 11]*u.degree, dec=[10, 11]*u.degree)
result = Simbad.query_region(coords, radius=[0.1, 0.2]*u.deg)

# 查询目录中的天体
result = Simbad.query_catalog('ESO')

# 查询天体的父/子/兄弟关系
result = Simbad.query_hierarchy("Mrk 116", hierarchy="children")

# ADQL 高级查询
query = """SELECT TOP 5 ra, dec, main_id, nbref
           FROM basic WHERE otype != 'Cl*..' AND rvz_redshift < 1
           ORDER BY nbref DESC"""
result = Simbad.query_tap(query)

# 自定义输出字段
simbad = Simbad()
simbad.add_votable_fields("otype", "mesplx")
simbad.ROW_LIMIT = 10
result = simbad.query_object("m1")
```

---

## 2. VizieR 星表服务

```python
from astroquery.vizier import Vizier
from astropy.coordinates import SkyCoord
import astropy.units as u

# 搜索目录
catalogs = Vizier.find_catalogs('hot jupiter exoplanet')
for k, v in catalogs.items():
    print(k, ":", v.description)

# 下载完整目录
Vizier.ROW_LIMIT = -1  # 无限制
result = Vizier.get_catalogs("J/ApJ/788/39")

# 按名称查询
vizier = Vizier(row_limit=10)
result = vizier.query_object("sirius")

# 区域查询（指定目录）
result = vizier.query_region(
    "3C 273", radius=0.1*u.deg, catalog='GSC'
)

# 矩形区域查询
coord = SkyCoord(ra=299.590, dec=35.201, unit='deg')
result = vizier.query_region(coord, width="30m", catalog=["NOMAD", "UCAC"])

# 列选择与过滤
vizier = Vizier(
    columns=['_RAJ2000', '_DEJ2000', 'Vmag', 'Plx'],
    column_filters={"Vmag": ">10"}
)
result = vizier.query_object("HD 226868", catalog=["NOMAD", "UCAC"])

# 在 Gaia 目录中按星等过滤
result = Vizier(catalog='I/345/gaia2',
                column_filters={'Gmag': '<19'}).query_region(
    SkyCoord.from_name('M81'), radius=10*u.arcmin
)

# 获取目录元数据
metadata = Vizier(catalog="VII/74A").get_catalog_metadata()
```

---

## 3. NED 河外数据库

```python
from astroquery.ipac.ned import Ned
import astropy.units as u
from astropy.coordinates import SkyCoord

# 按名称查询
result = Ned.query_object("NGC 224")

# 区域查询
result = Ned.query_region("3c 273", radius=0.05*u.deg)

# 使用坐标查询
coord = SkyCoord(ra=56.38, dec=38.43, unit='deg')
result = Ned.query_region(coord, radius=0.1*u.deg)

# 按文献代码查询
result = Ned.query_refcode('1997A&A...323...31K')

# 获取数据表（positions, photometry, diameters, redshifts, references）
table = Ned.get_table("3C 273", table='redshifts')

# 下载图像
images = Ned.get_images("m1")          # 返回 HDUList 列表
image_urls = Ned.get_image_list("m1")  # 返回 URL 列表

# 下载光谱
spectra = Ned.get_spectra('3c 273')
```

---

## 4. MAST 太空望远镜档案

```python
from astroquery.mast import Observations, Catalogs, MastMissions, Mast
from astropy.coordinates import SkyCoord
import astropy.units as u

# 按目标名称查询观测
obs = Observations.query_object("M42", radius="0.2 deg")

# 按坐标和任务查询
coord = SkyCoord(ra=10.6847, dec=41.269, unit="deg")
hst_obs = Observations.query_criteria(
    coordinates=coord,
    radius="0.1 deg",
    obs_collection="HST",
    dataproduct_type="image"
)

# 查询 JWST 系外行星观测
jwst_obs = Observations.query_criteria(
    obs_collection="JWST",
    target_classification="*exoplanet*",
    dataproduct_type="spectrum"
)

# 解析天体名称为坐标
mast = Mast()
coords = mast.resolve_object("M101", resolver="NED")

# 查询星表（Pan-STARRS、HSC 等）
catalog_data = Catalogs.query_object(
    "M10", radius="0.1 deg", catalog="Pan-STARRS"
)

# 获取并下载数据产品
products = Observations.get_product_list(hst_obs)
filtered = Observations.filter_products(products, productType="SCIENCE", extension="fits")
manifest = Observations.download_products(filtered, download_dir="./mast_downloads")

# 特定任务查询（HST）
hst = MastMissions(mission="hst")
hst_results = hst.query_criteria(target_name='M42', filters='F160W')

# 访问受限数据
Observations.login(token="YOUR_MAST_TOKEN")
```

---

## 5. Gaia 天体测量数据

```python
from astroquery.gaia import Gaia
from astropy.coordinates import SkyCoord
import astropy.units as u

# 设置数据版本
Gaia.MAIN_GAIA_TABLE = "gaiadr3.gaia_source"

# 矩形区域搜索
coord = SkyCoord(ra=280, dec=-60, unit='deg')
width = u.Quantity(0.1, u.deg)
height = u.Quantity(0.1, u.deg)
result = Gaia.query_object_async(coordinate=coord, width=width, height=height)

# 锥形搜索
Gaia.ROW_LIMIT = 50
result = Gaia.cone_search_async(coord, radius=u.Quantity(1.0, u.deg)).get_results()

# ADQL 查询（最灵活，推荐）
job = Gaia.launch_job_async(
    "SELECT TOP 100 source_id, ra, dec, parallax, pmra, pmdec, phot_g_mean_mag "
    "FROM gaiadr3.gaia_source "
    "WHERE parallax > 10 AND phot_g_mean_mag < 12.0 "
    "ORDER BY phot_g_mean_mag"
)
result = job.get_results()

# 保存结果到文件
job = Gaia.launch_job_async(
    "SELECT TOP 1000 source_id, ra, dec, parallax "
    "FROM gaiadr3.gaia_source",
    dump_to_file=True, output_format='csv'
)

# 探索可用表
tables = Gaia.load_tables(only_names=True)
for t in tables:
    print(t.get_qualified_name())

# 查看表的列
gaiadr3 = Gaia.load_table('gaiadr3.gaia_source')
for col in gaiadr3.columns:
    print(col.name)

# 获取额外数据（光变曲线、光谱等）
datalink = Gaia.load_data(
    ids=[2263166706630078848],
    data_release='Gaia DR3',
    retrieval_type='EPOCH_PHOTOMETRY'
)

# 控制行数
Gaia.ROW_LIMIT = 10     # 限制 10 行
Gaia.ROW_LIMIT = -1     # 无限制
Gaia.ROW_LIMIT = 2000   # 恢复默认
```

---

## 6. IRSA 红外档案

```python
from astroquery.ipac.irsa import Irsa
from astropy.coordinates import SkyCoord
import astropy.units as u

# 查看可用目录
Irsa.list_catalogs(filter='spitzer')

# 锥形搜索
coord = SkyCoord(121.1743, -21.5733, unit='deg', frame='galactic')
result = Irsa.query_region(
    coordinates=coord, spatial='Cone',
    catalog='fp_psc',  # 2MASS 点源目录
    radius=2*u.arcmin
)

# 按天体名称搜索
result = Irsa.query_region(
    "M81", catalog="allwise_p3as_psd",
    spatial="Cone", radius="2 arcmin"
)

# 框形搜索
result = Irsa.query_region(
    coordinates=coord, spatial='Box',
    catalog='fp_psc', width=2*u.arcmin
)

# 指定返回列
result = Irsa.query_region(
    "HIP 12", catalog="allwise_p3as_psd",
    spatial="Cone", columns="ra,dec,w1mpro", radius=2*u.arcmin
)

# TAP 查询（ADQL）
query = """SELECT TOP 10 ra, dec, j_m, h_m, k_m
           FROM fp_psc
           WHERE CONTAINS(POINT('ICRS', ra, dec),
                          CIRCLE('ICRS', 202.484, 47.231, 0.4)) = 1"""
result = Irsa.query_tap(query).to_qtable()

# 图像查询
result = Irsa.query_sia(
    pos=(coord, 1*u.arcmin), collection='spitzer_seip'
)

# 行限制
Irsa.ROW_LIMIT = 1000
```

---

## 7. ESO 科学档案

```python
from astroquery.eso import Eso

eso = Eso()
eso.ROW_LIMIT = 10

# 列出可用仪器
instruments = eso.list_instruments()

# 查询特定仪器的数据
table = eso.query_instrument(
    'midi',
    column_filters={
        'object': 'NGC4151',
        'exp_start': "between '2008-01-01' and '2009-05-12'"
    },
    columns=['object', 'date_obs']
)

# 查询已处理数据（勘测项目）
surveys = eso.list_surveys()
table = eso.query_surveys(surveys='HARPS', target_name="HD203608")

# 下载数据
data_files = eso.retrieve_data(table['dp_id'][:2], destination="./data")

# 获取完整 FITS 头信息
headers = eso.get_headers(table['dp_id'])

# 认证访问受限数据
eso.login(username="YOUR_USERNAME", store_password=True)
table = eso.query_instrument("nirps", authenticated=True)
```

---

## 8. 星表交叉匹配 (xmatch)

```python
from astroquery.xmatch import XMatch
from astropy.table import Table
import astropy.units as u

# 本地表与在线目录匹配
input_table = Table.read('pos_list.csv')  # 需包含 ra, dec 列
result = XMatch.query(
    cat1=input_table,
    cat2='vizier:II/246/out',  # 2MASS 目录
    max_distance=5*u.arcsec,
    colRA1='ra', colDec1='dec'
)
# 结果包含匹配的目录列和 angDist（匹配距离）

# 两个在线目录互匹配
result = XMatch.query(
    cat1='vizier:I/345/gaia2',    # Gaia DR2
    cat2='vizier:II/246/out',     # 2MASS
    max_distance=1*u.arcsec
)
```

---

## 9. NASA ADS 文献查询

```python
from astroquery.nasa_ads import ADS

# 按关键词搜索
results = ADS.query_simple("supernova remnant X-ray")

# 按作者搜索
results = ADS.query_simple("author:Hubble galaxy redshift")
```

---

## 10. JPL 太阳系天体历表

```python
from astroquery.jplhorizons import Horizons

# 查询小行星历表
obj = Horizons(id='Ceres', location='500', epochs=2459000.5)
eph = obj.ephemerids()  # 获取星历（位置、亮度等）
vec = obj.vectors()      # 获取状态向量

# 查询彗星
obj = Horizons(id='1P', location='500', epochs={'start':'2024-01-01', 'stop':'2024-12-31', 'step':'1d'})
eph = obj.ephemerids()

# 指定观测站
obj = Horizons(id='Ceres', location='G37', epochs=2459000.5)  # MMT 望远镜
```

---

## 11. 辅助模块示例

### splatalogue — 射电分子谱线
```python
from astroquery.splatalogue import Splatalogue
lines = Splatalogue.query_lines(
    min_frequency=1*u.GHz, max_frequency=10*u.GHz,
    chemical_name='CO'
)
```

### heasarc — 高能天文档案
```python
from astroquery.heasarc import Heasarc
result = Heasarc.query_object("M1", mission='chanmaster')
```

### skyview — 多波段天空图像
```python
from astroquery.skyview import SkyView
images = SkyView.get_images(position='M1', survey=['DSS'])
```

### atomic — 原子光谱线
```python
from astroquery.atomic import AtomicLineList
lines = AtomicLineList.query_object(wavelength_range='6000 7000', wavelength_type='Air')
```

### svo_fps — 滤光片透过率
```python
from astroquery.svo_fps import SvoFps
filters = SvoFps.get_filter_list('2MASS')
```
