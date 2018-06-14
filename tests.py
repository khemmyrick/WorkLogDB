from collections import OrderedDict
import datetime
import os
import re
import sys
import unittest

from peewee import *
import work_log2


class EntryTests(unit.TestCase):
    def setUp(self):
        self.adventure = work_log2.Entry.create(
            user_name='Steven Universe',
            task_name='Contain the Cluster',
            task_minutes=11,
            task_notes="""
I've got you.  You've got this.  We've all got each other!""",
            timestamp=datetime.datetime.now())
        # Test that this model has been created.
        # Test that this model can link to a test database (NOT log.db).
        # Test that this model instance can be created in, and edited at the database.

class ListTests(unittest.TestCase):
    def setUp(self):
        staff_list = OrderedDict([
            ('1', 'placeholder')
        ])
        date_list = OrderedDict([
            ('1', '01/01/1901')
        ])
        # Set up test database with entries for test_current_list to retrieve.

    def test_current_lists(self):
        entries = work_log2.Entry.select().order_by(
            work_log2.Entry.user_name.desc())
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
        assertGreater(len(staff_list), 1)

        entries = work_log2.Entry.select().order_by(
            work_log2.Entry.timestamp.desc())
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
        assertGreater(len(date_list),  1)
