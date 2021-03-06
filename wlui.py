"""Work Log with Database Employee Terminal"""

import datetime
import os
import sys

import models
from peewee import *
from worklog3 import CardCatalog


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
            invalid_input('task string somehow')
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
    if input('Save entry? [Y/n]\n> ').lower() != 'n':
        CardCatalog().save_new(add_name, add_task, add_minutes, add_notes)
        press_enter()
        return


def edit_entry(entry):
    updater = CardCatalog().acquire_target(entry)
    if updater is False:
        input(
            'Error. Entry not found. Press "enter" to return to main menu.'
        )
        return
    clear_screen()
    print("{}'s entry, {}.".format(entry['user_name'],
                                   entry['task_name']))

    entry_adding = 1
    while entry_adding:
        new_task = ''
        new_task = input('Edit task name, or hit enter to skip.\n> ')

        new_minutes = ''
        nm_check = 1
        while nm_check:
            new_minutes = input(
                'Edit integer of minutes, or enter to skip.\n> '
            )
            if new_minutes:
                if CardCatalog().minute_check(new_minutes):
                    break
                else:
                    invalid_input('integer')
                    continue

        new_date = ''
        nd_check = 1
        print(
            'Original Timestamp: ' + entry['timestamp'].strftime(
                '%m/%d/%Y'
            )
        )
        while nd_check:
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

        if input('Save entry? [Y/n]\n> ').lower() != 'n':
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
    clear_screen()
    s_choice = input('''
Please choose:
[L] A list of employees.
[n] To type a first or last name.
[p] To type in a partial name.
> ''').lower()
    clear_screen()
    if s_choice == 'p':
        namestr = input(
            'Please type a full or partial employee name.'
        )
        view_entries(bycat='name', target=namestr)
        return

    elif s_choice == 'n':
        roster = CardCatalog().generate_roster()
        if roster:
            new_roster = []
            name_loop = 1
            while name_loop:
                casual = input(
                    "Please type an employee's first or last name. \n> "
                )
                if CardCatalog().fol_check(casual):
                    break
                else:
                    invalid_input('first or last name')
                    continue
            for user in roster:
                if casual in user:
                    new_roster.append(user)
            r_num = 0
            if new_roster:
                for user in new_roster:
                    print('{}: {}'.format(r_num, user))
                    print('-' * 50)
                    r_num += 1
                list_loop = 1
                while list_loop:
                    employee = input(
                        "Please type a number to select an employee. \n> "
                    )
                    if CardCatalog().minute_check(employee):
                        if int(
                            employee
                        ) < len(
                            new_roster
                        ) and int(
                            employee
                        ) >= 0:
                            view_entries(
                                bycat='name',
                                target=new_roster[int(employee)]
                            )
                            clear_screen()
                            return
                    invalid_input('integer')
        print('No entries found.')
        press_enter()
        return

    else:
        roster = CardCatalog().generate_roster()
        if roster:
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
        print('No entries found.')
        press_enter()
        return


def by_date():
    """Search by date."""
    clear_screen()
    if input('''
Please choose:
[L] For a list of dates with tasks entered.
[r] To type in a specific range of dates.
> ''').lower() == 'r':
        timeloop = 1
        while timeloop:
            clear_screen()
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
        clear_screen()
        datelog = CardCatalog().generate_datelog()
        if datelog:
            d_num = 0
            for fenix in datelog:
                print('{}: {}'.format(d_num,
                                      fenix.strftime("%A %B %d, %Y")))
                print('-' * 50)
                d_num += 1
            listloop = 1
            while listloop:
                snackfruit = input(
                    "Please type a number to select a date. \n> "
                )
                if CardCatalog().minute_check(snackfruit):
                    if int(
                        snackfruit
                    ) >= 0 and int(
                        snackfruit
                    ) < len(
                        datelog
                    ):
                        view_entries(bycat='date',
                                     target=datelog[int(snackfruit)])
                        clear_screen()
                        return
                invalid_input('date selection')
        print('No entries found.')
        press_enter()
        return


def by_minutes():
    """Search by minutes spent on task."""
    clear_screen()
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
    clear_screen()
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
        print('No entries found.')
        press_enter()
        return


def search_entries():
    """Search existing entries."""
    clear_screen()
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
        quitter = 'Enter "q" to quit.'
        print('Welcome to the Library of Staff Productivity')
        print(quitter)
        print('-' * len(quitter))
        choice = input('''Please select an option.
-----------------------------
[a] Add new entry to work log.
[v] View entries.
[s] Search entries.
_____________________________
> ''').lower()
        if choice == 'a':
            add_entry()
        elif choice == 'v':
            view_entries()
        elif choice == 's':
            search_entries()
    return


if __name__ == '__main__':
    models.initialize()
    main_menu()
