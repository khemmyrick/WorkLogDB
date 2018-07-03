"""Work Log with Database Employee Terminal"""

from collections import OrderedDict
import datetime
import os
import re
import sys

from peewee import *
from worklog3 import CardCatalog

# db = SqliteDatabase('log.db')


def initialize():
    """Create database and table if they don't exist."""
    db.connect()
    db.create_tables([Entry], safe=True)


def clear_screen():
    """Clear the screen."""
    os.system('cls' if os.name == 'nt' else 'clear')


def add_entry():
    """Add new entry to work log."""
    clear_screen()
    name_adding = 1
    while name_adding:
        add_name = input('Please enter full name.\n> ')
        if CardCatalog().name_check(add_name):
            name_adding -= 1
        else:
            input('Please enter first and last name for employee.')
            continue

    task_adding = 1
    while task_adding:
        add_task = input('What task did you work on?\n> ')
        if isinstance(add_task, str):
            task_adding -= 1
        else:
            input('Task name must be a string.')
            continue

    minutes_adding = 1
    while minutes_adding:
        add_minutes = input('How many minutes were spent?\n> ')
        if CardCatalog().minute_check(add_minutes):
            minutes_adding -= 1
        else:
            input('Invalid integer. Press enter to try again.')
            continue

    add_notes = ''
    if input('Any notes? [y/N]').upper().strip() == "Y":
        print('Type notes here. Press "ctrl+d" when finished.')
        add_notes = sys.stdin.read().strip()
    
    clear_screen()
    print('Name: ' + add_name)
    print('Task: ' + add_task)
    print('Minutes: ' + add_minutes)
    print(CardCatalog().notes_out(add_notes))
    if input('Save entry? [Y/n]\n> ') != 'n':
        CardCatalog().save_new(add_name, add_task, add_minutes, add_notes)
        input('Hit enter key to continue.')


def edit_entry(entry):
    updater = CardCatalog().acquire_target(entry)
    if updater == False:
        input('Error. Entry not found. Press "enter" to return to main menu.')
        return
    print("{}'s entry, {}.".format(entry['user_name'],
                                   entry['task_name']))

    entry_adding = 1
    while entry_adding:
        new_task = ''
        new_task = input('Edit task name, or hit enter to skip.\n> ')

        new_minutes = ''
        nm_check = 1
        new_minutes = input('Edit integer of minutes, or enter to skip.\n> ')
        if new_minutes:
            if CardCatalog().minute_check(new_minutes):
                nm_check -= 1
            else:
                continue

        new_date = ''
        nd_check = 1
        print('Original Timestamp: ' + entry['timestamp'].strftime('%m/%d/%Y'))
        new_date = input("Type new date in MM/DD/YYYY format. Or enter to skip.")
        if new_date != '':
            try:
                new_dto = datetime.datetime.strptime(new_date,
                                           "%m/%d/%Y")
                nd_check -= 1
            except ValueError:
                input('Invalid date. Press enter to retry.')
                continue

        new_notes = ''
        if input('Any notes? [y/N]').upper().strip() == "Y":
            print('Type notes here. Press "ctrl+d" when finished.')
            add_notes = sys.stdin.read().strip()
    
        clear_screen()
        print('Name: ' + entry['user_name'])
        if new_task != '':
            print('Task: ' + new_task)
        else:
            print('Task: ' + entry['task_name'])
        if new_minutes != '':
            print('Minutes: ' + new_minutes)
        else:
            print('Minutes: ' + str(entry['task_minutes']))
        if new_notes:
            if len(new_notes) > 50:
                print('Notes: ' + new_notes[:50] + '. . . ')
            else:
                print('Notes: ' + new_notes)
        else:
            print('Notes: ' + entry['task_notes'])

        if input('Save entry? [Y/n]\n> ') != 'n':
            if new_task != '':
                updater.task_name = new_task
            if new_minutes != '':
                updater.task_minutes = new_minutes
            if new_notes != '':
                updater.task_notes = new_notes
            if new_date != '':
                updater.timestamp = new_dto

            saver = CardCatalog().save_edits(updater)
            if saver:
                input("Saved succesfully! Hit enter to continue.")
            else:
                input("Hit enter to return to previous menu.")
            entry_adding -= 1


def by_staff():
    """Search by staff names."""
    if input('''
Please choose:
[L] A list of empltoyees.
[n] To type in a specific name.
> ''').lower() == 'n':
        namestr = input('Please type a full or partial employee name.')
        view_entries(bycat='name', target=namestr)
        return
    else:
        roster = CardCatalog().generate_roster()
        r_num = 0
        for user in roster:
            print('{}: {}'.format(r_num, user))
            print('-' * 50)
            r_num += 1
        employee = input("Please type a number to select an employee. \n> ")
        view_entries(bycat='name', target=roster[int(employee)])
        clear_screen()
        return


def by_date():
    """Search by date."""
    pass
    # input('Search by date')


def by_minutes():
    """Search by minutes spent on task."""
    minloop = 1
    while minloop:
        minnum = input('Please type an integer of minutes.')
        if CardCatalog().minute_check(minnum):
            view_entries(bycat='minutes', target=minnum)
            return
        else:
            input('Invalid input.  Press enter to continue.')
            clear_screen()

def by_term():
    """Search by term."""
    termstr = input('Please enter search term.')
    view_entries(bycat='term', target=termstr)
    return


def view_entries(bycat=None, target=None):
    """View entries."""
    viewer = CardCatalog().load_entries(bycat=bycat, target=target)
    view = len(viewer)
    view_num = 0
    while view_num < view:
        clear_screen()
        vts = viewer[view_num]['timestamp'].strftime('%A %B %d') # list index out of range on items that happen once?
        # Specifically at this line?
        print(vts)
        print('='*len(vts))
        print("Recorded by: " + viewer[view_num]['user_name'])
        print("Task: " + viewer[view_num]['task_name'])
        print("Minutes: " + str(viewer[view_num]['task_minutes']))
        print("Additional Notes: " + viewer[view_num]['task_notes'])
        print('\n\n' + '=' * len(vts))
        print('N) Next entry')
        print('p) Previous entry')
        print('e) Edit entry')
        print('d) Delete entry')
        print('q) Return to menu')

        next_action = input('Action: \n[N/p/e/d/q]: ').lower().strip()
        if next_action == 'q':
            break
            # Break exits view loop, returns to main menu.
        elif next_action == 'e':
            edit_entry(viewer[view_num])
            break
        elif next_action == 'd':
            if input('Delete entry. Are you sure? y/N ').lower() == 'y':
                CardCatalog().delete_entry(viewer[view_num])
                break
            else:
                view_num += 0
        elif next_action == 'p':
            if view_num > 0:
                view_num -= 1
            else:
                input("Can't go further than that. (Enter to continue.)")
        else:
            if view_num < view - 1:
                view_num += 1
            else:
                input("That's all we could find. (Enter to continue.)")


def search_entries():
    """Search existing entries.""" 
    search_by = input('''
How would you like to search?
-----------------------------
[n] By Employee Name
[d] By Date
[m] By Minutes
[t] By Search Term
[Q] Return to Main Menu
_____________________________
> ''')
    if search_by.lower() == 'n':
        by_staff()
    elif search_by.lower() == 'd':
        by_date()
    elif search_by.lower() == 'm':
        by_minutes()
    elif search_by.lower() == 't':
        by_term()
    else:
        pass

def main_menu():
    """Show the menu loop."""
    choice = ''

    while choice.lower() != 'q':
        clear_screen()
        # staff_list, date_list = current_lists()
        quitter = 'Enter "q" to quit.'
        print('Welcome to the Library of Staff Productivity')
        print(quitter)
        print('-' * len(quitter))
        for key, value in menu.items():
            menu_buttons = '{}) {}'.format(key.upper(), value.__doc__)
            # .__doc__ will read docstrings of the menu functions.
            print(menu_buttons)
            print('-' * len(menu_buttons))
        choice = input("\nAction: ").lower().strip()

        if choice in menu:
            menu[choice]()


menu = OrderedDict([
    ('a', add_entry),
    ('v', view_entries),
    ('s', search_entries)
])

if __name__ == '__main__':
    main_menu()
