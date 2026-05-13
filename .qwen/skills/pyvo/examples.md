# PyVO 代码示例

> 更多高级用法请参考 [PyVO 官方文档](https://pyvo.readthedocs.io/en/latest/)。

---

## 1. TAP 表访问协议

```python
import pyvo as vo
from astropy.coordinates import SkyCoord
import astropy.units as u

# 连接 TAP 服务
tap = vo.dal.TAPService("https://dc.zah.uni-heidelberg.de/tap")

# 同步查询
result = tap.search("SELECT TOP 10 * FROM ivoa.obscore")

# 查询限制
print(f"maxrec: {tap.maxrec}, hardlimit: {tap.hardlimit}")
result = tap.search(query, maxrec=10000)

# 异步查询（一步）
result = tap.run_async("SELECT * FROM large_table WHERE ...")

# 异步作业（分步控制）
job = tap.submit_job("SELECT * FROM huge_table")
job.executionduration = 700   # 设置执行时间限制（秒）
job.run()
job.phase                     # 'PENDING' → 'QUEUED' → 'EXECUTING' → 'COMPLETED'
job.wait()
job.raise_if_error()
result = job.fetch_result()
job.delete()                  # 清理作业

# 上下文管理器（退出时自动删除作业）
with tap.submit_job("SELECT * FROM ivoa.obscore") as job:
    job.run()
    result = job.fetch_result()

# 调整轮询超时
import pyvo.dal.tap
pyvo.dal.tap.DEFAULT_JOB_POLL_TIMEOUT = 30  # 秒

# 上传本地表进行查询（TAP 1.1+）
result = tap.search(query, uploads={"my_table": "/path/to/data.csv"})
result = tap.search(query, uploads={"my_table": my_table})
result = tap.search(query, uploads={"my_table": "https://example.com/data.csv"})
```

---

## 2. SIA 简单图像访问

```python
import pyvo as vo
from astropy.coordinates import SkyCoord
from astropy import units as u

sia = vo.dal.SIAService("http://dc.g-vo.org/hppunion/q/im/siap.xml")

pos = SkyCoord.from_name('NGC 4993')
size = u.Quantity(0.5, unit="deg")

# 基本搜索
results = sia.search(pos=pos, size=size)

# 按格式过滤
results = sia.search(pos=pos, size=size, format='image/fits')

# 按空间覆盖关系过滤
results = sia.search(pos=pos, size=size, intersect='covers')  # COVERS, ENCLOSED, OVERLAPS, CENTER

# 仅获取元数据（不下载图像）
meta = sia.search(pos=pos, size=size, format='metadata')

# 详细度控制（1=最少列, 2=常用列, 3=全部列）
results = sia.search(pos=pos, size=size, verbosity=3)

# SIAv2 附加参数
results = sia.search(pos=pos, size=size, data_type='image', calib_level=2)

# 获取图像 URL
for record in results:
    print(record.acref)
    datalink = record.getdatalink()
```

---

## 3. SSA 简单光谱访问

```python
import pyvo as vo
from astropy.coordinates import SkyCoord
from astropy.time import Time
from astropy import units as u

ssa = vo.dal.SSAService("http://archive.stsci.edu/ssap/search2.php?id=BEFS&")

pos = SkyCoord.from_name('Vega')

# 基本搜索
results = ssa.search(pos=pos, diameter=u.Quantity(0.01, unit="deg"))

# 附加时间约束
results = ssa.search(
    pos=pos,
    diameter=u.Quantity(0.01, unit="deg"),
    time=Time((53000, 54000), format='mjd')
)

# 附加波段约束
results = ssa.search(
    pos=pos,
    diameter=u.Quantity(0.01, unit="deg"),
    band=u.Quantity((1e-7, 5e-7), unit="m")
)

# 获取光谱 URL
for record in results:
    print(record.acref)
```

---

## 4. SCS 简单锥形搜索

```python
import pyvo as vo
from astropy.coordinates import SkyCoord
import astropy.units as u

scs = vo.dal.SCSService('http://dc.g-vo.org/arihip/q/cone/scs.xml')

pos = SkyCoord(ra=10.68, dec=41.27, unit='deg')
results = scs.search(pos=pos, radius=u.Quantity(0.1, unit="deg"), verbosity=3)

table = results.to_table()
print(results.fieldnames)
```

---

## 5. SLAP 简单谱线访问

```python
import pyvo as vo
from astropy import units as u

slap = vo.dal.SLAService("http://some.line.service/slap")
results = slap.search(wavelength=u.Quantity((1e-10, 1e-9), unit="m"))
table = results.to_table()
```

---

## 6. Registry 注册表查询

```python
from pyvo import registry
from astropy.coordinates import SkyCoord
import astropy.units as u

# 服务发现
for res in registry.search(waveband="infrared", servicetype="ssa"):
    result = res.service.search(pos=SkyCoord.from_name("Bellatrix"), size=0.001)
    print(f"{res.res_title}: {len(result)} 条记录")

# 数据发现
resources = registry.search(keywords="white dwarf", waveband="UV")
resources = registry.search(registry.UCD("src.redshift"))
resources = registry.search(registry.UAT("cepheid-variable-stars", expand_down=3))
resources = registry.search(author="%Miller%")

# 组合多个约束
resources = registry.search(
    registry.Freetext("supernova remnant"),
    registry.Waveband("X-ray"),
    registry.Servicetype("tap")
)

# 空间搜索
resources = registry.search(
    registry.Freetext("Wolf-Rayet"),
    registry.Spatial((SkyCoord("23d +3d"), 180*u.arcmin), intersect="enclosed")
)

# 结果处理
resources.to_table()  # 转为 astropy Table
res = resources[0]
res.describe(verbose=True)
tap_service = res.service
result = tap_service.run_sync("SELECT TOP 5 * FROM ivoa.obscore")

# 资源详情
res.access_modes()            # 可用访问模式
res.get_contact()             # 维护者联系信息
tables = res.get_tables()     # 表元数据

# 生成 ADQL（不执行）
adql = registry.get_RegTAP_query(
    registry.Freetext("Gaia"), registry.Servicetype("tap")
)
print(adql)

# 切换注册表
registry.choose_RegTAP_service("https://reg.g-vo.org/tap")
```

---

## 7. 跨档案全局发现

```python
from pyvo import discover, registry
from astropy import units as u
from astropy.time import Time
import datetime

# 全局搜索图像
datasets, log = discover.images_globally(
    space=(273.5, -12.1, 0.1),           # (RA, Dec, 半径)，单位：度
    spectrum=1 * u.nm,                    # 波长约束
    time=(Time('1995-01-01'), Time('1995-12-31'))  # 时间范围
)
print(f"找到 {len(datasets)} 个数据集")

# 进度监视
def watch(disco, msg):
    print(datetime.datetime.now(), msg)

found, log = discover.images_globally(space=(3, 1, 0.2), watcher=watch)

# 超时控制（默认 20 秒）
found, log = discover.images_globally(space=(3, 1, 0.2), timeout=10)

# 包含未声明覆盖范围的服务（更慢但更全面）
found, log = discover.images_globally(space=(3, 1, 0.2), inclusive=True)

# 高级控制：手动设置服务
im = discover.image.ImageDiscoverer(
    space=(274.6880, -13.7920, 0.1),
    time=(Time('1996-10-04'), Time('1996-10-10'))
)
im.set_services(registry.search(keywords=["heasarc rass"]))
im.query_services()
print(im.results)
```

---

## 8. SAMP 应用间通信

```python
import pyvo

# 建立 SAMP 连接
with pyvo.samp.connection(client_name="my_script") as conn:
    # 发送表格到 TOPCAT
    pyvo.samp.send_table_to(conn, my_table, name="my-results", client_name="topcat")

    # 发送图像到 Aladin
    pyvo.samp.send_image_to(conn, image_url, name="my-image", client_name="aladin")

    # 发送光谱
    pyvo.samp.send_spectrum_to(conn, spectrum_url, name="my-spectrum")

    # 广播给所有客户端
    pyvo.samp.send_table_to(conn, my_table, name="broadcast-table")

    # 查找客户端 ID
    client_id = pyvo.samp.find_client_id(conn, "topcat")

    # 发布表格为临时 URL
    url = pyvo.samp.accessible_table(conn, my_table)
```

---

## 9. MIVOT 数据模型注解

```python
# 激活原型特性
from pyvo.utils.prototype import activate_features
activate_features("MIVOT")
```

### 读取带注解的光度数据

```python
from pyvo.dal import TAPService
from pyvo.mivot.utils.xml_utils import XmlUtils
from pyvo.mivot.viewer.mivot_viewer import MivotViewer

service = TAPService('https://xcatdb.unistra.fr/xtapdb')
result = service.run_sync(
    'SELECT TOP 5 * FROM "public".mergedentry',
    format="application/x-votable+xml;content=mivot"
)

m_viewer = MivotViewer(result, resolve_ref=True)
XmlUtils.pretty_print(m_viewer._mapping_block)

mango_object = m_viewer.dm_instances[0]
while m_viewer.next_row_view():
    if mango_object.dmtype == "mango:MangoObject":
        print(f"Source: {mango_object.identifier.value}")
        for prop in mango_object.propertyDock:
            if prop.dmtype == "mango:Brightness" and prop.value.value:
                print(f"  {prop.photCal.identifier.value}: "
                      f"{prop.value.value:.2e} ± {prop.error.sigma.value:.2e}")
```

### 读取带注解的坐标数据

```python
from pyvo.dal.scs import SCSService
from pyvo.mivot.viewer.mivot_viewer import MivotViewer
from pyvo.mivot.features.sky_coord_builder import SkyCoordBuilder

scs_srv = SCSService("https://vizier.cds.unistra.fr/viz-bin/conesearch/V1.5/I/239/hip_main")
query_result = scs_srv.search(
    pos=SkyCoord(ra=52.26708*u.degree, dec=59.94027*u.degree, frame='icrs'),
    radius=0.5
)

m_viewer = MivotViewer(query_result, resolve_ref=True)
while m_viewer.next_row_view():
    if m_viewer.dm_instance.dmtype == "mango:EpochPosition":
        scb = SkyCoordBuilder(m_viewer.dm_instance)
        print(scb.build_sky_coord())
```

---

## 10. 通用技巧

### 认证访问

```python
import pyvo.auth

# 方式一：凭据存储
store = pyvo.auth.CredentialStore()
store.set_login("my-service", "username", "password")
session = store.get_session("my-service")
tap = vo.dal.TAPService("https://protected.archive.org/tap", session=session)

# 方式二：直接认证
auth = pyvo.auth.AuthSession()
auth.credentials.set_login("username", password="password")
tap = vo.dal.TAPService("https://protected.archive.org/tap", session=auth)
```

### 结果处理

```python
# 转换
table = result.to_table()
qtable = result.to_qtable()
df = result.to_table().to_pandas()

# 访问
print(result.fieldnames)
for row in result:
    print(row['ra'], row['dec'])
first_10 = result[:10]
```

### 稳健的跨档案查询

```python
from astropy.table import vstack
from pyvo import registry

results = []
for svc_rec in registry.search(datamodel="obscore", servicetype="tap"):
    try:
        result = svc_rec.service.run_sync("SELECT TOP 1 * FROM ivoa.obscore")
        results.append(result.to_table())
    except KeyboardInterrupt:
        raise
    except Exception as e:
        print(f"服务 {svc_rec.ivoid} 失败: {e}")
if results:
    final_table = vstack(results)
```

### 辅助函数

```python
from pyvo.dal import imagesearch, spectrumsearch, linesearch, conesearch, tablesearch

results = imagesearch("http://dc.g-vo.org/sia.xml", pos=(257.41, 64.345), size=0.25)
results = spectrumsearch("http://dc.g-vo.org/ssap", pos=(257.41, 64.345), diameter=0.25)
results = conesearch("http://dc.g-vo.org/scs", pos=(257.41, 64.345), radius=0.25)
results = tablesearch("http://dc.g-vo.org/tap", "SELECT TOP 5 * FROM ivoa.obscore")
results = linesearch("http://dc.g-vo.org/slap", wavelength=(1e-10, 1e-9))
```

### 原型特性激活

```python
from pyvo.utils.prototype import activate_features
activate_features("MIVOT")     # MIVOT 注解
activate_features("TableOps")  # TAP 表操作（create_table, load_table 等）
```
