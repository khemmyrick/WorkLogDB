"""Work Log with Database Employee Terminal"""

from collections import OrderedDict
import datetime
import os
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


def invalid_input(wanted):
    """Warn user about incorrect input."""
    input("Invalid {}.  Please try again.".format(wanted))
    return


def press_enter():
    input("Press enter to return.")
    return

def add_entry():
    """Add new entry to work log."""
    clear_screen()
    name_adding = 1
    while name_adding:
        add_name = input('Please enter full name.\n> ')
        if CardCatalog().name_check(add_name):
            break
        else:
            invalid_input('first and last name string')
            continue

    task_adding = 1
    while task_adding:
        add_task = input('What task did you work on?\n> ')
        if isinstance(add_task, str):
            break
        else:
            input('Task name must be a string.')
            continue

    minutes_adding = 1
    while minutes_adding:
        add_minutes = input('How many minutes were spent?\n> ')
        if CardCatalog().minute_check(add_minutes):
            break
        else:
            invalid_input('integer')
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
    if updater is False:
        input(
            'Error. Entry not found. Press "enter" to return to main menu.'
        )
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
                break
            else:
                continue

        new_date = ''
        nd_check = 1
        print(
            'Original Timestamp: ' + entry['timestamp'].strftime(
                '%m/%d/%Y'
            )
        )
        new_date = input(
            "Type new date in MM/DD/YYYY format. Or enter to skip."
        )
        if new_date != '':
            try:
                new_dto = datetime.datetime.strptime(
                    new_date,
                    "%m/%d/%Y"
                )
                break
            except ValueError:
                invalid_input('date string')
                continue

        new_notes = ''
        if input('Any notes? [y/N]').upper().strip() == "Y":
            print('Type notes here. Press "ctrl+d" when finished.')
            new_notes = sys.stdin.read().strip()

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
                print("Saved succesfully!")
                press_enter()
            else:
                press_enter()
            return


def by_staff():
    """Search by staff names."""
    # Under test.
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
        list_loop = 1
        while list_loop:
            employee = input(
                "Please type a number to select an employee. \n> "
            )
            if CardCatalog().minute_check(employee):
                if int(employee) < len(roster) and int(employee) >= 0:
                    view_entries(
                        bycat='name',
                        target=roster[int(employee)]
                    )
                    clear_screen()
                    return
            invalid_input('integer')


def by_date():
    """Search by date."""
    # Under test.
    if input('''
Please choose:
[L] For a list of dates with tasks entered.
[r] To type in a specific range of dates.
> ''').lower() == 'r':
        timeloop = 1
        while timeloop:
            clear_screen()
            # My project reviewer reported 'an error searching with "03/03/3333-05/05/5555". The same thing happens if I try to pick a date from the list with a bad input.' By the time I tried to recrete said error, I'd already implemented the d_range_check function to catch improper date range inputs.  So, I think I fixed it?
            target_range = input('''
Please enter date range in following format:
"MM/DD/YYYY-MM/DD/YYYY"
Range will find from midnight of first date, to midnight of the last date.
So, if you want to search New Year's Day 2018, type "01/01/2018-01/02/2018"
> ''')
            if CardCatalog().d_range_check(target_range):
                targets = target_range.split(sep='-')
                dateobj = CardCatalog().date_check(targets[0])
                dateobj1 = CardCatalog().date_check(targets[1])
                view_entries(bycat='date', target=dateobj, datelast=dateobj1)
                return
            else:
                invalid_input('date range string')
    else:
        datelog = CardCatalog().generate_datelog()
        d_num = 0
        for fenix in datelog:
            print('{}: {}'.format(d_num,
                                  fenix.strftime("%A %B %d, %Y")))
            print('-' * 50)
            d_num += 1
        listloop = 1
        while listloop:
            snackfruit = input("Please type a number to select a date. \n> ")
            # Check that number entered exists in list.
            if CardCatalog().minute_check(snackfruit):
                if int(snackfruit) >= 0 and int(snackfruit) < len(datelog):
                    view_entries(bycat='date', target=datelog[int(snackfruit)])
                    clear_screen()
                    return
            invalid_input('date selection')


def by_minutes():
    """Search by minutes spent on task."""
    # Under test.
    minloop = 1
    while minloop:
        minnum = input('Please type an integer of minutes.')
        if CardCatalog().minute_check(minnum):
            view_entries(bycat='minutes', target=minnum)
            return
        else:
            invalid_input('integer')
            clear_screen()


def by_term():
    """Search by term."""
    # Under test.
    termstr = input('Please enter search term.')
    view_entries(bycat='term', target=termstr)
    return


def view_entries(bycat=None, target=None, datelast=None):
    """View entries."""
    if datelast:
        viewer = CardCatalog().load_entries(bycat=bycat,
                                            target=target,
                                            datelast=datelast)
    else:
        viewer = CardCatalog().load_entries(bycat=bycat,
                                            target=target)
    if viewer:
        view = len(viewer)
        view_num = 0
        while view_num < view:
            clear_screen()
            vts = viewer[view_num]['timestamp'].strftime('%A %B %d, %Y')
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
    else:
        press_enter()
        return

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
        return


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
        # Get rid of ordered dict!
        choice = input('''Please select an option.
-----------------------------
[a] Add new entry to work log.
[v] View entries.
[s] Search entries.
_____________________________
> ''').lower()
        # End refac.
        # for key, value in menu.items():
        #    menu_buttons = '{}) {}'.format(key.upper(), value.__doc__)
        #    # .__doc__ will read docstrings of the menu functions.
        #    print(menu_buttons)
        #    print('-' * len(menu_buttons))
        # choice = input("Action: ").lower()

        # if choice in menu:
        #    menu[choice]()
        if choice == 'a':
            add_entry()
        elif choice == 'v':
            view_entries()
        elif choice == 's':
            search_entries()
    return


def start_now():
    in_play = 1
    while in_play == 1:
        main_menu()
        in_play -= 1
    print('Out of main menu.')

    
menu = OrderedDict([
    ('a', add_entry),
    ('v', view_entries),
    ('s', search_entries)
])

if __name__ == '__main__':
    start_now()
    # main_menu()
