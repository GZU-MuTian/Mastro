# PyVO API 参考速查

> 遇到复杂任务时，请参考 [PyVO 官方文档](https://pyvo.readthedocs.io/en/latest/) 获取完整 API。

---

## 1. pyvo.dal.TAPService — 表访问协议 (TAP)

| 功能 | API |
|------|-----|
| 创建服务 | `vo.dal.TAPService("url")` |
| 同步查询 | `tap.search(adql, maxrec=N)` |
| 异步查询（一步） | `tap.run_async(adql)` |
| 异步作业（分步） | `job = tap.submit_job(adql)` → `job.run()` → `job.wait()` → `job.fetch_result()` |
| 查询限制 | `tap.maxrec`, `tap.hardlimit` |
| 作业属性 | `job.phase`, `job.executionduration`, `job.destruction`, `job.error` |
| 上下文管理器 | `with tap.submit_job(adql) as job:` (退出时自动删除) |
| 轮询超时 | `pyvo.dal.tap.DEFAULT_JOB_POLL_TIMEOUT = 30` |
| 上传表 | `tap.search(adql, uploads={"name": table_or_path_or_url})` |

**作业生命周期**：PENDING → QUEUED → EXECUTING → COMPLETED / ERROR / ABORTED

**文档**：https://pyvo.readthedocs.io/en/latest/dal/tap.html

---

## 2. pyvo.dal.SIAService — 简单图像访问 (SIA)

| 功能 | API |
|------|-----|
| 创建服务 | `vo.dal.SIAService("url")` |
| 搜索图像 | `sia.search(pos=, size=, format=, intersect=, verbosity=)` |
| 格式过滤 | `format='image/fits'`, `'graphics'`, `'metadata'`, `'all'` |
| 覆盖关系 | `intersect='OVERLAPS'`(默认), `'COVERS'`, `'ENCLOSED'`, `'CENTER'` |
| 详细度 | `verbosity=1`(最少), `2`(常用), `3`(全部) |
| SIAv2 附加 | `data_type='image'`, `calib_level=2` |
| 获取 URL | `record.getdataurl()` |
| 获取数据 | `record.getdataset()` |
| Datalink | `record.getdatalink()` |

**文档**：https://pyvo.readthedocs.io/en/latest/dal/sia.html

---

## 3. pyvo.dal.SSAService — 简单光谱访问 (SSA)

| 功能 | API |
|------|-----|
| 创建服务 | `vo.dal.SSAService("url")` |
| 搜索光谱 | `ssa.search(pos=, diameter=, band=, time=)` |
| 波段约束 | `band=(1e-7, 5e-7) * u.m` |
| 时间约束 | `time=Time((53000, 54000), format='mjd')` |

**SSA vs SIA**：SSA 搜索圆形（`diameter`），支持 `band`/`time`；SIA 搜索矩形（`size`），无波段/时间约束。

**文档**：https://pyvo.readthedocs.io/en/latest/dal/ssa.html

---

## 4. pyvo.dal.SCSService — 简单锥形搜索 (SCS)

| 功能 | API |
|------|-----|
| 创建服务 | `vo.dal.SCSService("url")` |
| 锥形搜索 | `scs.search(pos=, radius=, verbosity=)` |

**文档**：https://pyvo.readthedocs.io/en/latest/dal/scs.html

---

## 5. pyvo.dal.SLAService — 简单谱线访问 (SLAP)

| 功能 | API |
|------|-----|
| 创建服务 | `vo.dal.SLAService("url")` |
| 搜索谱线 | `sla.search(wavelength=)`（仅波长，不需要位置） |

**文档**：https://pyvo.readthedocs.io/en/latest/dal/slap.html

---

## 6. pyvo.registry — VO 注册表查询

### 约束条件

| 约束 | 关键字参数 | 说明 |
|------|-----------|------|
| `Freetext` | `keywords` | 标题/描述/主题文本匹配 |
| `Servicetype` | `servicetype` | tap, ssa, sia1, sia2, conesearch |
| `UCD` | `ucd` | 列 UCD 模式（如 `phot.mag`） |
| `UAT` | `uat` | 天文词汇（支持 `expand_down` 层级展开） |
| `Waveband` | `waveband` | Radio, Millimeter, IR, Optical, UV, EUV, X-ray, Gamma-ray |
| `Author` | `author` | 作者（支持 SQL 通配符 `%`） |
| `Datamodel` | `datamodel` | obscore, epntap, regtap |
| `Ivoid` | `ivoid` | IVOA 标识符精确匹配 |
| `Spatial` | — | 空间位置约束（RegTAP 1.2） |
| `Spectral` | — | 光谱覆盖约束（RegTAP 1.2） |
| `Temporal` | — | 时间覆盖约束（RegTAP 1.2） |

多个约束之间为**逻辑与**关系。

### 查询与结果

| 功能 | API |
|------|-----|
| 搜索 | `registry.search(constraint1, constraint2, ...)` 或 `registry.search(keywords=, waveband=, ...)` |
| 结果转表 | `resources.to_table()` |
| 获取资源 | `res = resources[0]` 或 `resources["short_name"]` |
| 获取服务 | `res.service`（需指定 `servicetype`） |
| 获取接口 | `res.list_interfaces()` |
| 资源详情 | `res.access_modes()`, `res.get_contact()`, `res.describe(verbose=True)` |
| 表元数据 | `res.get_tables()` |

### 配置

| 功能 | API |
|------|-----|
| 生成 ADQL（不执行） | `registry.get_RegTAP_query(constraint1, ...)` |
| 切换注册表 | `registry.choose_RegTAP_service("url")` |
| 环境变量 | `export IVOA_REGISTRY="url"` |

**文档**：https://pyvo.readthedocs.io/en/latest/registry/index.html

---

## 7. pyvo.discover — 跨档案全局发现

| 功能 | API |
|------|-----|
| 全局搜索图像 | `discover.images_globally(space=(ra, dec, deg), spectrum=, time=, timeout=, inclusive=, watcher=)` |
| 空间约束 | `space=(273.5, -12.1, 0.1)` — (RA, Dec, 半径)，单位：度 |
| 光谱约束 | `spectrum=1 * u.nm` |
| 时间约束 | `time=(Time('1995-01-01'), Time('1995-12-31'))` |
| 超时 | `timeout=10`（默认 20 秒） |
| 包含未声明 | `inclusive=True`（更慢但更全面） |
| 进度监视 | `watcher=callback_fn`，签名为 `fn(disco, msg)` |
| 返回值 | `(datasets, log)` — datasets 为 ImageFound 列表，log 为日志 |
| 高级控制 | `discover.image.ImageDiscoverer(space=, time=)` → `.set_services()` → `.query_services()` |

**文档**：https://pyvo.readthedocs.io/en/latest/discover/index.html

---

## 8. pyvo.samp — SAMP 应用间通信

| 功能 | API |
|------|-----|
| 建立连接 | `with pyvo.samp.connection(client_name=) as conn:` |
| 发送表格 | `pyvo.samp.send_table_to(conn, table, name=, client_name=)` |
| 发送图像 | `pyvo.samp.send_image_to(conn, url, name=)` |
| 发送光谱 | `pyvo.samp.send_spectrum_to(conn, url, name=)` |
| 通用发送 | `pyvo.samp.send_product_to(conn, url, mtype=, name=)` |
| 查找客户端 | `pyvo.samp.find_client_id(conn, "topcat")` |
| 发布表格 URL | `pyvo.samp.accessible_table(conn, table)` |

**文档**：https://pyvo.readthedocs.io/en/latest/samp.html

---

## 9. pyvo.mivot — VOTable 数据模型注解

> **原型特性**：需 `activate_features("MIVOT")`，需 Astropy >= 6.0

| 功能 | API |
|------|-----|
| 激活 | `from pyvo.utils.prototype import activate_features; activate_features("MIVOT")` |
| 创建查看器 | `MivotViewer(result, resolve_ref=True)` |
| 遍历行 | `m_viewer.next_row_view()` |
| 访问实例 | `m_viewer.dm_instances[0]`, `m_viewer.dm_instance` |
| 坐标构建 | `SkyCoordBuilder(mango_property).build_sky_coord()` |
| 打印注解 | `XmlUtils.pretty_print(m_viewer._mapping_block)` |

**文档**：https://pyvo.readthedocs.io/en/latest/mivot/index.html

---

## 10. 结果集通用接口

所有 DAL 服务的 `search()` 返回相同接口：

| 方法/属性 | 说明 |
|-----------|------|
| `result.fieldnames` | 列名元组 |
| `result.to_table()` / `result.to_qtable()` | 转为 `astropy.table.Table` / `QTable` |
| `result.fieldname_with_ucd('phot.mag')` | 按 UCD 查找列名 |
| `result.fieldname_with_utype('obscore:...')` | 按 utype 查找列名 |
| `result['col']` / `result[0]` / `result['col', 0]` | 整列/单行/单值 |
| `result.votable` | 底层 VOTableFile |

---

## 11. 认证 (pyvo.auth)

| 功能 | API |
|------|-----|
| 凭据存储 | `store = pyvo.auth.CredentialStore()` |
| 设置凭据 | `store.set_login("service", "user", "pass")` |
| 获取会话 | `session = store.get_session("service")` |
| 直接认证 | `auth = pyvo.auth.AuthSession(); auth.credentials.set_login(...)` |
| 使用会话 | `TAPService("url", session=auth)` |

---

## 12. 异常类

| 异常 | 说明 |
|------|------|
| `DALQueryError` | ADQL 查询语法或语义错误 |
| `DALServiceError` | 服务通信失败 |
| `DALFormatError` | 响应格式错误 |
| `DALOverflowWarning` | 结果被截断（`e.result` 仍可访问部分结果） |
| `DALRateLimitError` | HTTP 429 限速 |

---

## 13. 辅助函数

| 函数 | 等价于 |
|------|--------|
| `pyvo.dal.imagesearch(url, pos, size)` | `SIAService(url).search(pos, size)` |
| `pyvo.dal.spectrumsearch(url, pos, diameter)` | `SSAService(url).search(pos, diameter)` |
| `pyvo.dal.conesearch(url, pos, radius)` | `SCSService(url).search(pos, radius)` |
| `pyvo.dal.tablesearch(url, query)` | `TAPService(url).search(query)` |
| `pyvo.dal.linesearch(url, wavelength)` | `SLAService(url).search(wavelength)` |

---

## 14. 常用 TAP 服务 URL

| 服务 | URL |
|------|-----|
| GAVO DC | `http://dc.g-vo.org/tap` |
| Gaia (ESA) | `https://gea.esac.esa.int/tap-server/tap` |
| MAST | `https://mast.stsci.edu/api/v0.1/` |
| ESO | `http://archive.eso.org/tap_obs` |
| CADC | `https://www.cadc-ccda.hia-iha.nrc-cnrc.gc.ca/tap` |
| Simbad (CDS) | `https://simbad.u-strasbg.fr/simbad/sim-tap` |
| VizieR (CDS) | `https://tapvizier.cds.unistra.fr/TAPVizieR/tap` |
