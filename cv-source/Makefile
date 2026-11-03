.PHONY: all en zh fonts verify publish clean
PYTHON ?= python3
all: en zh

en:
	$(PYTHON) tools/check_en_fonts.py
	mkdir -p build
	cd en && xelatex -interaction=nonstopmode -halt-on-error -output-directory=../build Di_Wu_CV_EN.tex
	cd en && xelatex -interaction=nonstopmode -halt-on-error -output-directory=../build Di_Wu_CV_EN.tex

zh:
	mkdir -p build
	$(PYTHON) tools/prepare_cn.py zh
	cd zh && pdflatex -interaction=nonstopmode -halt-on-error -output-directory=../build Di_Wu_CV_CN.tex

fonts:
	$(PYTHON) tools/install_en_fonts.py

verify: all
	$(PYTHON) tools/verify_pdf.py ../cv/Di_Wu_CV_CN.pdf build/Di_Wu_CV_CN.pdf --report build/verification-zh.json
	$(PYTHON) tools/verify_pdf.py ../cv/Di_Wu_CV_EN.pdf build/Di_Wu_CV_EN.pdf --report build/verification-en.json

# Explicitly refresh website downloads after reviewing the PDFs. Does not push Git.
publish: all
	cp build/Di_Wu_CV_CN.pdf ../cv/Di_Wu_CV_CN.pdf
	cp build/Di_Wu_CV_EN.pdf ../cv/Di_Wu_CV_EN.pdf

clean:
	rm -f build/*.aux build/*.log build/*.out build/*.fls build/*.fdb_latexmk build/*.synctex.gz
	rm -rf zh/generated
