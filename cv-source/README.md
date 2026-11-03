# Di Wu / 吴笛 — 中英文 CV LaTeX 源码

这个目录是中英文简历的源码入口；网站下载文件统一放在仓库的 [`cv/`](../cv/) 目录。采用同一仓库管理，可以让源码、发布 PDF 和个人主页链接在同一次 Git 提交中更新，避免维护两个仓库的版本同步。Jekyll 已排除 `cv-source/`，不会把源码、构建缓存或本机完整字体发布到网站。

## 目录

```text
cv-source/
  en/Di_Wu_CV_EN.tex       英文正文（原有常规 XeLaTeX 排版）
  en/cv-style.tex          英文版式
  en/fonts/checksums.json  已确认的英文字体校验值
  zh/Di_Wu_CV_CN.tex       中文正文（逐文字片段、固定坐标）
  zh/layout.json          中文原稿的坐标、样式、绘制顺序及字符映射
  zh/assets/              原稿内的字体子集、头像和 PDF 字体映射
  tools/                  字体安装、中文预处理、PDF 对比工具
  verification/           初次转换的验收记录
  build/                  编译出的两份 PDF 和日志（Git 忽略）
```

## 当前工作机：修改 → 编译 → 查看

本机已经安装依赖和字体，日常修改无需重新安装。统一在下面的目录操作：

```bash
cd /mnt/workspace/wudi/cv/wudi7012.github.io/cv-source
```

### 1. 找到要编辑的文件

| 要改什么 | 编辑文件 |
| --- | --- |
| 英文经历、论文、联系方式等正文 | [`en/Di_Wu_CV_EN.tex`](en/Di_Wu_CV_EN.tex) |
| 英文字号、间距、分割线等版式 | [`en/cv-style.tex`](en/cv-style.tex) |
| 中文文字 | [`zh/Di_Wu_CV_CN.tex`](zh/Di_Wu_CV_CN.tex) |
| 中文固定坐标、样式等高级排版参数 | [`zh/layout.json`](zh/layout.json) |

英文是常规 LaTeX 排版。中文版为了精确复现原稿，使用固定坐标的文字片段，例如：

```tex
\CVText{t002}{24岁}
```

中文只改第二组花括号里的文字，保留 `t002` 等编号，一条命令保持在一行。不要修改 `zh/generated/`：它是每次编译重新生成的中间文件。文本增长不会自动推动后面的片段或换行，因此改后要检查重叠、行末和页底。新增原稿没有使用过的字形可能报错，处理方式见后面的限制说明。

两个版本不会自动互译或同步正文；同一段经历如需中英文都更新，请分别编辑。

### 2. 保存后编译

```bash
make en       # 只编译英文
make zh       # 只编译中文
# 或者：
make          # 同时编译中英文
```

英文会自动运行两遍 XeLaTeX；中文会自动完成文本编码预处理，再运行 pdfLaTeX。不要绕过 `make zh`，直接对中文源文件调用 pdfLaTeX。

### 3. 打开或刷新生成的 PDF

| 版本 | 本机预览文件 |
| --- | --- |
| 英文 | `/mnt/workspace/wudi/cv/wudi7012.github.io/cv-source/build/Di_Wu_CV_EN.pdf` |
| 中文 | `/mnt/workspace/wudi/cv/wudi7012.github.io/cv-source/build/Di_Wu_CV_CN.pdf` |

在文件列表中打开 `build/` 下对应的 PDF；编辑器支持 PDF 预览时可以直接查看，否则下载后用浏览器或 PDF 阅读器打开。再次修改并编译后，刷新 PDF 或重新打开即可。无需启动 Jekyll，也无需推送 GitHub，就能在本地看效果。

**日常预览请看 `cv-source/build/`，而不是仓库 `cv/` 或上一级带日期文件名的旧副本。** `make en`、`make zh` 和 `make` 只更新构建结果，不更新网站下载文件。

### 4. 清理是可选操作

```bash
make clean
```

这会删除编译日志、缓存和 `zh/generated/`，保留正文、字体、头像以及 `build/` 下的最终 PDF。不必每次编译后执行；编译出错时先保留日志，排查后再清理。下次编译会重新生成需要的中间文件。

### 5. 常见问题

| 情况 | 处理 |
| --- | --- |
| 修改后 PDF 没变化 | 先保存 `.tex`，确认 `make` 成功结束，再刷新 `build/` 下的 PDF；编译失败时旧 PDF 可能仍存在。 |
| `Missing or different font` | 运行 `make fonts` 安装匹配的英文字体；字体校验不允许静默替换。 |
| 中文提示 `font subset lacks` | 新字符不在原稿字体子集中；需要扩充匹配字体与字符映射，或从新批准的 PDF 重新导入。不能靠重复编译解决。 |
| 中文出现文字重叠 | 当前布局是固定坐标；缩短对应文字，或同时调整相关片段的布局。 |
| `make verify` 在改完正文后失败 | 它比较的是当前发布版，正文被有意修改后产生差异是预期行为，不等于 LaTeX 编译失败。 |
| 查英文 / 中文编译错误 | 分别查看 `build/Di_Wu_CV_EN.log`、`build/Di_Wu_CV_CN.log`，以及终端最后的错误信息。 |

## 原英文工作目录的兼容关系

原路径 `/mnt/workspace/wudi/cv/english_cv/Di_Wu_CV_EN.tex` 和 `cv-style.tex` 是指向本仓库英文源码的符号链接，编辑它们也会修改这里的同一份源码。

但两个目录的构建输出位置不同：原目录运行 `make` 输出到原目录，新的 `cv-source/` 目录运行 `make en` 输出到 `cv-source/build/`。**建议以后统一使用本 README 的新目录和命令**，避免打开另一处尚未更新的 PDF。

## 新机器首次安装

已配置好的当前工作机可以跳过这一节。新机器先克隆仓库，再安装依赖。

Ubuntu / Debian 示例：

```bash
git clone https://github.com/wudi7012/wudi7012.github.io.git
cd wudi7012.github.io/cv-source
sudo apt-get install make texlive-xetex texlive-latex-recommended texlive-fonts-recommended poppler-utils cabextract python3-venv
python3 -m venv .venv
. .venv/bin/activate
pip install -r requirements.txt
make fonts
make
```

新机器后续打开终端时，先进入 `cv-source/` 并执行 `. .venv/bin/activate`，再运行编译或验证命令。上面固定的 `/mnt/workspace/...` 路径只适用于当前工作机，新机器使用实际克隆目录。

`make fonts` 下载微软原始字体安装包的 Internet Archive 存档，验证已记录的 SHA-1 后，只提取字体文件，不运行 Windows 程序。完整字体不提交 Git；使用需遵守安装包自带的许可条款。若存档不可用，可自行将匹配的 `msyh.ttf`、`msyhbd.ttf` 放入 `en/fonts/`，构建时会校验 SHA-256。字体缺失或版本不符会停止构建。

## 确认效果后发布到个人主页

本地预览满意后，才需要执行这一步：

```bash
# 在 cv-source/ 目录执行：
make publish                  # 重新编译，并复制两份 PDF 到仓库 cv/ 目录
cd ..                         # 回到 wudi7012.github.io 仓库根目录

# 如需更新主页底部日期，编辑 _pages/about.md 的 last_modified_at 为实际更新日期。
git status --short
git diff --stat
git add cv-source cv _pages/about.md
git commit -m "Update CVs"
git push origin main
```

`make publish` 不会自行提交或推送。推送后等待 GitHub Pages 部署，检查 [英文下载](https://wudi7012.github.io/cv/Di_Wu_CV_EN.pdf)、[中文下载](https://wudi7012.github.io/cv/Di_Wu_CV_CN.pdf) 和主页日期。

初次建立源码目录时，`cv/` 保留的是用户批准的原 PDF；只有执行 `make publish` 才会用本次重新编译的 PDF 替换它们。

## 可选的一致性验证

```bash
make verify
```

该命令编译中英文，并分别与仓库 `cv/` 下当前发布的 PDF 进行像素和文本比较，结果写入 `build/verification-zh.json`、`build/verification-en.json`。它适用于迁移环境、排版重构或确认没有意外变化，**不是每次修改内容后必须通过的发布门槛**。

## 中文版的“完全一致”范围

基准是用户提供的 `吴笛的简历_CN_2026_11.pdf`，SHA-256 为：

```text
e80a487bdbda045a7d8cc00102100b1914c34ff8477696856ca005b553793af8
```

该 PDF 由 wkhtmltopdf 生成，采用微软雅黑 **6.25** 与 DejaVu Sans **2.33**。英文版已确认的完整字体是微软雅黑 **5.00**，不能拿它替换中文原稿的字形。中文版直接复用原 PDF 内已嵌入的字体子集、字距、原始头像和绘制指令，由 LaTeX 重新生成单页 PDF。

它不是 `pdfpages` 包装，也不是整页截图：正文在 `zh/Di_Wu_CV_CN.tex` 中以 100 个 `\CVText{编号}{文字}` 片段保存，输出保留真实、可选择和检索的文字；唯一图像是原有头像。原稿内的性别、日期、措辞、加粗、下划线、局部底色及字号均保留，不套用英文版的编辑内容。

初次验收结果：

- 页面尺寸 615 × 870 pt、单页、提取文字完全一致。
- MuPDF：72 / 144 / 300 / 600 DPI 的差异像素全部为 0。
- Poppler：300 DPI 的差异像素为 0。
- 中文字体资源、头像字节、忽略空白后的 PDF 绘制指令均一致。

**明确的差异与限制：**

1. PDF 文件本身不是逐字节相同：生成器、时间戳、对象编号、压缩组织及文件大小不同。零像素差异指上述同一渲染器、同一参数下的验证结果，不能解释为两个文件的 SHA-256 相同。
2. 中文版采用固定坐标，不是自动换行的通用简历模板。改动文字长度后，需要检查相邻片段、行末和页底；版式参数保存在 `layout.json`。
3. 原稿只嵌入实际使用过的字形。新增不在子集中的字符会明确报错；需要取得匹配的完整字体并扩充编码/重新标定版式，或从新版批准 PDF 重新导入。不得用其他字体补字并声称完全一致。
4. `make verify` 比较的是仓库当前发布版本；有意修改正文后出现差异是正常的，需要人工验收后再更新发布版。初次转换的记录固定保存在 `verification/`。

可运行 `python tools/check_cn_editing.py` 检查文本编辑确实改变输出，以及未知字形会被拒绝。它在临时目录测试，不修改正式简历。

## 从新版中文 PDF 重新导入固定版式

若要从一份新的、人工确认的中文 PDF 重新建立固定版式，先保存现有工作，然后运行：

```bash
python tools/import_cn_pdf.py /path/to/new-approved.pdf /path/to/new-source-directory
```

输出目录必须为空。先在新目录检查结果，不要覆盖正在编辑的源文件。这个工具为当前中文 PDF 的资源和文字结构编写，并非所有 PDF 都能直接导入。
