"""Work Log DB.
"""


import datetime
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

    def load_entries(self, bycat=None, target=None, datelast=None):
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
        elif datelast:
            self.ent_from_db = Entry.select().where(
                (Entry.timestamp >= target) &
                (Entry.timestamp <= datelast)).order_by(
                Entry.timestamp.desc())
        elif bycat == 'date':
            self.ent_from_db = Entry.select().where(
                (Entry.timestamp.year == target.year) &
                (Entry.timestamp.month == target.month) &
                (Entry.timestamp.day == target.day))
        else:
            self.ent_from_db = Entry.select().order_by(Entry.timestamp.desc())

        if self.ent_from_db:
            for entry in self.ent_from_db:
                self.new_dict = {'user_name': entry.user_name,
                                 'task_name': entry.task_name,
                                 'task_minutes': entry.task_minutes,
                                 'task_notes': entry.task_notes,
                                 'timestamp': entry.timestamp}
                self.ent_browse.append(self.new_dict)
            return self.ent_browse
        else:
            print("Sorry. No entries found matching your query.")
            return False

    def delete_entry(self, entry):
        """Delete an entry."""
        # Under test!
        try:
            deleter = Entry.get(
                Entry.user_name == entry['user_name'],
                Entry.task_name == entry['task_name'],
                Entry.task_minutes == entry['task_minutes'],
                Entry.timestamp == entry['timestamp']
            )
            deleter.delete_instance()
            print('Entry deleted.')
            return True
        except DoesNotExist:
            return False

    def generate_roster(self):
        """Return a list of staff with worklog entries."""
        # Under test.
        self.roster = []
        self.ent_from_db = Entry.select().order_by(Entry.user_name.desc())
        for entry in self.ent_from_db:
            self.roster.append(entry.user_name)
        set_list = set(self.roster)
        self.roster = list(set_list)
        return self.roster

    def generate_datelog(self):
        """Return a list of task dates for easy selection."""
        # Under test.
        self.datelog = []
        self.ent_from_db = Entry.select().order_by(Entry.timestamp.desc())
        for entry in self.ent_from_db:
            self.datelog.append(entry.timestamp.date())
        set_list = set(self.datelog)
        self.datelog = list(set_list)
        return self.datelog

    def d_range_check(self, tdoves):
        # TEST ME!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
        if re.match(r'(\d{2}/\d{2}/\d{4}\-\d{2}/\d{2}/\d{4})', tdoves):
            return True
        else:
            return False

    def date_check(self, phoenix):
        """Create a datetime object from a string. Or return False."""
        # Under Test
        try:
            day_in_q = datetime.datetime.strptime(
                phoenix,
                "%m/%d/%Y"
            )
        except ValueError:
            return False
        else:
            return day_in_q

    def save_new(self,
                 user_name,
                 task_name,
                 task_minutes,
                 task_notes):
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
        """Returns True if string can be parsed as integer."""
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
        """Return entry from database for editing."""
        try:
            output = Entry.get(
                Entry.user_name == entry['user_name'],
                Entry.task_name == entry['task_name'],
                Entry.task_minutes == entry['task_minutes'],
                Entry.timestamp == entry['timestamp']
            )
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
