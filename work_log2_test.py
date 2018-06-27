from collections import OrderedDict
import datetime
import os
import re
import sys
import unittest
from unittest.mock import patch, MagicMock

from peewee import *
import work_log2


# Only need to test that peewee database functions are being called, not if they work.
# May not even need to check that?
TEST_DB = SqliteDatabase(':memory:') # Save an SQL database into RAM memory.
# Not sure if this SqliteDatabase() call actually works.
# Everytime I run this testfile, my log.db seems to add a copy of my setUp entry to log.db.
TEST_DB.connect()
TEST_DB.create_tables([work_log2.Entry], safe=True)


class EntryTests(unittest.TestCase):
    """Test that entries can be added, edited, and deleted."""
    # Not sure if this patch is actually doing anything.
    # The TESTS are working though.
    @patch('work_log2.db')
    def setUp(self, TEST_DB):
        self.stubby = work_log2.Entry.create(
            user_name='Kit Williams', 
            task_name='Masquerade',
            task_minutes=43200,
            task_notes='something no one has done'
        )

    def test_current_lists(self):
        """Test list pre-search function."""
        staff_list, date_list = work_log2.current_lists()
        self.assertEqual(staff_list['1'], 'Kit Williams')
        self.assertEqual(date_list['1'], self.stubby.timestamp.date())

    def test_reset_view_list(self):
        view_list = work_log2.reset_view_list()
        self.assertEqual(view_list,
                          OrderedDict([
                    ('1', 'view_entry')
                ]))

    def test_name_check_good(self):
        checked = work_log2.name_check('Kit Williams')
        self.assertTrue(checked)

    @patch('builtins.input', MagicMock()) # I DID IT! I DID A MOCK!
    def test_name_check_bad(self):
        checked = work_log2.name_check('Masquerade')
        # Regex check names must include a first and last name, with a space.
        self.assertFalse(checked)

    def test_delete_entry(self):
        eraser = work_log2.delete_entry(self.stubby)
        self.assertTrue(eraser)

    @unittest.expectedFailure
    def test_delete_bad_entry(self):
        condemned = work_log2.Entry.get(
            work_log2.Entry.user_name=='Norm Fakey',
            work_log2.Entry.task_name=='Fake Task',
            work_log2.Entry.task_minutes==100000,
            work_log2.Entry.timestamp==datetime.datetime.now())
        eraser = work_log2.delete_entry(condemned)
        self.assertFalse(eraser)


    def test_save_new(self):
        saver = work_log2.save_new(
            self.stubby.user_name,
            self.stubby.task_name,
            self.stubby.task_minutes,
            self.stubby.task_notes
        )
        self.assertTrue(saver)

    def test_save_existing(self):
        savor = work_log2.save_existing(self.stubby)
        self.assertTrue(savor)

    def test_task_check_good(self):
        checked = work_log2.task_check('Masquerade')
        self.assertTrue(checked)

    @patch('builtins.input', MagicMock())
    def test_task_check_bad(self):
        checked = work_log2.task_check(5)
        self.assertFalse(checked)

    def test_minute_check_good(self):
        checked = work_log2.minute_check('2')
        self.assertTrue(checked)

    @patch('builtins.input', MagicMock())
    def test_minute_check_bad(self):
        checked = work_log2.minute_check('the number two')
        # User input passed to minute_check will always be str.
        # Therefore, appropriate input can be parsed as int,
        # But will never be a bool.  So no need to check for bool error.
        self.assertFalse(checked)

    def test_scrape_username(self):
        entries = work_log2.entry_scrape(
            work_log2.Entry.select().order_by(
                work_log2.Entry.timestamp.desc()
            ),
            search_query='user_name',
            search_item='Kit Williams'
        )
        self.assertIn(self.stubby, entries)

    def test_scrape_task_term_task(self):
        entries = work_log2.entry_scrape(
            work_log2.Entry.select().order_by(
                work_log2.Entry.timestamp.desc()
            ),
            search_query='task_term',
            search_item='Masquerade'
        )
        self.assertIn(self.stubby, entries)

    def test_scrape_task_term_notes(self):
        entries = work_log2.entry_scrape(
            work_log2.Entry.select().order_by(
                work_log2.Entry.timestamp.desc()
            ),
            search_query='task_term',
            search_item='something'
        )
        self.assertIn(self.stubby, entries)

    def test_scrape_date(self):
        entries = work_log2.entry_scrape(
            work_log2.Entry.select().order_by(
                work_log2.Entry.timestamp.desc()
            ),
            search_query='date',
            search_item=datetime.datetime.today().date()
        )
        self.assertIn(self.stubby, entries)

    def test_scrape_dates(self):
        entries = work_log2.entry_scrape(
            work_log2.Entry.select().order_by(
                work_log2.Entry.timestamp.desc()
            ),
            search_query='date_range',
            fdate=datetime.datetime.today().date()-datetime.timedelta(days=1),
            ldate=datetime.datetime.today().date()+datetime.timedelta(days=1)
        )
        self.assertIn(self.stubby, entries)

    def test_scrape_minutes(self):
        entries = work_log2.entry_scrape(
            work_log2.Entry.select().order_by(
                work_log2.Entry.timestamp.desc()
            ),
            search_query='task_minutes',
            search_item=43200
        )
        self.assertIn(self.stubby, entries)

    def test_scrape_unknown(self):
        entries = work_log2.entry_scrape(
            work_log2.Entry.select().order_by(
                work_log2.Entry.timestamp.desc()
            ),
            search_query='bad_query'
        )
        self.assertFalse(entries)

    # test_scrape_keyexcept
    # @patch('work_log2.add_entry')
    # @patch('builtins.input', MagicMock())
    # def test_main_menu_add(self, mock_func):
    #    MagicMock().return_value = 'a'
    #    work_log2.main_menu()
    #    mock_func.assert_called()

    def tearDown(self):
        self.stubby.delete_instance()


if __name__ == '__main__':
    unittest.main()
