# Astropy API 参考速查

> 遇到复杂任务时，请参考 [astropy 官方文档](https://docs.astropy.org/en/stable/) 获取完整 API。

---

## 1. astropy.units — 物理单位

| 功能 | API |
|------|-----|
| 创建 Quantity | `value * u.unit`（如 `4.2 * u.lightyear`） |
| 单位转换 | `q.to(target_unit)` |
| 等价转换 | `q.to(unit, equivalencies=u.spectral())`（波长↔频率） |
| 获取数值/单位 | `q.value`, `q.unit` |
| 分解单位 | `q.decompose()`, `q.si`, `q.cgs` |

**常用单位**：`u.m`, `u.km`, `u.pc`, `u.kpc`, `u.Mpc`, `u.lightyear`, `u.AU`, `u.deg`, `u.rad`, `u.arcsec`, `u.Jy`, `u.mJy`, `u.s`, `u.year`, `u.kg`, `u.eV`, `u.keV`

**文档**：https://docs.astropy.org/en/stable/units/index.html

---

## 2. astropy.coordinates — 天球坐标

| 功能 | API |
|------|-----|
| 创建坐标 | `SkyCoord(ra=, dec=, frame='icrs')`, `SkyCoord('00h42m44.33s +41d16m07.5s')` |
| 银道坐标 | `SkyCoord(l=, b=, frame='galactic')` |
| 坐标转换 | `c.galactic`, `c.transform_to('fk5')` |
| 三维坐标 | `SkyCoord(ra=, dec=, distance=)` |
| 角距计算 | `c1.separation(c2)`, `c1.separation_3d(c2)` |
| 名称解析 | `SkyCoord.from_name('M31')` |
| 数组坐标 | `SkyCoord(ra=[...]*u.degree, dec=[...]*u.degree)` |

**文档**：https://docs.astropy.org/en/stable/coordinates/index.html

---

## 3. astropy.io.fits — FITS 文件

| 功能 | API |
|------|-----|
| 打开文件 | `fits.open('file.fits')` → HDUList |
| 读取数据/头 | `hdul[n].data`, `hdul[n].header` |
| 便捷读取 | `fits.getdata('file.fits')`, `fits.getheader('file.fits')` |
| 内存映射 | `fits.open('file.fits', memmap=True)` |
| 写入图像 | `fits.PrimaryHDU(data).writeto('out.fits', overwrite=True)` |
| 写入表 | `fits.BinTableHDU.from_columns([col1, col2]).writeto(...)` |
| 更新文件 | `fits.open('file.fits', mode='update')` → `hdul.flush()` |
| 列定义 | `fits.Column(name=, format=, array=)` |

**命令行工具**：`fitsinfo`, `fitsheader`, `fitscheck`, `fitsdiff`

**文档**：https://docs.astropy.org/en/stable/io/fits/index.html

---

## 4. astropy.table — 表格数据

| 功能 | API |
|------|-----|
| 创建 | `Table()`, `QTable()`（QTable 支持 Quantity 列） |
| 访问 | `t['col']`, `t[0]`, `t[0]['col']`, `t[t['col'] > 2]` |
| 列操作 | `t['new'] = vals`, `del t['col']`, `t.rename_column(old, new)` |
| 添加行 | `t.add_row({...})` |
| 表连接 | `join(t1, t2, keys='name')` |
| 纵向拼接 | `vstack([t1, t2])` |
| 分组 | `t.group_by('col')` |
| 读写 | `Table.read('file')`, `t.write('file', format=, overwrite=True)` |
| Pandas 互转 | `t.to_pandas()`, `Table.from_pandas(df)` |

**文档**：https://docs.astropy.org/en/stable/table/index.html

---

## 5. astropy.time — 时间系统

| 功能 | API |
|------|-----|
| 创建时间 | `Time('2024-01-15T12:30:00', scale='utc')`, `Time(59000.0, format='mjd')` |
| 当前时间 | `Time.now()` |
| 格式转换 | `t.iso`, `t.jd`, `t.mjd`, `t.datetime` |
| 尺度转换 | `t.tai`, `t.tt`, `t.tdb` |
| 时间算术 | `t + 3*u.day`, `t2 - t1`（返回 TimeDelta） |

**文档**：https://docs.astropy.org/en/stable/time/index.html

---

## 6. astropy.cosmology — 宇宙学

| 功能 | API |
|------|-----|
| 预定义模型 | `Planck18`, `WMAP9`, `FlatLambdaCDM(H0=, Om0=)` |
| 光度距离 | `cosmo.luminosity_distance(z)` |
| 角直径距离 | `cosmo.angular_diameter_distance(z)` |
| 共动距离 | `cosmo.comoving_distance(z)` |
| 宇宙年龄 | `cosmo.age(z)` |
| 回顾时间 | `cosmo.lookback_time(z)` |
| 距离模数 | `cosmo.distmod(z)` |
| 共动体积 | `cosmo.comoving_volume(z)` |

**文档**：https://docs.astropy.org/en/stable/cosmology/index.html

---

## 7. astropy.wcs — 世界坐标系统

| 功能 | API |
|------|-----|
| 从头加载 | `WCS(header)` |
| 像素→天球 | `wcs.pixel_to_world(x, y)` → SkyCoord |
| 天球→像素 | `wcs.world_to_pixel(skycoord)` |
| Matplotlib 投影 | `plt.subplot(projection=wcs)` |

**文档**：https://docs.astropy.org/en/stable/wcs/index.html

---

## 8. astropy.modeling — 模型拟合

| 功能 | API |
|------|-----|
| 预定义模型 | `models.Gaussian1D(amplitude=, mean=, stddev=)` |
| 多项式 | `models.Polynomial1D(degree=, c0=, c1=, ...)` |
| 黑体 | `models.BlackBody(temperature=)` |
| 2D 高斯 | `models.Gaussian2D(amplitude=, x_mean=, y_mean=)` |
| 模型组合 | `model1 + model2`, `model1 * model2` |
| 拟合器 | `fitting.LevMarLSQFitter()`, `fitting.TRFLSQFitter()` |
| 执行拟合 | `fitter(model, x, y, weights=)` |
| 评估模型 | `fitted_model(x)` |

**文档**：https://docs.astropy.org/en/stable/modeling/index.html

---

## 9. astropy.stats — 统计工具

| 功能 | API |
|------|-----|
| Sigma clipping | `sigma_clip(data, sigma=3, maxiters=5)` |
| 便捷统计 | `sigma_clipped_stats(data, sigma=3.0)` → (mean, median, std) |
| 鲁棒均值 | `biweight_location(data)` |
| 鲁棒标准差 | `biweight_scale(data)` |
| σ ↔ FWHM | `gaussian_sigma_to_fwhm`（常量 2.3548） |

**文档**：https://docs.astropy.org/en/stable/stats/index.html

---

## 10. astropy.convolution — 卷积与核

| 功能 | API |
|------|-----|
| 卷积 | `convolve(image, kernel)`, `convolve_fft(image, kernel, boundary=)` |
| 高斯核 | `Gaussian2DKernel(x_stddev=)` |
| 方盒核 | `Box2DKernel(width=)` |
| 圆形核 | `Tophat2DKernel(radius=)` |
| 自定义核 | `CustomKernel(array=[...])` |

**文档**：https://docs.astropy.org/en/stable/convolution/index.html

---

## 11. astropy.nddata — N 维数据

| 功能 | API |
|------|-----|
| 创建 | `NDData(data, uncertainty=StdDevUncertainty(sigma), mask=mask)` |
| 算术运算 | `result = ndd1 + ndd2`（不确定性自动传播） |
| CCDData | `CCDData.read('file.fits', unit='adu')`, `ccd.write('out.fits')` |

**文档**：https://docs.astropy.org/en/stable/nddata/index.html

---

## 12. astropy.visualization — 可视化

| 功能 | API |
|------|-----|
| ZScale 拉伸 | `simple_norm(data, 'zscale')` |
| Log 拉伸 | `ImageNormalize(stretch=LogStretch())` |
| Asinh 拉伸 | `ImageNormalize(vmin=, vmax=, stretch=AsinhStretch())` |
| WCS 坐标轴 | `plt.subplot(projection=WCS(header))` |

**文档**：https://docs.astropy.org/en/stable/visualization/index.html

---

## 13. astropy.constants — 物理常数

**常用常数**：`c.c`（光速）, `c.G`（引力常数）, `c.M_sun`（太阳质量）, `c.R_sun`（太阳半径）, `c.k_B`（玻尔兹曼常数）, `c.h`（普朗克常数）, `c.m_p`（质子质量）, `c.sigma_sb`（斯特藩-玻尔兹曼常数）

与单位配合：`energy = c.h * frequency`

**文档**：https://docs.astropy.org/en/stable/constants/index.html
