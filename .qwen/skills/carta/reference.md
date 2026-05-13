# CARTA API 参考

> API 处于实验阶段，可能会变更。详见 [carta-python 文档](https://carta-python.readthedocs.io/en/latest/)。

## Session — 会话管理

`Session` 类管理与 CARTA 前端的连接。

### 连接与生命周期

| 方法 | 参数 | 说明 |
|------|------|------|
| `Session(url)` | `url: str` — CARTA 后端地址，如 `"localhost:1234"` | 创建会话实例 |
| `.connect()` | 无 | 建立与 CARTA 后端的 HTTP 连接 |
| `.close()` | 无 | 关闭连接 |
| `.set_user_preferences(prefs)` | `prefs: dict` — 偏好设置字典 | 设置用户偏好 |

### 图像操作

| 方法 | 参数 | 说明 |
|------|------|------|
| `.open_image(path, hdu=0)` | `path: str` — 文件路径，`hdu: int` — HDU 索引 | 打开图像，返回 `Image` 对象 |
| `.append_image(path)` | `path: str` | 追加打开图像（不关闭已有图像） |
| `.close_image(image)` | `image: Image` | 关闭指定图像 |
| `.get_images()` | 无 | 返回当前打开的图像列表 |

### 目录操作

| 方法 | 参数 | 说明 |
|------|------|------|
| `.open_catalog_file(path, file_type)` | `path: str`, `file_type: int` | 打开目录文件 |
| `.load_votable(path)` | `path: str` | 加载 VOTable 目录 |
| `.load_catalog(path)` | `path: str` | 加载 CSV/TSV/FITS 目录 |

## Image — 图像操作

`Image` 类代表 CARTA 前端打开的图像。

### 基本属性

| 属性/方法 | 说明 |
|-----------|------|
| `.file_info` | 获取文件信息（维度、坐标系、频率等） |
| `.name` | 图像名称 |
| `.shape` | 数据维度 |

### 渲染控制

| 方法 | 参数 | 说明 |
|------|------|------|
| `.set_colormap(name)` | `name: str` — 如 `"viridis"`, `"jet"`, `"hot"` | 设置颜色映射表 |
| `.set_scaling(scaling)` | `scaling: str` — `"linear"`, `"log"`, `"sqrt"`, `"square"`, `"gamma"` | 设置缩放函数 |
| `.set_value_range(min, max)` | `min, max: float` | 设置显示值范围 |
| `.set_bias_contrast(bias, contrast)` | `bias, contrast: float` | 设置偏压和对比度 |
| `.set_nan_color(color)` | `color: str` — 如 `"#000000"` | 设置 NaN 像素颜色 |

### 等值线

| 方法 | 参数 | 说明 |
|------|------|------|
| `.set_contours(enabled, levels, color)` | `enabled: bool`, `levels: list[float]`, `color: str` | 设置等值线显示 |

### 矢量场（偏振）

| 方法 | 参数 | 说明 |
|------|------|------|
| `.set_vector_overlay(intensity, angle, threshold)` | `intensity: Image`, `angle: Image`, `threshold: float` | 设置矢量场叠加 |

### 剖面提取

| 方法 | 参数 | 说明 |
|------|------|------|
| `.get_spatial_profile(start, end)` | `start, end: tuple(x,y)` | 沿空间路径提取剖面 |
| `.get_spectral_profile(region, stokes)` | `region: Region`, `stokes: str` — 如 `"I"`, `"Q"` | 提取区域平均光谱 |
| `.get_stats(region)` | `region: Region` | 获取区域统计信息 |

### 矩图与 PV 图

| 方法 | 参数 | 说明 |
|------|------|------|
| `.get_moment_map(moment, range)` | `moment: int` — 0/1/2 等，`range: tuple(lo, hi)` | 生成矩图 |
| `.get_pv_slice(start, end, width)` | `start, end: tuple(x,y)`, `width: int` | 提取 PV 切片 |

### 导出

| 方法 | 参数 | 说明 |
|------|------|------|
| `.export_image(path, format)` | `path: str`, `format: str` — `"png"`, `"jpeg"` | 导出当前视图 |
| `.export_data(path, format)` | `path: str`, `format: str` | 导出数据 |

## Region — 区域操作

`Region` 类代表图像上的感兴趣区域。

### 创建区域

| 方法 | 参数 | 说明 |
|------|------|------|
| `.create_point(x, y)` | `x, y: float` | 创建点区域 |
| `.create_rect(x, y, w, h)` | `x, y, w, h: float` | 创建矩形区域 |
| `.create_ellipse(x, y, r1, r2)` | `x, y, r1, r2: float` | 创建椭圆区域 |
| `.create_polygon(vertices)` | `vertices: list[tuple]` | 创建多边形区域 |
| `.create_line(start, end)` | `start, end: tuple(x,y)` | 创建线段区域 |

### 区域操作

| 方法 | 参数 | 说明 |
|------|------|------|
| `.set_region(region)` | `region: dict` | 设置区域参数 |
| `.delete_region()` | 无 | 删除区域 |
| `.import_regions(path)` | `path: str` — .crtf/.reg 文件 | 导入区域文件 |
| `.export_regions(path, format)` | `path: str`, `format: str` | 导出区域文件 |

## 数据查询

### SIMBAD 查询

| 方法 | 参数 | 说明 |
|------|------|------|
| `.query_simbad(object_name)` | `object_name: str` — 如 `"Cas A"` | 查询天体信息并叠加 |

### VizieR 查询

| 方法 | 参数 | 说明 |
|------|------|------|
| `.query_vizier(catalog, ra, dec, radius)` | `catalog: str`, `ra, dec, radius: float` | 查询星表并叠加 |

### HiPS2FITS 查询

| 方法 | 参数 | 说明 |
|------|------|------|
| `.query_hips(hips_id, ra, dec, fov)` | `hips_id: str`, `ra, dec, fov: float` | 查询 HiPS 图像并加载 |

### 谱线查询

| 方法 | 参数 | 说明 |
|------|------|------|
| `.query_splatalogue(freq_range)` | `freq_range: tuple(lo, hi)` — 频率范围 (MHz) | 查询谱线数据库并叠加 |

## 偏好设置

```python
# CARTA 全局偏好（通过 Session 设置）
{
    "WCS": {
        "wcsType": 0,           # 0=自动, 1=像素, 2=WCS
        "systemType": "FK5",    # 坐标系
        "equinox": "J2000"      # 历元
    },
    "Region": {
        "color": "#2EE6D6",     # 区域颜色
        "lineWidth": 2,         # 线宽
        "dashLength": 5         # 虚线长度
    },
    "Contour": {
        "color": "#FFFFFF",     # 等值线颜色
        "thickness": 1,         # 线宽
        "dashLength": 0         # 虚线长度
    }
}
```
