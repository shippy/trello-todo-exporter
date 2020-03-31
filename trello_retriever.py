#!/fs/u00/simon/.conda/envs/trello_exporter/bin/python
"""
Print out the cards from your Daily to-do board as nested checklists.

See README for details.
"""
import datetime
from dotenv import load_dotenv
import os
from trello import TrelloClient
from functools import partial
import re

DATE = datetime.datetime.today().strftime("%Y/%m/%d")
INITIAL_HR = False


def get_trello_list_from_name(api, board, name, list_id_lookup=None):
    """
    Load lists based on IDs if available, name-matching thru all board lists if
    not

    name: List name, should correspond to keys in list_id_lookup as well as actual
              Trello list name
    board: trello.Board object
    list_id_lookup: "List name" => trello.List object ID
    """
    # Try to get dict_id if that's a possibility
    dict_id = None
    if list_id_lookup is not None:
        dict_id = list_id_lookup.get(name)

    if dict_id is not None:
        # If dict_id successfully retrieved, use it
        target = api.get_list(dict_id)
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
                          print_attachments=False):
    cards = lst.list_cards()
    if len(cards) == 0:
        return

    card_format = '- [{check}] {labels} {name_with_url}. {desc}'

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
        name_with_url = get_formatted_link(card, link_after_name, check_alternatives=True)
        print(card_format.format(
            check=checkmark,
            labels=labels,
            # name=card.name,
            # url=card.url,
            name_with_url=name_with_url,
            desc=desc))
        print_checklists_from_card(card)
        if print_attachments:
            print_attachments_from_card(card, skip_links=True)


def print_checklists_from_card(card, remove_wip=False):
    checklists = card.checklists
    print_names = len(checklists) >= 2

    for chl in checklists:
        if print_names:
            print('    - **{}**'.format(chl.name))
            addl_indent = '    '
        else:
            addl_indent = ''

        items = chl.items
        in_progress_regex = r'\((in progress|WIP)\)$'
        for item in items:
            if item.get('checked'):
                checkmark = '- [x]'
            elif re.search(in_progress_regex, item.get('name')):
                checkmark = '- [-]'
            else:
                checkmark = '- [ ]'

            item_name = item.get('name')
            if remove_wip:
                item_name = re.sub(in_progress_regex, "", item_name)

            print('{}    {} {}'.format(addl_indent, checkmark, item_name))


def print_attachments_from_card(card, skip_links=False):
    attachments = card.attachments
    for a in attachments:
        if not a['isUpload'] and (a['url'] == a['name']):
            if not skip_links:
                print('    - [Card originally from another board]({})'
                      .format(a['url']))
        elif not a['isUpload']:
            print('    - Attachment: {}'.format(a['name']))


def get_formatted_link(card, link_after_name=True, check_alternatives=True):
    def get_alternative_card_source(card):
        attachments = card.attachments
        for a in attachments:
            if not a['isUpload'] and (a['url'] == a['name']):
                return a['url']
        else:
            return None

    alt = None
    if check_alternatives:
        alt = get_alternative_card_source(card)

    if link_after_name:
        if alt is None:
            template = "**{name}** ([card]({url}))"
        else:
            template = "**{name}** ([card]({url}), [card on original board]({alt}))"
    else:
        template = "**[{name}]({url})**"
        if alt is not None:
            template += " ([card on original board]({alt}))"

    if alt is None:
        return template.format(name=card.name, url=card.url)
    else:
        return template.format(name=card.name, url=card.url, alt=alt)


def get_labels_from_card(card):
    labels = card.labels
    if labels is None:
        return ""

    labels_text = []
    # spaces around label intended as padding that e-mail client doesn't strip
    label_template = ("<span style='color: white; background-color: {color};'>"
                      "&nbsp;{lbl}&nbsp;</span> ")
    for label in labels:
        labels_text.append(label_template.format(
            color=label.color, lbl=label.name))
    return "".join(labels_text)


def main_print(api, board, list_id_lookup):
    get_trello_list = partial(
        get_trello_list_from_name,
        api=api,
        board=board,
        list_id_lookup=list_id_lookup)

    done_today = get_trello_list(name='Done today')
    tomorrow = get_trello_list(name='Tomorrow')
    waiting_on = get_trello_list(name='Waiting on')
    in_progress = get_trello_list(name='In progress')

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
    my_week = client.get_board(os.getenv('BOARD_ID'))
    list_ids = {
        'Waiting on': os.getenv('LIST_WAITING_ON_ID'),
        'Done today': os.getenv('LIST_DONE_TODAY_ID'),
        'Tomorrow': os.getenv('LIST_TOMORROW_ID'),
        'In progress': os.getenv('LIST_INPROGRESS_ID'),
    }
    print('# {}'.format(DATE))
    main_print(client, my_week, list_ids)
