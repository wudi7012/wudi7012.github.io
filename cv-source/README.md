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

## 安装与编译

Ubuntu / Debian 所需系统依赖：

```bash
sudo apt-get install texlive-xetex texlive-latex-recommended texlive-fonts-recommended poppler-utils cabextract python3-venv
cd cv-source
python3 -m venv .venv
. .venv/bin/activate
pip install -r requirements.txt
make fonts    # 新机器首次构建英文版时运行；当前工作机已安装
make          # 编译中英文，输出到 build/
```

`make fonts` 下载微软原始字体安装包的 Internet Archive 存档，验证已记录的 SHA-1 后，只提取字体文件，不运行 Windows 程序。完整字体不提交 Git；使用需遵守安装包自带的许可条款。若存档不可用，可自行将匹配的 `msyh.ttf`、`msyhbd.ttf` 放入 `en/fonts/`，构建时会校验 SHA-256。**字体缺失或版本不符会停止构建，不静默替换。**

常用命令：

```bash
make en       # 仅英文，XeLaTeX 两遍
make zh       # 仅中文，先编码 UTF-8 文本，再运行 pdfLaTeX
make verify   # 编译并与仓库 cv/ 下当前发布 PDF 进行像素及文本对比
make clean    # 删除缓存和中文生成代码，保留 build/ 内最终 PDF
```

查看 `build/Di_Wu_CV_EN.pdf` 与 `build/Di_Wu_CV_CN.pdf`。中文版本需要通过 `make zh` 编译，因为 `.tex` 中的 UTF-8 文字需要先映射到原稿字体的字符编码；不要跳过预处理直接调用 pdfLaTeX。

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

## 编辑与发布

英文编辑 `en/Di_Wu_CV_EN.tex`；中文编辑 `zh/Di_Wu_CV_CN.tex`。中文片段保持一条命令一行，保留 `t001` 等编号，按 LaTeX 习惯转义 `%`、`&`、`_` 等字符。相关样式片段可能属于同一可见行。

审核编译结果后：

```bash
make publish                  # 更新 ../cv/ 的两份 PDF；不会自动推送 GitHub
cd ..
git add cv-source cv
# 如主页内容改变，同时修改 _pages/about.md 中的 last_modified_at。
git commit -m "Update CVs"
git push origin main
```

当前发布 PDF 保留用户批准的原文件；初次建立源码目录不替换它们。`make publish` 仅在后续确实要发布重新生成的版本时使用。

若要从一份新的、人工确认的中文 PDF 重新建立固定版式，先保存现有工作，然后运行：

```bash
python tools/import_cn_pdf.py /path/to/new-approved.pdf /path/to/new-source-directory
```

该命令生成新的目录，不要用现有目录作为输出，以免覆盖正在编辑的内容。
