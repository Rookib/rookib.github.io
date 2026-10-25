# Rookib

这是一个托管在 GitHub Pages 上的个人 iOS 越狱 APT 软件源，同时支持传统 rootful、现代 rootless 与 rootHide 软件包。

## 添加软件源

软件源地址：

```text
https://rookib.github.io/
```

在已越狱设备上打开上述网页，或把地址粘贴到 Sileo、Zebra、Cydia、Installer 中。

## 发布软件包

1. 构建一个有效的 Debian 软件包（`.deb`）。
2. 把它放进 [`pool`](./pool) 目录。
3. 在 [`config/packages.json`](./config/packages.json) 登记中文名称、摘要、分类、作者与图标来源，并在 [`depictions`](./depictions) 添加 Sileo 原生“描述 / 更新”详情页。作者显示统一为 `Rookib`，原始许可证及版权声明保留。
4. 将实际图标放入 `assets/packages/`；没有独立原图标时登记 `repository-fallback`，运行 `python3 scripts/render-fallback-icons.py` 生成明确标注的源内通用图标。
5. 运行 `python3 scripts/build-metadata.py`，生成 APT 展示覆盖、网页详情与插件目录，再运行 `python3 scripts/build-metadata.py --check --require-versions`。不要直接修改自动生成的文件。
6. 提交拉取请求。GitHub Actions 会验证多版本、多架构索引及软件包校验和，并生成可检查的网页产物；拉取请求不会部署。
7. 检查通过后合并到 `main`，由主分支自动发布。

一个最小的 `control` 文件通常包含：

```text
Package: com.example.package
Name: 示例插件
Version: 1.0.0
Architecture: iphoneos-arm64
Description: 插件功能的简短中文说明。
Maintainer: Rookib
Author: Rookib
Section: 系统插件
```

三种目标环境使用不同架构：

- 传统 rootful：`iphoneos-arm`
- 现代 rootless：`iphoneos-arm64`
- rootHide：`iphoneos-arm64e`

软件包内部目录必须已经适配目标越狱环境；本软件源只负责识别和分发，不会自动在 rootful、rootless 与 rootHide 之间转换软件包。同一软件可以把三种构建产物都放进 `pool/`，构建流程会保留所有版本与多架构条目，客户端再按当前环境筛选。

### rootHide 构建要点

rootHide 版本应使用 [roothide/theos](https://github.com/roothide/theos) 构建，在 Makefile 中加入：

```make
THEOS_PACKAGE_SCHEME = roothide
```

也可以运行 `make package THEOS_PACKAGE_SCHEME=roothide`。在不同 scheme 之间切换前先运行 `make clean`。

rootHide 的 `.deb` 架构应为 `iphoneos-arm64e`，但这不代表每个 Mach-O 都只能编译为 arm64e。不要把普通 rootless 包只改架构名后上传：rootHide 使用随机 jbroot，不能硬编码 `/var/jb` 或某个展开后的 jbroot 路径。源码若要访问越狱文件，应按 [rootHide 开发文档](https://github.com/roothide/Developer) 使用 `jbroot()` 等 API，并确认所有第三方依赖都有 rootHide 兼容版本。

同一软件包若发布新内容，请务必提升 `Version`，不要用相同版本号覆盖旧 `.deb`，否则客户端可能继续使用缓存。

## 目录结构

- `pool/` — `.deb` 软件包
- `depictions/` — Sileo 原生“描述 / 更新”双标签详情页及生成的中文网页详情
- `config/packages.json` — 中文展示元数据和图标来源
- `assets/packages/` — 插件原图标或明确登记的源内通用图标
- `docs/asset-sources.md` — 头像、横幅及图标来源
- `scripts/build-metadata.py` — 生成展示文件并核验安装包/索引一致性
- `config/package-overrides` — 软件包摘要、分类及详情页地址覆盖
- `scripts/build-repo.sh` — APT 索引生成脚本
- `.github/workflows/deploy.yml` — GitHub Pages 自动发布流程
- `index.html` — 软件源首页

同域名的 `https://rookib.github.io/jailbreak-repo/` 保留完整兼容副本；新设备请使用上面的短地址。此前使用旧账号域名的设备需将软件源更新为以上地址，兼容目录不会重定向旧域名。

请只发布自己制作或已获得再分发许可的软件包。

## 展示与版本维护

源名称、源图标、首页与包详情统一使用 Rookib。APT 覆盖只调整展示字段，不修改 `.deb` 内的包 ID、版本、依赖、架构、可执行文件或许可。新增版本直接追加到 `pool/`，保留旧版本；请勿把新版本的系统兼容条件套到旧版本。FolderDockGlass 按要求固定现有 1.1.0+opt.2，本次只更新源内展示。

原生详情与网页详情共享同一份 `depictions/*.json`。安装包的兼容范围、测试状态与更新记录应明确写入该文件；展示中的“当前版本”必须在源内实际存在。构建会阻止缺少中文元数据、图标丢失、原图标校验和变化、重复包身份、索引漏掉旧版本或改写依赖等问题。

完整 APT 构建需要 Linux 的 `apt-utils`、`dpkg-dev`、`bzip2` 和 `xz-utils`，运行 `bash scripts/build-repo.sh`。仅检查和生成展示文件可在 macOS 使用 Python 3.9 以上版本离线完成。
