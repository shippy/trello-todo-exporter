#!/fs/u00/simon/.conda/envs/trello_exporter/bin/python
"""
Print out the cards from your Daily to-do board as nested checklists.

See README for details.
"""
import datetime
from dotenv import load_dotenv
import os
from trello import TrelloClient

DATE = datetime.datetime.today().strftime("%Y/%m/%d")
INITIAL_HR = False


def get_trello_list_from_name(name, board, keys_dict=None):
    """
    Load lists based on IDs if available, name-matching thru all board lists if
    not

    name: List name, should correspond to keys in keys_dict as well as actual
              Trello list name
    board: trello.Board object
    keys_dict: "List name" => trello.List object ID
    """
    # Try to get dict_id if that's a possibility
    dict_id = None
    if keys_dict is not None:
        dict_id = keys_dict.get(name)

    if dict_id is not None:
        # If dict_id successfully retrieved, use it
        target = client.get_list(dict_id)
    else:
        # Iterate through all lists on board until you find the first one
        # that's open and has this name
        all_lists = board.all_lists()
        try:
            target = [lst for lst in all_lists
                      if (lst.name == name) and not lst.closed][0]
        except IndexError:
            target = None

    if target is None:
        raise ValueError("Could not retrieve list '{}'".format(name))

    return target


def print_cards_from_list(lst, checkmark=' ', link_after_name=True,
                          print_attachments=True):
    cards = lst.list_cards()
    if len(cards) == 0:
        return

    if link_after_name:
        card_format = '- [{check}] {labels}**{name}** ([card]({url})). {desc}'
    else:
        card_format = "- [{check}] {labels}**[{name}]({url})**. {desc}"

    global INITIAL_HR
    if INITIAL_HR:
        print("\n----\n")
    else:
        INITIAL_HR = True
    print("## {}\n".format(lst.name))

    for card in cards:
        if "\n" in card.desc:
            desc = "Long description - see card."
        else:
            desc = card.desc
        labels = get_labels_from_card(card)
        print(card_format.format(
            check=checkmark,
            labels=labels,
            name=card.name,
            url=card.url,
            desc=desc))
        print_checklists_from_card(card)
        if print_attachments:
            print_attachments_from_card(card)


def print_checklists_from_card(card):
    checklists = card.checklists
    print_names = len(checklists) > 2
    for chl in checklists:
        if print_names:
            # print('## {}'.format(chl.name))
            print('  - **{}**'.format(chl.name))
            addl_indent = '  '
        else:
            addl_indent = ''

        items = chl.items
        for item in items:
            if item.get('checked'):
                checkmark = '- [x]'
            else:
                checkmark = '- [ ]'
            print('{}    {} {}'.format(
                addl_indent, checkmark, item.get('name')))


def print_attachments_from_card(card):
    attachments = card.attachments
    for a in attachments:
        if not a['isUpload'] and (a['url'] == a['name']):
            print('    - [Card originally from another board]({})'
                  .format(a['url']))
        elif not a['isUpload']:
            print('    - Attachment: {}'.format(a['name']))


def get_labels_from_card(card):
    labels = card.labels
    labels_text = []
    label_template = ("<span style='color: white; background-color: {color};'>"
                      " {lbl} </span> ")  # spaces around intended as padding
    for label in labels:
        labels_text.append(label_template.format(
            color=label.color, lbl=label.name))
    return "".join(labels_text)


def main_print(client, board, list_ids):
    my_week = board

    # print("---")
    # print("title: Update, {}".format(DATE))
    # print("---")

    done_today = get_trello_list_from_name('Done today', my_week, list_ids)
    tomorrow = get_trello_list_from_name('Tomorrow', my_week, list_ids)
    waiting_on = get_trello_list_from_name('Waiting on', my_week, list_ids)
    in_progress = get_trello_list_from_name('In progress', my_week, list_ids)

    print_cards_from_list(done_today, 'x')
    print_cards_from_list(in_progress, '-')
    print_cards_from_list(waiting_on, '-')
    print_cards_from_list(tomorrow, ' ')


if __name__ == '__main__':
    load_dotenv()
    client = TrelloClient(
        api_key=os.getenv('TRELLO_API_KEY'),
        token=os.getenv('TRELLO_TOKEN'),
        token_secret=os.getenv('TRELLO_TOKEN_SECRET'))
    list_ids = {
        'Waiting on': os.getenv('LIST_WAITING_ON_ID'),
        'Done today': os.getenv('LIST_DONE_TODAY_ID'),
        'Tomorrow': os.getenv('LIST_TOMORROW_ID'),
        'In progress': os.getenv('LIST_INPROGRESS_ID'),
    }
    my_week = client.get_board(os.getenv('BOARD_ID'))
    print('# {}'.format(DATE))
    main_print(client, my_week, list_ids)
