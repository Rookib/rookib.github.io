# 素材来源

## 软件源头像

用户提供的蓝色动漫头像，保留完整画面，仅从 JPEG 无裁剪转为 PNG。`assets/avatar.png`、`CydiaIcon.png` 与 `SileoIcon.png` 使用相同内容。

`CydiaIcon@2x.png` 与 `CydiaIcon@3x.png` 是相同原图的字节副本，为 Sileo 优先请求的文件名提供完整画质。两种名称也发布到旧 `/jailbreak-repo/` 路径。Sileo 不使用 Release 的 Icon 字段读取源列表头像；已加载的源名称与头像需彻底退出并重开 Sileo 才会重新读取。

## 软件源横幅

- 参考源：https://tsangbaby.github.io/
- 原图：https://raw.githubusercontent.com/Tsangbaby/Tsangbaby.github.io/main/Alisa.png
- 本地文件：`assets/repo-featured-banner.png`
- 保留原始文件，不重绘、翻译或裁去原图内的文字。该图是参考源 Sileo 推荐横幅，不代表其首页渐变背景。
- 本源首页与 Sileo 推荐横幅使用此图；所有显示尺寸保持 2:1 比例。
- SHA-256：`fc150ca5cbf11bf60cc8deca60fde95591af590da9835811e71762396c1a5c16`

## 插件图标

图标展示不更改原插件许可或版权归属。优先使用包内原图标，缺少独立图标的项目使用本源通用软件包图形，来源在本清单及配置中明确登记。

| 插件 | 图标来源 |
| --- | --- |
| 截图标记 | 源内通用图标（非插件原图标） |
| Hello 键盘侠 · 长截图与拼图 | 源内通用图标（包内只有白色透明操作图，无独立插件图标） |
| StayShot 长截图引擎 | 源内通用图标（非插件原图标） |
| CocoaTop64 中文版 | 原插件图标 |
| Hello Left 左滑返回 | 原插件图标 |
| Hidden VPN | 用户提供的图标，随 `com.eason.fivegadvanced 2.6.9` 安装包提供；源内使用 `Library/PreferenceBundles/FiveGAdvancedPrefs.bundle/icon@3x.png` |
| FolderDockGlass 玻璃效果 | 源内通用图标（非插件原图标） |
| MisakaHelper 微信助手 | 源内通用图标（非插件原图标） |
| 快捷指令闪退修复 | 源内通用图标（非插件原图标） |
| 微信禁用热更新 | 源内通用图标（非插件原图标） |
| Wechatku 爱疯助手 | 源内通用图标（非插件原图标） |
| Hello Action 按键增强 | 原插件图标 |
| Relaxin 应用黑屏修复 | 源内通用图标（非插件原图标） |
| RootHide SSH 提示静默 | 源内通用图标（非插件原图标） |
| Touch-Dan | Touch-Viz 4.2 原图标 |
| QQ 紧凑布局 | 用户提供的 QQ 9.3.50 包内主图标 `Payload/QQ.app/AppIcon-160x60@2x.png`，保持原始 PNG 字节 |
| 短信通知复制 | 按用户要求用内置 image_gen 生成的专属图标：绿色短信气泡与复制符号；保留原始 PNG 字节 |
| Frida 动态调试工具 | [Frida 官方网站图标](https://github.com/frida/frida-website/blob/main/_assets/favicon32.png)，保留 32×32 原始 PNG；[MIT 许可](licenses/frida-website-MIT.txt) |

具体原包版本、成员路径及原图标 SHA-256 见 `config/packages.json`。通用图标由 `scripts/render-fallback-icons.py` 使用固定几何图形生成，可离线重新生成；本流程不会用通用图标替换已有原图标。
