CONDA_ENV = /fs/u00/simon/.conda/envs/trello_exporter
title := $(shell date +'%Y%m%d')
html_file := output/$(title).html
md_file := output/$(title).md

$(html_file): $(md_file)
	$(CONDA_ENV)/bin/pandoc -f gfm --template email_template.html \
		-M title="Update, `date +'%Y/%m/%d'`" \
		-o $(html_file) $(md_file)

$(md_file):
	$(CONDA_ENV)/bin/python trello_retriever.py > $(md_file)

sendmail: $(html_file)
	cat $(html_file) | sendmail -t

# But that's an actual target, Simon, not a phony!
# I know, but I always want to remake it, so ¯\_(ツ)_/¯
.PHONY: sendmail $(md_file)
