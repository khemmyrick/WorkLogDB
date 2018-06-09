#!/usr/bin/env python3

"""Work Log: Now with Database!
Basic skeleton of this version is from:
1. Project 3 Work Log
2. diary.py from Using Databases in Python
Presently, main_menu, and add_entry functions are working.
view_entry is working enough for me to verify that add_entry is indeed working.

"""

from collections import OrderedDict
import datetime
import os
import re
import sys

from peewee import *

db = SqliteDatabase('log.db')


class Entry(Model):
    user_name = CharField(max_length=500, unique=True)
    task_name = CharField(max_length=1000)
    task_minutes = IntegerField(default=0)
    # I'm not sure if IntegerField takes a "max_length" argument.
    # But, 480 minutes is an 8 hour day, so I figure no task should last longer than 999 minutes.  There's probably an integer-specific alternative to max_length that I can actually set to 480?
    task_notes = TextField()
    timestamp = DateTimeField(default=datetime.datetime.now)

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


def view_entry(search_query=None):
    """View entries."""
    entries = Entry.select().order_by(Entry.timestamp.desc())
    
    if search_query:
        entries = entries.where(Entry.user_name.contains(search_query))
    # The block above in SQL would look like:
    # SELECT *FROM entry WHERE user_name LIKE '%search_query%' ORDER BY timestamp DESC
    
    for entry in entries:
        clear_screen()
        timestamp = entry.timestamp.strftime('%A %B %d, %Y %I:%M%p')
        print(timestamp)
        print('='*len(timestamp))
        print(entry.user_name)
        print(entry.task_name + ': ' + str(entry.task_minutes))
        print('-' * len(entry.task_name))
        if entry.task_notes:
            print('Notes: ' + entry.task_notes)
        print('\n\n' + '=' * len(timestamp))
        print('n) Next entry')
        print('d) Delete entry')
        print('q) Return to menu')

        next_action = input('Action: [N/d/q]: ').lower().strip()
        if next_action == 'q':
            break
        elif next_action == 'd':
            delete_entry(entry)


def search_entries():
    """Search existing entries."""
    # As a user of the script, if I choose to find a previous entry, I should be presented with four options: find by employee, find by date, find by time spent, find by search term.
    clear_screen()
    view_entry(input('Search Query: '))


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
        quitter = 'Enter "q" to quit.'
        print(quitter)
        print('-' * len(quitter))
        for key, value in menu.items():
            menu_buttons = '{}) {}'.format(key.upper(), value.__doc__)
            print(menu_buttons)
            print('-' * len(menu_buttons))
            # .__doc__ will read docstrings of the menu functions.
        choice = input("\nAction: ").lower().strip()
        
        if choice in menu:
            menu[choice]()


menu = OrderedDict([
    ('a', add_entry),
    ('v', view_entry),
    ('s', search_entries)
])

if __name__ == '__main__':
    initialize()
    main_menu()
