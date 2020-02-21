title := $(shell date +'%Y%m%d')
html_file := output/$(title).html
md_file := output/$(title).md

include .env

$(html_file): $(md_file)
	$(TRELLO_CONDA_ENV)/bin/pandoc -f gfm --template email_template.html \
		-M title="Update, `date +'%Y/%m/%d'`" \
		-M mail_to="$(TRELLO_MAIL_TO)" \
		-M mail_from="$(TRELLO_MAIL_FROM)" \
		-o $(html_file) $(md_file)

$(md_file):
	$(TRELLO_CONDA_ENV)/bin/python trello_retriever.py > $(md_file)

sendmail: $(html_file)
	cat $(html_file) | sendmail -t

.PHONY: sendmail
