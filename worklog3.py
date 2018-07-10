"""Work Log DB.
"""


import datetime
import re
import sys

from peewee import *
from models import Entry


class CardCatalog:
    """For viewing, sorting and editing worklog database."""
    # Class attributes weren't being used.  Now deleted.
    # Variables used in functions are different from class attributes.
    def load_entries(self, bycat=None, target=None, datelast=None):
        # Under test.
        # Not sure how to test for it NOT working?
        ent_browse = []
        if bycat == 'minutes':
            ent_from_db = Entry.select().where(
                (Entry.task_minutes == target)).order_by(
                Entry.task_minutes.desc())
        elif bycat == 'term':
            ent_from_db = Entry.select().where(
                Entry.task_name.contains(target) |
                Entry.task_notes.contains(target)).order_by(
                Entry.task_name.desc())
        elif bycat == 'name':
            ent_from_db = Entry.select().where(
                Entry.user_name.contains(target)).order_by(
                Entry.user_name.desc())
            # CharField is NOT case sensitive?
        elif datelast:
            ent_from_db = Entry.select().where(
                (Entry.timestamp >= target) &
                (Entry.timestamp <= datelast)).order_by(
                Entry.timestamp.desc())
        elif bycat == 'date':
            ent_from_db = Entry.select().where(
                (Entry.timestamp.year == target.year) &
                (Entry.timestamp.month == target.month) &
                (Entry.timestamp.day == target.day))
        else:
            ent_from_db = Entry.select().order_by(Entry.timestamp.desc())

        if ent_from_db:
            for entry in ent_from_db:
                new_dict = {'user_name': entry.user_name,
                            'task_name': entry.task_name,
                            'task_minutes': entry.task_minutes,
                            'task_notes': entry.task_notes,
                            'timestamp': entry.timestamp}
                ent_browse.append(new_dict)
            return ent_browse
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
        roster = []
        ent_from_db = Entry.select().order_by(Entry.user_name.desc())
        for entry in ent_from_db:
            roster.append(entry.user_name)
        set_list = set(roster)
        roster = list(set_list)
        return roster

    def generate_datelog(self):
        """Return a list of task dates for easy selection."""
        # Under test.
        datelog = []
        ent_from_db = Entry.select().order_by(Entry.timestamp.desc())
        for entry in ent_from_db:
            datelog.append(entry.timestamp.date())
        set_list = set(datelog)
        datelog = list(set_list)
        return datelog

    def d_range_check(self, tdoves):
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
        if re.match(r'([a-z]+ [a-z]+)', name, re.I):
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

    def fol_check(self, name):
        if re.match(r'[a-z]+$', name, re.I):
            return True
        else:
            return False

    def notes_out(self, notes):
        # Under Test.
        if notes == '':
            pass  # Does this return None as value of notes? Is that a problem?
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
            # Revisit this test?
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
