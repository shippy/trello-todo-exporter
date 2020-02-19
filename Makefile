CONDA_ENV = /fs/u00/simon/.conda/envs/trello_exporter/
title := $(shell date +'%Y%m%d')
html_file := output/$(title).html
md_file := output/$(title).md

$(html_file): $(md_file)
	$(CONDA_ENV)/bin/pandoc -f gfm --template email_template.html -M title="Update, `date +'%Y/%m/%d'`" -o $(html_file) $(md_file)

$(md_file):
	./trello_retriever.py > $(md_file)

clean: 
	rm $(md_file) $(html_file)

# inspired by https://stackoverflow.com/a/3267187/2114580
# ...unnecessary, given the existence of make --always-make
redo: | clean $(md_file) $(html_file)

sendmail: $(html_file)
	cat $(html_file) | sendmail -t

.PHONY: sendmail redo clean
