# Trello exporter

Tool to export your day-to-day to-do Trello board into nested checklist form.

## Assumed structure of your Trello

Board, with lists called:

- "This week" (not used here) - task plan for the week
- "Today" (not used here) - task plan for the day, usually automatically
  populated from Tomorrow
- "In progress" - what you're working on right now (which is likely half-done)
- "Done today" - what you're done with (duh)
- "Tomorrow" - task plan for tomorrow
- "Waiting on" - what you'll get on as soon as someone does their job on it

Butler moves the cards between the lists around midnight, but that's not
important right now.

## Use

1. Create the conda environment: `conda env create -f environment.yml`
2. Set your environmental variables in `.env`. See `.env.example` for the
   required and optional variables. **This includes the location of your newly
   created conda environment and your board ID** - see [FAQ](#FAQ) to learn how
   to get those.
3. Run `make` to create the Markdown rundown of your day, as well as an
   e-mailable HTML, in `output/`
4. Run `make sendmail` to have sendmail send that to the recipients specified
   in `.env`.

## FAQ

### How can I get the Trello board identifier?

Courtesy of [/u/heyylisten/](https://www.reddit.com/r/trello/comments/4axfcd/where_is_my_trello_board_id/d14ok3k/):

1. In your browser, navigate to the board in question. Its format will be along
   the lines of `https://trello.com/b/MMKEsHNn/my-week`.
2. In the URL, replace the board name (`my-week`) with the string
   `reports.json`: `https://trello.com/b/MMKEsHNn/reports.json`
3. The very first entry should be your board ID.

### How can I get the location of my conda environment?

`conda info` when you sourced the environment, or `conda info --env` for
information about all your environments.

### Make says "make: <file> is up to date." What if I want to re-make the files I just made?

Run `make --always-make` or `make -B` (they're the same thing).

## To-do:

- [ ] Make the conda environment's location detection automatic
- [ ] Find the board based on board name instead of requiring board ID
