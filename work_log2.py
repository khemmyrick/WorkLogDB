#!/usr/bin/env python3

"""Work Log: Now with Database!
Next Steps:
0. Refactor Add / Edit Entry so users enter all information in 1 text box, ie the task_notes entry mode.  Have users press "enter" between each thing and split resulting string into list.  To reduce total number of inputs?
1. Start unit testing.
Steps taken as of 6/24/18:
    a] Figure out HOW to unittest inputs...
    b] Find out how to write various assert methods needed to test methods/functions in this project.
    c] Figure out which mocks are needed, to test inputs, function calls, etc etc
    d] Begin rewriting entire program from scratch, based on what tests I can figure out how to write.
    e] Preview an example of how someone else completed this assignment....
    Realization @ 6pm on 6/24/18:
!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
    ????!!!!!!! Do I only need assertTrue/False tests !!!!!!??????
!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
2. START UNIT TESTING?
As of 6/25/18 @ 10:40am... I have 11 tests that run in 8.5 seconds.
Next steps:
Test, refactor, test, repeat.

"""

from collections import OrderedDict
import datetime
import os
import re
import sys
import unittest

from peewee import *

db = SqliteDatabase('log.db')


class Entry(Model):
    timestamp = DateTimeField(default=datetime.datetime.now)
    user_name = CharField(max_length=500)
    task_name = CharField(max_length=1000)
    task_minutes = IntegerField(default=0)
    task_notes = TextField()

    class Meta:
        """Tell entry what database it belongs to?"""
        database = db


def initialize():
    """Create database and table if they don't exist."""
    db.connect()
    db.create_tables([Entry], safe=True)


def clear_screen():
    """Clear the screen."""
    os.system('cls' if os.name == 'nt' else 'clear')


def current_lists():
    """Prepare lists for date and name searches."""
    entries = Entry.select().order_by(Entry.user_name.desc())
    emp_num = 1
    staff_list = OrderedDict([
    ('1', 'placeholder')
    ])
    for entry in entries:
        if entry.user_name in staff_list.values():
            continue
        else:
            staff_list[str(emp_num)] = entry.user_name
            emp_num += 1

    entries = Entry.select().order_by(Entry.timestamp.desc())
    date_iter = 1
    date_list = OrderedDict([
    ('1', '01/01/1901')
    ])
    for entry in entries:
        if entry.timestamp.date() in date_list.values():
            continue
        else:
            date_list[str(date_iter)] = entry.timestamp.date()
            date_iter += 1

    return staff_list, date_list


def reset_view_list():
    view_list = OrderedDict([
    ('1', 'view_entry')
    ])
    return view_list


def name_check(name):
    if re.match(r'(\w+ \w+)', name):
        return True
    else:
        input('Please enter first and last name for employee.')
        return False


def task_check(task):
    if isinstance(task, str):
        return True
    else:
        input('Task name must be string.')
        return False


def minute_check(minutes):
    try:
        int(minutes)
    except ValueError:
        input('Invalid integer. Press enter to try again.')
        return False
    else:
        return True


def delete_entry(entry):
    """Delete an entry."""
    try:
        deleter = Entry.get(Entry.user_name==entry.user_name,
                            Entry.task_name==entry.task_name,
                            Entry.timestamp==entry.timestamp)
        deleter.delete_instance()
        print('Entry deleted.')
        return True
    except DoesNotExist:
        return False
    
    


def edit_entry(entry):
    """Edit an entry."""
    updater = Entry.get(Entry.user_name==entry.user_name,
                        Entry.task_name==entry.task_name,
                        Entry.timestamp==entry.timestamp)
    print("{}'s entry, {}.".format(entry.user_name, entry.task_name))

    entry_adding = 1
    while entry_adding:
        new_task = ''
        new_task = input('Edit task name, or hit enter to skip.\n> ')
        new_minutes = ''
        new_minutes = input('Edit integer of minutes, or enter to skip.\n> ')
        new_date = ''
        print('Original Timestamp: ' + entry.timestamp.strftime('%m/%d/%Y'))
        new_date = input("Type new date in MM/DD/YYYY format. Or enter to skip.")

        if isinstance(new_task, str):
            pass
        else:
            input('Employee name and task name must be strings.')
            continue

        if new_minutes:
            if minute_check(new_minutes):
                pass
            else:
                continue

        if new_date != '':
            try:
                new_dto = datetime.datetime.strptime(new_date,
                                           "%m/%d/%Y")
            except ValueError:
                input('Invalid date. Press enter to retry.')
                continue

        new_notes = ''
        if input('Any notes? [y/N]').upper().strip() == "Y":
            print('Type notes here. Press "ctrl+d" when finished.')
            add_notes = sys.stdin.read().strip()
    
        clear_screen()
        print('Name: ' + entry.user_name)
        if new_task != '':
            print('Task: ' + new_task)
        else:
            print('Task: ' + entry.task_name)
        if new_minutes != '':
            print('Minutes: ' + new_minutes)
        else:
            print('Minutes: ' + str(entry.task_minutes))
        if new_notes:
            if len(new_notes) > 50:
                print('Notes: ' + new_notes[:50] + '. . . ')
            else:
                print('Notes: ' + new_notes)

        if input('Save entry? [Y/n]\n> ') != 'n':
            if new_task != '':
                updater.task_name = new_task
            if new_minutes != '':
                updater.task_minutes = new_minutes
            if new_notes != '':
                updater.task_notes = new_notes
            if new_dto != '':
                updater.timestamp = new_dto

            savor = save_existing(updater)
            if savor:
                input("Saved succesfully! Hit enter to continue.")
            else:
                input("Hit enter to return to previous menu.")
            entry_adding -= 1


def view_entry(search_query=None, search_item=None, fdate=None, ldate=None):
    """View entries."""
    entries = Entry.select().order_by(Entry.timestamp.desc())

    if search_query:
        if search_query == 'user_name':
            entries = entries.where((Entry.user_name == search_item))
        elif search_query == 'task_term':
            entries = entries.where(
                Entry.task_name.contains(search_item) |
                Entry.task_notes.contains(search_item))
        elif search_query == 'date':
            # entries = entries.where(Entry.timestamp.contains(search_item))
            # begin date refactor
            entries = entries.where(
                (Entry.timestamp.year == search_item.year) &
                (Entry.timestamp.month == search_item.month) &
                (Entry.timestamp.day == search_item.day))
            # end date refactor
        elif search_query == 'date_range':
            entries = entries.where(
                (Entry.timestamp >= fdate) &
                (Entry.timestamp <= ldate))
        elif search_query == 'task_minutes':
            entries = entries.where(
                (Entry.task_minutes == search_item))
        elif search_query == 'task_minutes_more':
            entries = entries.where(
                (Entry.task_minutes >= search_item))
        elif search_query == 'task_minutes_less':
            entries = entries.where(
                (Entry.task_minutes <= search_item))
        else:
            print('Something happened. "search_query" variable not recognized.')
            input('Press enter to return to menu.')

    available_entries = []
    # refactor of e_list
    available_entries = list(entries)
    # end refactor
    #for entry in entries:
    #    e_list.append("item")
    view_list = reset_view_list()
    if len(available_entries) > 0:
        view_num = 1
        for entry in entries:
            if entry in view_list.values():
                continue
            else:
                view_list[str(view_num)] = entry
                view_num += 1
        view_num = 1
        while view_num < (len(view_list)+1):
            clear_screen()
            vts = view_list[str(view_num)].timestamp.strftime('%A %B %d, %Y %I:%M%p')
            print(vts)
            print('='*len(vts))
            print("Recorded by: " + view_list[str(view_num)].user_name)
            print("Task: " + view_list[str(view_num)].task_name)
            print("Minutes: " + str(view_list[str(view_num)].task_minutes))
            print("Additional Notes: " + view_list[str(view_num)].task_notes)
            print('\n\n' + '=' * len(vts))
            print('N) Next entry')
            print('p) Previous entry')
            print('e) Edit entry')
            print('d) Delete entry')
            print('q) Return to menu')

            next_action = input('Action: \n[N/p/e/d/q]: ').lower().strip()
            if next_action == 'q':
                break
            elif next_action == 'e':
                edit_entry(view_list[str(view_num)])
                break
            elif next_action == 'd':
                if input('Delete entry. Are you sure? y/N ').lower() == 'y':
                    delete_entry(view_list[str(view_num)])
                    break
                else:
                    view_num += 0
            elif next_action == 'p':
                if view_num > 1:
                    view_num -= 1
                else:
                    input("Can't go further than that. (Enter to continue.)")
            else:
                if view_num < len(view_list):
                    view_num += 1
                else:
                    input("That's all we could find. (Enter to continue.)")
    else:
        print('Sorry. No matching entries found.')
        input('Press enter to return to main menu.')


def search_staff():
    """Seach by employee."""
    ss_choice = input('Search by name or see list? [n/L] \n>')
    target = ""
    staff_list, date_list = current_lists()
    if ss_choice.lower().strip() == 'n':
        spec_name = 1
        while spec_name:
            print("Which employee's logs would you like to see?")
            target = input("Please enter full or partial name. \n> ")
            if target in staff_list.values():
                view_entry(search_query="user_name",
                           search_item="target")
                break

            emp_list = []
            for emp in staff_list.values():
                if re.search(target.lower(), emp.lower()):
                    emp_list.append(emp)

            if len(emp_list) == 1:
                view_entry(search_query="user_name",
                           search_item=emp_list[0])
                break

            elif len(emp_list) > 1:
                e_num = 1
                for emp in emp_list:
                    print(str(e_num) + ") " + emp)
                    e_num += 1
                fin_loop = 1
                while fin_loop:
                    fin = input('''
This is what we found. Please select a number.
> ''')
                    fin = int(fin) - 1
                    if emp_list[fin]:
                        view_entry(search_query="user_name",
                                   search_item=emp_list[fin])
                        spec_name -= 1
                        fin_loop -= 1
                    else:
                        input('Invalid selection. Press enter to retry.')

            else:
                print('Sorry. No names matched that search.')
                again = input('Would you like to search another name? [Y/n]')
                if again.lower() == 'n':
                    spec_name -= 1
                else:
                    continue

    else:
        clear_screen()

        name_pick = 1
        while name_pick:
            for key, value in staff_list.items():
                print(key + ") " + value)

            emp_choice = input('Please choose a number from the list.\n> ')
            if emp_choice in staff_list.keys():
                view_entry(search_query="user_name",
                           search_item=staff_list[emp_choice])
                name_pick -= 1
            else:
                input('Invalid selection.  Press enter to retry.')
                clear_screen()


def search_date():
    """Search by log date(s)."""
    sd_choice = input('Check specific date range or see list? [r/L] \n>')
    if sd_choice.lower().strip() == 'r':
        spec_date = 1
        while spec_date:
            clear_screen()
            target_range = input('''
Please enter date range in following format:
"MM/DD/YYYY-MM/DD/YYYY"
Range will find from midnight of first date, to midnight of the last date.
So, if you want to search New Year's Day 2018, type "01/01/2018-01/02/2018"
> ''')
            targets = target_range.split(sep='-')
            try:
                first_date = datetime.datetime.strptime(targets[0],
                                                        "%m/%d/%Y")
                last_date = datetime.datetime.strptime(targets[1],
                                                       "%m/%d/%Y")
            except ValueError:
                input('Invalid date range. Press enter to retry.')
            else:
                if first_date <= last_date:
                    spec_date -= 1
                else:
                    print('Invalid date range.')
                    print('Please enter two dates, earliest first.')
                    input('Press enter to retry.')
        view_entry(search_query='date_range',
                   fdate=first_date,
                   ldate=last_date)
    else:
        clear_screen()
        staff_list, date_list = current_lists()
        date_pick = 1
        while date_pick:
            for key, value in date_list.items():
                print(key + ") " + str(value))

            date_choice = input('Please choose a number from the list.\n> ')
            if date_choice in date_list.keys():
                view_entry(search_query="date",
                           search_item=date_list[date_choice])
                date_pick -= 1
            else:
                input('Invalid selection.  Press enter to retry.')
                clear_screen()


def search_minutes():
    """Search by number of task minutes."""
    # As a user of the script, if finding by time spent, I should be allowed to enter the amount of time spent on the project and then be presented with entries containing that amount of time spent.
    # By exact minutes or by range?
    minu_loop = 1
    while minu_loop:
        target = ''
        target = input("Please type a number of minutes.\n> ")
        if target != '':
            if re.match(r'\d+', target):
                # if re.search(r'\-', target):
                #    view_entry(search_query='task_minutes_less',
                #               search_item=target)
                # elif re.search(r'\+', target):
                #    view_entry(search_query='task_minutes_more',
                #                search_item=target)
                view_entry(search_query='task_minutes',
                           search_item=int(target))
                    # ValueError: invalid literal for int() with base 10: '%5%'
                    # '5 was the number i attempted.
                break
            else:
                print('Invalid entry. Please enter only integers.')
                input('Press enter to retry.')
        else:
            print('Invalid entry. Please enter only integers.')
            input('Press enter to retry.')


def search_term():
    """Search by task keyword(s)."""
    # As a user of the script, if finding by a search term, I should be allowed to enter a string and then be presented with entries containing that string in the task name or notes.
    term_loop = 1
    while term_loop:
        target = input('Please type a search term.')
        if target != '':
            if re.match(r'\S', target):
                view_entry(search_query='task_term', search_item=target)
                break
        print('Search term may not be blank or begin with a space.')
        input('Hit enter to retry.')


def search_entries():
    """Search existing entries."""
    # As a user of the script, if I choose to find a previous entry, I should be presented with four options: find by employee, find by date, find by time spent, find by search term.
    clear_screen()
    find = ''
    sm_loop = 1
    while sm_loop:
        print('How would you like to search?')
        for key, value in search_menu.items():
            find_buttons = '{}) {}'.format(key.upper(), value.__doc__)
            print(find_buttons)
            print('-' * len(find_buttons))
            # .__doc__ will read docstrings of the menu functions.
        find = input("\nAction: ").lower().strip()
        if find in search_menu:
            sm_loop -= 1
        else:
            input('Invalid selection. Press enter to retry.')
    search_menu[find]()
    # view_entries(input('Search Query: '))


def save_new(user_name, task_name, task_minutes, task_notes):
    try:
        Entry.create(user_name=user_name,
                     task_name=task_name,
                     task_minutes=task_minutes,
                     task_notes=task_notes)
    except:
        print('Unexpected Error: ', sys.exc_info())
        print('Unable to save.')
        return False
    else:
        print('Entry should be added!')
        return True


def save_existing(update_me):
    try:
        update_me.save()
        return True
    except:
        print('Unexpected Error: ', sys.exc_info())
        print('Cannot confirm save.')
        return False


def add_entry():
    """Add new entry to work log."""
    clear_screen()
    entry_adding = 1
    while entry_adding:

        add_name = input('Please enter full name.\n> ')
        add_task = input('What task did you work on?\n> ')
        add_minutes = input('How many minutes were spent?\n> ')

        if name_check(add_name):
            pass
        else:
            continue

        if isinstance(add_name + add_task, str):
            pass
        else:
            input('Employee name and task name must be strings.')
            continue

        if minute_check(add_minutes):
            pass
        else:
            continue

        add_notes = ''
        if input('Any notes? [y/N]').upper().strip() == "Y":
            print('Type notes here. Press "ctrl+d" when finished.')
            add_notes = sys.stdin.read().strip()
    
        clear_screen()
        print('Name: ' + add_name)
        print('Task: ' + add_task)
        print('Minutes: ' + add_minutes)
        if add_notes:
            if len(add_notes) > 50:
                print('Notes: ' + add_notes[:50] + '. . . ')
            else:
                print('Notes: ' + add_notes)
        if input('Save entry? [Y/n]\n> ') != 'n':
            save_new(add_name, add_task, add_minutes, add_notes)
            input('Hit enter key to continue.')
            entry_adding -= 1


def main_menu():
    """Show the menu loop."""
    choice = ''

    while choice.lower() != 'q':
        clear_screen()
        staff_list, date_list = current_lists()
        quitter = 'Enter "q" to quit.'
        print('Welcome to the new Work Log Database!')
        print(quitter)
        print('-' * len(quitter))
        for key, value in menu.items():
            menu_buttons = '{}) {}'.format(key.upper(), value.__doc__)
            print(menu_buttons)
            print('-' * len(menu_buttons))
            # .__doc__ will read docstrings of the menu functions.
        print(date_list)
        choice = input("\nAction: ").lower().strip()

        if choice in menu:
            menu[choice]()


search_menu = OrderedDict([
    ('1', search_staff),
    ('2', search_date),
    ('3', search_minutes),
    ('4', search_term)
])


menu = OrderedDict([
    ('a', add_entry),
    ('v', view_entry),
    ('s', search_entries)
])

staff_list = OrderedDict([
    ('1', 'placeholder')
])

date_list = OrderedDict([
    ('1', '01/01/1901')
])

view_list = OrderedDict([
    ('1', 'view_entry')
])


if __name__ == '__main__':
    initialize()

    main_menu()
