CONDA_ENV = /fs/u00/simon/.conda/envs/trello_exporter/
mail_file := output/$(shell date +'%Y%m%d').html
$(mail_file):
	./trello_retriever.py | $(CONDA_ENV)/bin/pandoc -f gfm --template email_template.html -M title="Update, `date +'%Y/%m/%d'`" -o $(mail_file)

sendmail: $(mail_file)
	cat $(mail_file) | sendmail -t

.PHONY: email
