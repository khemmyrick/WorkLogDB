#!/usr/bin/env python3

"""Work Log: Now with Database!
As of 6:43pm 6/10/18:
Search name function is just starting to work!
User can either type a name in, or see a list of available names.
Planning to approach search date with similar coding.

"""

from collections import OrderedDict
import datetime
import os
import re
import sys

from peewee import *

db = SqliteDatabase('log.db')


class Entry(Model):
    timestamp = DateTimeField(default=datetime.datetime.now)
    user_name = CharField(max_length=500)
    task_name = CharField(max_length=1000)
    task_minutes = IntegerField(default=0)
    # I'm not sure if IntegerField takes a "max_length" argument.
    # But, 480 minutes is an 8 hour day, so I figure no task should last longer than 999 minutes.  There's probably an integer-specific alternative to max_length that I can actually set to 480?
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
    entries = Entry.select().order_by(Entry.user_name.desc())
    emp_num = 1
    for entry in entries:
        if entry.user_name in staff_list.values():
            continue
        else:
            staff_list[str(emp_num)] = entry.user_name
            emp_num += 1
    entries = Entry.select().order_by(Entry.timestamp.desc())
    date_iter = 1
    for entry in entries:
        if str(entry.timestamp.date()) in date_list.values():
            continue
        else:
            date_list[str(date_iter)] = str(entry.timestamp.date())
            date_iter += 1
        
    return staff_list, date_list

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
    if input('Delete entry. Are you sure? y/N ').lower() == 'y':
        entry.delete_instance()
        print('Entry deleted.')


def edit_entry(entry):
    """Edit an entry."""
    pass


def view_entries(*args):
    """View entries."""
    # This is my attempt to update the work_log.py from TP3.
    # Seems to be failing miserably for this project.
    entries = Entry.select().order_by(Entry.timestamp.desc())
    
    if args[0] == 'user_name':
        entries = entries.where(Entry.user_name.contains(args[1]))
    elif args[0] == 'task_name':
        entries = entries.where(Entry.task_name.contains(args[1]))
    elif args[0] == 'task_minutes':
        entries = entries.where(Entry.task_minutes.contains(args[1]))
    elif args[0] == 'task_notes':
        entries = entries.where(Entry.task_notes.contains(args[1]))
    elif args[0] == 'timestamp':
        entries = entries.where(Entry.timestamp.contains(args[1]))
    elif args[0] == 'date_range':
        pass

    e_iter = 0
    results_loop = 1
    while results_loop:
        clear_screen()
        print(str(len(entries)) + " results match your search.")
        print("Recorded by: " + entries[e_iter].user_name)
        print("Date: " + entries[e_iter].timestamp.strftime('%A %B %d'))
        print("Task: " + entries[e_iter].task_name)
        print("Time Spent: " + str(entries[e_iter].task_minutes))
        print("Notes: " + entries[e_iter].task_notes + "\n")
        print("Entry {} of {}.".format((e_iter + 1), len(entries)))

        if e_iter == 0 and e_iter < (len(results) - 1):
            review_action = input('''
[N]ext Item,
[E]dit Item, [D]elete Item, [R]eturn to Search Menu
> ''')
        elif e_iter == (len(results) - 1) and e_iter > 0:
            review_action = input('''
[P]revious Item,
[E]dit Item, [D]elete Item, [R]eturn to Search Menu
> ''')
        elif e_iter == (len(results) - 1) and e_iter == 0:
            review_action = input('''
[E]dit Item, [D]elete Item, [R]eturn to Search Menu
> ''')
        else:
            review_action = input('''
[N]ext Item, [P]revious Item,
[E]dit Item, [D]elete Item, [R]eturn to Search Menu
> ''')

        if review_action.upper() == "N" and entry < len(results) - 1:
            entry += 1
        elif review_action.upper() == "P" and entry > 0:
            entry -= 1
        elif review_action.upper() == "E":
            edit_entry(results[entry])
            results_loop -= 1
        elif review_action.upper() == "D":
            delete_entry(results[entry])
            results_loop -= 1
        elif review_action.upper() == "R":
            results_loop -= 1
        else:
            input("Error: Invalid selection. Press enter to try again.")

            # The block above in SQL would look like:
            # SELECT *FROM entry WHERE user_name LIKE '%search_query%' ORDER BY timestamp DESC
            # e_iter = 1
            # for entry in entries:
            #   clear_screen()
            #    timestamp = entry.timestamp.strftime('%A %B %d, %Y %I:%M%p')
            #    print(timestamp)
            #    print('='*len(timestamp))
            #    print(entry.user_name)
            #    print(entry.task_name + ': ' + str(entry.task_minutes))
            #    print('-' * len(entry.task_name))
            #    if entry.task_notes:
            #        print('Notes: ' + entry.task_notes)
            #    print('\n\n' + '=' * len(timestamp))
            #    if len(entries) > e_iter:
            #        print('n) Next entry')
            #    if e_iter > 1:
            #        print('p) Previous entry')
            #    print('d) Delete entry')
            #    print('q) Return to menu')
        
            #    next_action = input('Action: [N/p/d/q]: ').lower().strip()
            #    if next_action == 'q':
            #        break
            #    elif next_action == 'd':
            #        delete_entry(entry)
            #    elif next_action == 'n':


def view_entry(search_query=None, search_item=None):
    """View entries."""
    # From diary.py file from database course.
    entries = Entry.select().order_by(Entry.timestamp.desc())
    
    if search_query:
        if search_query == 'user_name':
            entries = entries.where(Entry.user_name.contains(search_item))
        elif search_query == 'task_name':
            entries = entries.where(Entry.task_name.contains(search_item))
        elif search_query == 'date':
            entries = entries.where(Entry.timestamp.contains(search_query))
        elif search_query == 'task_notes':
            entries = entries.where(Entry.task_notes.contains(search_query))
        elif search_query == 'task_minutes':
            entries = entries.where(Entry.task_minutes.contains(search_query))

    # The block above in SQL would look like:
    # SELECT *FROM entry WHERE thought LIKE '%search_query%' ORDER BY timestamp DESC
    if entries:
        for entry in entries:
            clear_screen()
            timestamp = entry.timestamp.strftime('%A %B %d, %Y %I:%M%p')
            print(timestamp)
            print('='*len(timestamp))
            print("Recorded by: " + entry.user_name)
            print("Task: " + entry.task_name)
            print("Minutes spent on task: " + str(entry.task_minutes))
            print("Additional Notes: " + entry.task_notes)
            print('\n\n' + '=' * len(timestamp))
            print('n) Next entry')
            print('d) Delete entry')
            print('q) Return to menu')
    
            next_action = input('Action: [N/d/q]: ').lower().strip()
            if next_action == 'q':
                break
            elif next_action == 'd':
                delete_entry(entry)
    else:
        print('Sorry. No matching entries found.')
        input('Press enter to return to main menu.')


def search_staff():
    """Seach by employee."""
    # As a user of the script, if finding by employee, I should be allowed to enter employee name and then be presented with entries with that employee as their creator.
    # If multiple employees share a name (e.g. multiple people with the first name Beth), a list of possible matches is given.
    ss_choice = input('Search by name or see list? [n/L] \n>')
    target = ""
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
            # entries = Entry.select().order_by(Entry.user_name.desc())
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
    pass


def search_minutes():
    """Search by number of task minutes."""
    # As a user of the script, if finding by time spent, I should be allowed to enter the amount of time spent on the project and then be presented with entries containing that amount of time spent.
    # By exact minutes or by range?
    pass


def search_term():
    """Search by task keyword(s)."""
    pass


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


def add_entry():
    """Add new entry to work log."""
    # Use unittest instead of doctest to avoid breaking KL-style menu?
    clear_screen()
    # As a user of the script, if I choose to enter a new work log, no entry fields (except notes) may remain blank.
    an_loop = 1
    while an_loop:
        add_name = input('Please enter full name.\n> ')
        if re.match(r'(\w+ \w+)', add_name):
            an_loop -= 1
        else:
            input('Invalid entry.  Press enter to retry.')

    at_loop = 1
    while at_loop:
        add_task = input('What task did you work on?\n> ')
        if re.match(r'\S+', add_task):
            at_loop -= 1
        else:
            input('Invalid task name.  Press enter to try again.')

    am_loop = 1
    while am_loop:
        add_minutes = input('How many minutes did you spend on this task?\n> ')
        legit = minute_check(add_minutes)
        if legit:
            am_loop -= 1
        else:
            continue

    add_notes = ''
    if input('Any notes? [y/N]').upper().strip() == "Y": 
        print('Type notes here. Press "ctrl+d" when finished.\n> ')
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

    add_ts = datetime.datetime.now()
    ats_string = add_ts.strftime('%A %B %d, %Y %I:%M%p')
    print(ats_string)
    print('-' * len(ats_string))
    if input('Save entry? [Y/n]\n> ') != 'n':
        Entry.create(user_name=add_name,
                    task_name=add_task,
                    task_minutes=add_minutes,
                    task_notes=add_notes,
                    timestamp=add_ts)
        print("Saved succesfully!")


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


if __name__ == '__main__':
    initialize()
    
    main_menu()
