## Assumed structure of your Trello

Board, with lists called:

- "This week" (not used here) - task plan for the week
- "Today" (not used here) - task plan for the day, usually automatically populated from Tomorrow
- "In progress" - what you're working on right now (which is likely half-done)
- "Done today" - what you're done with (duh)
- "Tomorrow" - task plan for tomorrow
- "Waiting on" - what you'll get on as soon as someone does their job on it

Butler moves the cards between the lists around midnight, but that's not important right now.

## Use

1. Set your environmental variables in `.env`. See `.env.example` for the
   required and optional variables.
2. Create the conda environment: `conda env create -f environment.yml`
3. **Patch the following files**: 
    - the `Makefile` with the actual conda env location,
    - the `email_template.html` with the actual `From:` and `To:` headers you want to use.
4. Run `make` to create the Markdown rundown of your day, as well as an
   e-mailable HTML, in `output/`
5. Run `make sendmail` to have sendmail send that _to the recipients specified
   in `email_template.html`_.

## To-do:

- [ ] Make the conda environment's location detection automatic
- [ ] Make the `From:` and `To:` headers configurable via `.env`. (Or some
      other way, since only `trello_retriever.py` actually has access to those
      variables - they don't get *actually* exported into the shell environment
      shared with `pandoc` / `Makefile`.)
