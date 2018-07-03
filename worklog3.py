"""Work Log DB.
Return True, False, Item or None.
Every function should return something."""


from collections import OrderedDict
import datetime
import os
import re
import sys

from peewee import *
from models import Entry


# db = SqliteDatabase('log.db')


class CardCatalog:
    """For viewing, sorting and editing worklog database."""
    title = 'Welcome to the Library of Employee Productivity!'
    ent_from_db = Entry.select()
    ent_by_timestamp = Entry.select().order_by(Entry.timestamp.desc())
    ent_by_taskname = Entry.select().order_by(Entry.task_name.desc())
    ent_by_minutes = Entry.select().order_by(Entry.task_minutes.desc())
    roster = []
    datelog = []
    ent_browse = []
    total_ent = Entry.select().count()
    curr_ent = 0
    new_dict = {'user_name': 'John Doe',
                'task_name': 'Work Task',
                'task_minutes': 1,
                'task_notes': ''}
    # target_entry

    def load_entries(self, bycat=None, target=None):
        # Under test.
        # Not sure how to test for it NOT working?
        self.ent_browse = []
        if bycat == 'minutes':
            self.ent_from_db = Entry.select().where(
                (Entry.task_minutes == target)).order_by(
                Entry.task_minutes.desc())
        elif bycat == 'term':
            self.ent_from_db = Entry.select().where(
                Entry.task_name.contains(target) |
                Entry.task_notes.contains(target)).order_by(
                Entry.task_name.desc())
        elif bycat == 'name':
            self.ent_from_db = Entry.select().where(
                Entry.user_name.contains(target)).order_by(
                Entry.user_name.desc())
            # CharField is NOT case sensitive?
        else:
            self.ent_from_db = Entry.select().order_by(Entry.timestamp.desc())

        for entry in self.ent_from_db:
            self.new_dict = {'user_name': entry.user_name,
                             'task_name': entry.task_name,
                             'task_minutes': entry.task_minutes,
                             'task_notes': entry.task_notes,
                             'timestamp': entry.timestamp}
            self.ent_browse.append(self.new_dict)
        return self.ent_browse

    def delete_entry(self, entry):
        """Delete an entry."""
        # Under test!
        try:
            deleter = Entry.get(Entry.user_name==entry['user_name'],
                                Entry.task_name==entry['task_name'],
                                Entry.task_minutes==entry['task_minutes'],
                                Entry.timestamp==entry['timestamp'])
            deleter.delete_instance()
            print('Entry deleted.')
            return True
        except DoesNotExist:
            return False

    def generate_blank_entry(self):
        self.new_dict = {'user_name': 'John Doe',
                    'task_name': 'Work Task',
                    'task_minutes': 1,
                    'task_notes': ''}
        return self.new_dict

    def generate_roster(self):
        # This code is returning individual LETTERS rather than strings for some reason??
        self.roster = []
        self.ent_from_db = Entry.select().order_by(Entry.user_name.desc())
        for entry in self.ent_from_db:
            self.roster.append(entry.user_name)
        set_list = set(self.roster)
        self.roster = list(set_list)
        print(self.roster)
        return self.roster

    def generate_datelog(self):
        # Like gen_roster, this code is trying to iterate character by character through individual dates
        # instead of adding each date to the list as intended. 
        for entry in self.ent_by_timestamp:
            self.datelog += entry.timestamp.date()
        set_list = set(self.datelog)
        self.datelog = list(set_list)
        return self.datelog
    
    def save_new(self, user_name, task_name, task_minutes, task_notes):
        """Save a new entry."""
        # Under test.
        try:
            Entry.create(user_name=user_name,
                         task_name=task_name,
                         task_minutes=task_minutes,
                         task_notes=task_notes)
        except ValueError:
            print('Unexpected values found in entry.')
            print('Please carefully follow all instructions.')
            print('Unable to save.')
            return False
        else:
            print('Entry should be added!')
            return True

    def name_check(self, name):
        """Check for a string consistent with a first and last name."""
        # Under test.
        if re.match(r'(\w+ \w+)', name):
            return True
        else:
            return False

    def minute_check(self, minutes):
    # Under test.
        try:
            int(minutes)
        except ValueError:
            return False
        else:
            return True

    def notes_out(self, notes):
        # Under Test.
        if notes == '':
            pass
        elif len(notes) > 40:
            return 'Notes: ' + notes[:50] + '. . . '
        else:
            return 'Notes: ' + notes

    def acquire_target(self, entry):
        try:
            output = Entry.get(Entry.user_name==entry['user_name'],
                               Entry.task_name==entry['task_name'],
                               Entry.task_minutes==entry['task_minutes'],
                               Entry.timestamp==entry['timestamp'])
        except (DoesNotExist, StopIteration):
            # Under test.  Sort of.
            # These may not be the correct exceptions?
            return False
        else:
            return output

    def save_edits(self, target_entry):
        try:
            # Under Test.
            target_entry.save()
            return True
        except:
            # Under test.  Sort of.
            print('Unexpected Error: ', sys.exc_info())
            print('Cannot confirm save.')
            return False

#    def start(self):
#        wlux.main_menu()
        

# if __name__ == '__main__':
#    libra = CardCatalog()
#    libra.start()
