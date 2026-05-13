# Astroquery API 参考速查

> 遇到复杂任务时，请参考 [astroquery 官方文档](https://astroquery.readthedocs.io/en/latest/) 获取完整 API。

---

## 1. astroquery.simbad — SIMBAD 天文数据库

| 功能 | API |
|------|-----|
| 按名称查询 | `Simbad.query_object("m1")`, `Simbad.query_object("M [1-9]", wildcard=True)` |
| 查询所有标识符 | `Simbad.query_objectids("Polaris")` |
| 区域查询 | `Simbad.query_region(coord, radius=0.5*u.degree)` |
| 批量区域查询 | `Simbad.query_region(coords_array, radius=radius_array)` |
| 目录查询 | `Simbad.query_catalog('ESO')` |
| 层次关系 | `Simbad.query_hierarchy("Mrk 116", hierarchy="children")` |
| ADQL 查询 | `Simbad.query_tap(adql_string)` |
| 自定义字段 | `simbad = Simbad(); simbad.add_votable_fields("otype", "mesplx")` |
| 行限制 | `Simbad.ROW_LIMIT = N` |

**文档**：https://astroquery.readthedocs.io/en/latest/simbad/simbad.html

---

## 2. astroquery.vizier — VizieR 星表服务

| 功能 | API |
|------|-----|
| 搜索目录 | `Vizier.find_catalogs('keyword')` |
| 下载目录 | `Vizier.get_catalogs("J/ApJ/788/39")` |
| 按名称查询 | `Vizier(row_limit=10).query_object("sirius")` |
| 区域查询 | `Vizier.query_region(coord, radius=, catalog=)` |
| 矩形区域 | `Vizier.query_region(coord, width="30m", catalog=[...])` |
| 列选择与过滤 | `Vizier(columns=[...], column_filters={"Vmag": ">10"})` |
| 目录元数据 | `Vizier(catalog="VII/74A").get_catalog_metadata()` |
| 行限制 | `Vizier.ROW_LIMIT = N`（`-1` 无限制） |

**文档**：https://astroquery.readthedocs.io/en/latest/vizier/vizier.html

---

## 3. astroquery.ipac.ned — NED 河外数据库

| 功能 | API |
|------|-----|
| 按名称查询 | `Ned.query_object("NGC 224")` |
| 区域查询 | `Ned.query_region(coord_or_name, radius=)` |
| 文献查询 | `Ned.query_refcode('1997A&A...323...31K')` |
| 数据表 | `Ned.get_table("3C 273", table='redshifts')`（positions/photometry/diameters/redshifts/references） |
| 下载图像 | `Ned.get_images("m1")`（返回 HDUList 列表） |
| 图像 URL | `Ned.get_image_list("m1")` |
| 下载光谱 | `Ned.get_spectra('3c 273')` |

**文档**：https://astroquery.readthedocs.io/en/latest/ipac/ned/ned.html

---

## 4. astroquery.mast — MAST 太空望远镜档案

| 功能 | API |
|------|-----|
| 按目标查询 | `Observations.query_object("M42", radius="0.2 deg")` |
| 条件查询 | `Observations.query_criteria(coordinates=, obs_collection="HST", dataproduct_type=)` |
| 解析名称 | `Mast().resolve_object("M101", resolver="NED")` |
| 星表查询 | `Catalogs.query_object("M10", radius=, catalog="Pan-STARRS")` |
| 获取数据产品 | `Observations.get_product_list(obs_table)` |
| 过滤产品 | `Observations.filter_products(products, productType=, extension=)` |
| 下载产品 | `Observations.download_products(products, download_dir=)` |
| 特定任务 | `MastMissions(mission="hst").query_criteria(target_name=, filters=)` |
| 认证 | `Observations.login(token="YOUR_MAST_TOKEN")` |

**文档**：https://astroquery.readthedocs.io/en/latest/mast/mast.html

---

## 5. astroquery.gaia — Gaia 天体测量数据

| 功能 | API |
|------|-----|
| 设置数据版本 | `Gaia.MAIN_GAIA_TABLE = "gaiadr3.gaia_source"` |
| 矩形搜索 | `Gaia.query_object_async(coordinate=, width=, height=)` |
| 锥形搜索 | `Gaia.cone_search_async(coord, radius=).get_results()` |
| ADQL 查询 | `Gaia.launch_job_async(adql).get_results()` |
| 保存到文件 | `Gaia.launch_job_async(adql, dump_to_file=True, output_format='csv')` |
| 探索表 | `Gaia.load_tables(only_names=True)` |
| 查看列 | `Gaia.load_table('gaiadr3.gaia_source').columns` |
| 额外数据 | `Gaia.load_data(ids=[...], data_release='Gaia DR3', retrieval_type='EPOCH_PHOTOMETRY')` |
| 行限制 | `Gaia.ROW_LIMIT = N`（`-1` 无限制） |

**文档**：https://astroquery.readthedocs.io/en/latest/gaia/gaia.html

---

## 6. astroquery.ipac.irsa — IRSA 红外档案

| 功能 | API |
|------|-----|
| 列出目录 | `Irsa.list_catalogs(filter='spitzer')` |
| 锥形搜索 | `Irsa.query_region(coordinates=, spatial='Cone', catalog=, radius=)` |
| 按名称搜索 | `Irsa.query_region("M81", catalog=, spatial="Cone", radius=)` |
| 框形搜索 | `Irsa.query_region(coordinates=, spatial='Box', catalog=, width=)` |
| 指定列 | `Irsa.query_region(..., columns="ra,dec,w1mpro")` |
| TAP 查询 | `Irsa.query_tap(adql).to_qtable()` |
| 图像查询 | `Irsa.query_sia(pos=(coord, radius), collection=)` |
| 行限制 | `Irsa.ROW_LIMIT = N` |

**文档**：https://astroquery.readthedocs.io/en/latest/ipac/irsa/irsa.html

---

## 7. astroquery.eso — ESO 科学档案

| 功能 | API |
|------|-----|
| 列出仪器 | `Eso().list_instruments()` |
| 查询仪器数据 | `eso.query_instrument('midi', column_filters={...}, columns=[...])` |
| 列出勘测 | `eso.list_surveys()` |
| 查询勘测数据 | `eso.query_surveys(surveys='HARPS', target_name=)` |
| 下载数据 | `eso.retrieve_data(dp_ids, destination=)` |
| 获取 FITS 头 | `eso.get_headers(dp_ids)` |
| 认证 | `eso.login(username=, store_password=True)` |

**文档**：https://astroquery.readthedocs.io/en/latest/eso/eso.html

---

## 8. astroquery.xmatch — 星表交叉匹配

| 功能 | API |
|------|-----|
| 本地表 vs 在线目录 | `XMatch.query(cat1=input_table, cat2='vizier:II/246/out', max_distance=5*u.arcsec, colRA1='ra', colDec1='dec')` |
| 两个在线目录 | `XMatch.query(cat1='vizier:I/345/gaia2', cat2='vizier:II/246/out', max_distance=1*u.arcsec)` |

**文档**：https://astroquery.readthedocs.io/en/latest/xmatch/xmatch.html

---

## 9. astroquery.nasa_ads — NASA ADS 文献查询

| 功能 | API |
|------|-----|
| 关键词搜索 | `ADS.query_simple("supernova remnant X-ray")` |
| 作者搜索 | `ADS.query_simple("author:Hubble galaxy redshift")` |

**文档**：https://astroquery.readthedocs.io/en/latest/nasa_ads/nasa_ads.html

---

## 10. astroquery.jplhorizons — JPL 太阳系天体历表

| 功能 | API |
|------|-----|
| 查询天体 | `Horizons(id='Ceres', location='500', epochs=2459000.5)` |
| 星历 | `obj.ephemerids()`（位置、亮度等） |
| 状态向量 | `obj.vectors()` |
| 指定观测站 | `Horizons(id='Ceres', location='G37', epochs=...)` |
| 时间范围 | `Horizons(id='1P', epochs={'start':'2024-01-01', 'stop':'2024-12-31', 'step':'1d'})` |

**文档**：https://astroquery.readthedocs.io/en/latest/jplhorizons/jplhorizons.html

---

## 11. 常用辅助模块

| 模块 | 功能 | API |
|------|------|-----|
| `splatalogue` | 射电分子谱线 | `Splatalogue.query_lines(min_frequency=, max_frequency=, chemical_name=)` |
| `heasarc` | 高能天文档案 | `Heasarc.query_object("M1", mission='chanmaster')` |
| `skyview` | 多波段天空图像 | `SkyView.get_images(position='M1', survey=['DSS'])` |
| `atomic` | 原子光谱线 | `AtomicLineList.query_object(wavelength_range='6000 7000', wavelength_type='Air')` |
| `svo_fps` | 滤光片透过率 | `SvoFps.get_filter_list('2MASS')` |

**文档**：各模块详见 [astroquery 官方文档](https://astroquery.readthedocs.io/en/latest/)

---

## 通用技巧

| 技巧 | 说明 |
|------|------|
| 清除缓存 | `Module.clear_cache()` |
| 控制行数 | `Module.ROW_LIMIT = N`（`-1` 返回全部） |
| 批量查询 | 使用数组坐标/名称列表，避免循环调用 |
| 异步查询 | 大数据集使用 `async_job=True` 或 `launch_job_async` |
| 返回类型 | 所有结果为 `astropy.table.Table` |
