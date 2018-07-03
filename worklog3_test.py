import datetime
import os
import re
import sys
import unittest
from unittest.mock import patch, MagicMock

from peewee import *
from models import Entry
import wlux
from worklog3 import CardCatalog

class FunctionTests(unittest.TestCase):
    def setUp(self):
        Entry.create(timestamp=datetime.datetime(2018, 7, 2, 8),
                     user_name='White Diamond',
                     task_name='Unknown',
                     task_minutes=1200,
                     task_notes="mystery")

    def tearDown(self):
        egg = CardCatalog().delete_entry({'user_name': 'White Diamond',
                            'task_name': 'Unknown',
                            'task_minutes': 1200,
                            'task_notes': "mystery",
                            'timestamp': datetime.datetime(2018, 7, 2, 8)})

    def test_save_new_good(self):
        sav = CardCatalog().save_new(
                 'Steven Universe',
                 'Containing the Cluster',
                 11,
                 "I got you. You got this. We've all got eachother.")
        self.assertTrue(sav)

    def test_save_new_bad(self):
        sav = CardCatalog().save_new(
                 43,
                 22,
                 'seventy-eight',
                 False)
        self.assertFalse(sav)

    def test_save_edit_good(self):
        e_dict = {'timestamp': datetime.datetime(2018, 7, 2, 8),
                  'user_name': 'White Diamond',
                  'task_name': 'Unknown',
                  'task_minutes': 1200,
                  'task_notes': "mystery"}
        updater = CardCatalog().acquire_target(e_dict)
        updater.task_name = 'Reknowned'
        updater.task_minutes = 21
        updater.task_notes = 'solved'
        updater.timestamp = datetime.datetime(2015, 6, 2, 8)
        saver = CardCatalog().save_edits(updater)
        self.assertTrue(saver)

    @unittest.expectedFailure
    def test_save_edit_error(self):
        saver = CardCatalog().save_edits('Not an entry')
        assertFalse(saver)

    def test_name_check_good(self):
        self.assertTrue(CardCatalog().name_check('Steven Universe'))

    def test_name_check_bad(self):
        self.assertFalse(CardCatalog().name_check('Beyonce'))

    def test_minute_check_good(self):
        self.assertTrue(CardCatalog().minute_check('10'))
        
    def test_minute_check_bad(self):
        self.assertFalse(CardCatalog().minute_check('ten'))

    def test_notes_out_else(self):
        self.assertEqual(CardCatalog().notes_out('notes'), 'Notes: notes')

    def test_notes_out_empty(self):
        self.assertIsNone(CardCatalog().notes_out(''))

    def test_notes_out_elif(self):
        stone = '-' * 50
        self.assertEqual(CardCatalog().notes_out(stone),
                         'Notes: ' + stone + '. . . ')
        
    def test_load_entries(self):
        self.assertTrue(CardCatalog().load_entries())

    def test_load_entries_bymin(self):
        self.assertTrue(CardCatalog().load_entries(
                bycat='minutes', target=1200))

    def test_delete_entry(self):
        tde = CardCatalog().delete_entry({'user_name': 'White Diamond',
                            'task_name': 'Unknown',
                            'task_minutes': 1200,
                            'task_notes': "mystery",
                            'timestamp': datetime.datetime(2018, 7, 2, 8)})
        self.assertTrue(tde)

    def test_delete_entry_dne(self):
        tde = CardCatalog().delete_entry({'user_name': 'Rose-Quartz',
                            'task_name': 'Defying Pink Diamond',
                            'task_minutes': 9999999,
                            'timestamp': datetime.datetime(2017, 5, 5, 5)})
        self.assertFalse(tde)

    def test_acquire_target(self):
        entry_dict = {'timestamp': datetime.datetime(2018, 7, 2, 8),
                      'user_name': 'White Diamond',
                      'task_name': 'Unknown',
                      'task_minutes': 1200,
                      'task_notes': "mystery"}
        self.assertEqual(CardCatalog().acquire_target(entry_dict), Entry.get(
                Entry.user_name=='White Diamond',
                Entry.task_name=='Unknown',
                Entry.task_minutes==1200,
                Entry.timestamp==datetime.datetime(2018, 7, 2, 8)))

    @unittest.expectedFailure
    def test_acquire_target_dne(self):
        entry_dict = {'timestamp': datetime.datetime(2000, 1, 1, 1),
                      'user_name': 'Black Gold',
                      'task_name': 'Nameless',
                      'task_minutes': 999999,
                      'task_notes': "idk"}
        self.assertFalse(CardCatalog().acquire_target(entry_dict), Entry.get(
                Entry.user_name=='Black Gold',
                Entry.task_name=='Nameless',
                Entry.task_minutes==999999,
                Entry.timestamp==datetime.datetime(2000, 1, 1, 1)))


if __name__ == '__main__':
    unittest.main()
