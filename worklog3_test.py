import datetime
import unittest
import unittest.mock

import wlui
import models
from models import Entry
from worklog3 import CardCatalog


class FunctionTests(unittest.TestCase):
    def setUp(self):
        models.initialize()
        Entry.create(timestamp=datetime.datetime(2018, 7, 2, 8),
                     user_name='White Diamond',
                     task_name='Unknown',
                     task_minutes=1200,
                     task_notes="mystery")

    def tearDown(self):
        CardCatalog().delete_entry(
            {'user_name': 'White Diamond',
             'task_name': 'Unknown',
             'task_minutes': 1200,
             'task_notes': "mystery",
             'timestamp': datetime.datetime(2018, 7, 2, 8)}
        )

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

    def test_save_edit_error(self):
        saver = CardCatalog().save_edits('Not an entry')
        self.assertFalse(saver)

    def test_name_check_good(self):
        self.assertTrue(CardCatalog().name_check('Steven Universe'))

    def test_name_check_bad(self):
        self.assertFalse(CardCatalog().name_check('Beyonce'))

    def test_date_check(self):
        feebird = CardCatalog().date_check('01/01/2018')
        self.assertIsInstance(feebird, datetime.datetime)

    def test_date_check_bad(self):
        feebird = CardCatalog().date_check('15/35/99999')
        self.assertFalse(feebird)

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

    def test_generate_roster(self):
        stafflist = CardCatalog().generate_roster()
        self.assertIsInstance(stafflist, list)

    def test_generate_datelog(self):
        cale = CardCatalog().generate_roster()
        self.assertIsInstance(cale, list)

    def test_load_entries(self):
        loaded = CardCatalog().load_entries()
        self.assertIsInstance(loaded, list)

    def test_load_entries_bymin(self):
        loaded = CardCatalog().load_entries(
                bycat='minutes', target=1200)
        self.assertIsInstance(loaded, list)

    def test_load_entries_byterm(self):
        loaded = CardCatalog().load_entries(
                bycat='term', target='mystery')
        self.assertIsInstance(loaded, list)

    def test_load_entries_byname(self):
        loaded = CardCatalog().load_entries(
                bycat='name', target='White Diamond')
        self.assertIsInstance(loaded, list)

    def test_delete_entry(self):
        tde = CardCatalog().delete_entry(
            {'user_name': 'White Diamond',
             'task_name': 'Unknown',
             'task_minutes': 1200,
             'task_notes': "mystery",
             'timestamp': datetime.datetime(2018, 7, 2, 8)})
        self.assertTrue(tde)

    def test_delete_entry_dne(self):
        tde = CardCatalog().delete_entry(
            {'user_name': 'Rose-Quartz',
             'task_name': 'Defying Pink Diamond',
             'task_minutes': 9999999,
             'timestamp': datetime.datetime(2017, 5, 5, 5)}
        )
        self.assertFalse(tde)

    def test_acquire_target(self):
        entry_dict = {'timestamp': datetime.datetime(2018, 7, 2, 8),
                      'user_name': 'White Diamond',
                      'task_name': 'Unknown',
                      'task_minutes': 1200,
                      'task_notes': "mystery"}
        spam = CardCatalog().acquire_target(entry_dict)
        egg = Entry.get(
                Entry.user_name == 'White Diamond',
                Entry.task_name == 'Unknown',
                Entry.task_minutes == 1200,
                Entry.timestamp == datetime.datetime(2018, 7, 2, 8),
                Entry.task_notes == "mystery"
        )
        self.assertEqual(spam, egg)

    def test_acquire_target_dne(self):
        entry_dict = {'timestamp': datetime.datetime(2000, 1, 1, 1),
                      'user_name': 'Black Gold',
                      'task_name': 'Nameless',
                      'task_minutes': 999999,
                      'task_notes': "idk"}
        self.assertFalse(CardCatalog().acquire_target(entry_dict))


class UserInterfaceTests(unittest.TestCase):
    def setUp(self):
        models.initialize()

    def test_invalid_input(self):
        with unittest.mock.patch('builtins.input', return_value=''):
            self.assertIsNone(wlui.invalid_input('wanted'))

    def test_press_enter(self):
        with unittest.mock.patch('builtins.input', return_value=''):
            self.assertIsNone(wlui.press_enter())

    @unittest.mock.patch('wlui.view_entries', return_value='True')
    def test_by_term(self, mock_ve):
        """Test search task names/notes."""
        with unittest.mock.patch('builtins.input', return_value='Y'):
            wlui.by_term()
            mock_ve.assert_called_with(bycat='term', target='Y')

    @unittest.mock.patch('wlui.view_entries', return_value='True')
    def test_by_minutes_good(self, mock_ve):
        """Test search by minutes with a valid integer."""
        with unittest.mock.patch('builtins.input', return_value='3'):
            wlui.by_minutes()
            mock_ve.assert_called_with(bycat='minutes', target='3')

    @unittest.mock.patch('wlui.invalid_input', return_value='True')
    @unittest.mock.patch('wlui.view_entries', return_value='True')
    def test_by_minutes_bad_then_good(self, mock_ve, mock_ii):
        """Test search by minutes with a valid integer."""
        with unittest.mock.patch('builtins.input', side_effect=['two', '2']):
            wlui.by_minutes()
            mock_ii.assert_called_with('integer')
            # Bad arg calls invalid_input function, then loops.
            # Good arg is passed through to view_entries function.
            mock_ve.assert_called_with(bycat='minutes', target='2')

    @unittest.mock.patch('wlui.view_entries', return_value='True')
    def test_by_staff_list_good(self, mock_ve):
        with unittest.mock.patch('builtins.input', side_effect=['l', '0']):
            wlui.by_staff()
            mock_ve.assert_called()

    @unittest.mock.patch('wlui.invalid_input', return_value='True')
    @unittest.mock.patch('wlui.view_entries', return_value='True')
    def test_by_staff_list_bad_then_good(self, mock_ve, mock_ii):
        with unittest.mock.patch('builtins.input',
                                 side_effect=['l', 'five', '0']):
            wlui.by_staff()
            mock_ii.assert_called_with('integer')
            mock_ve.assert_called()

    @unittest.mock.patch('wlui.view_entries', return_value='True')
    def test_by_staff_input(self, mock_ve):
        with unittest.mock.patch('builtins.input',
                                 side_effect=['p', 'John']):
            wlui.by_staff()
            mock_ve.assert_called_with(bycat='name', target='John')

    @unittest.mock.patch('wlui.view_entries', return_value='True')
    def test_by_staff_fol(self, mock_ve):
        with unittest.mock.patch('builtins.input',
                                 side_effect=['n',
                                              'Yellow',
                                              0]):
            Entry.create(
                timestamp=datetime.datetime(2018, 1, 1, 1),
                user_name='Yellow Diamond',
                task_name='Stomp RQ',
                task_minutes=1,
                task_notes="mystery"
            )
            wlui.by_staff()
            mock_ve.assert_called_with(bycat='name', target='Yellow Diamond')
            CardCatalog().delete_entry(
                {'user_name': 'Yellow Diamond',
                 'task_name': 'Stomp RQ',
                 'task_minutes': 1,
                 'task_notes': "mystery",
                 'timestamp': datetime.datetime(2018, 1, 1, 1)}
            )

    @unittest.mock.patch('wlui.view_entries', return_value='True')
    def test_by_date_list_good(self, mock_ve):
        with unittest.mock.patch('builtins.input',
                                 side_effect=['l', '0']):
            wlui.by_date()
            mock_ve.assert_called()

    @unittest.mock.patch('wlui.invalid_input', return_value='True')
    @unittest.mock.patch('wlui.view_entries', return_value='True')
    def test_by_date_list_bad_then_good(self, mock_ve, mock_ii):
        with unittest.mock.patch('builtins.input',
                                 side_effect=['l', 'zero', '0']):
            wlui.by_date()
            mock_ii.assert_called_with('date selection')
            mock_ve.assert_called()

    @unittest.mock.patch('wlui.view_entries', return_value='True')
    def test_by_date_input_good(self, mock_ve):
        with unittest.mock.patch('builtins.input',
                                 side_effect=['r',
                                              '03/03/3333-05/05/5555']):
            wlui.by_date()
            mock_ve.assert_called()

    @unittest.mock.patch('wlui.invalid_input', return_value='True')
    @unittest.mock.patch('wlui.view_entries', return_value='True')
    def test_by_date_input_bad_then_good(self, mock_ve, mock_ii):
        with unittest.mock.patch('builtins.input',
                                 side_effect=['r',
                                              'fourth of july',
                                              '03/03/3333-05/05/5555']):
            wlui.by_date()
            mock_ii.assert_called_with('date range string')
            mock_ve.assert_called()

    @unittest.mock.patch('wlui.by_staff', return_value='True')
    def test_search_entries_staff(self, mock_staff):
        with unittest.mock.patch('builtins.input', return_value='n'):
            wlui.search_entries()
            mock_staff.assert_called()

    @unittest.mock.patch('wlui.by_date', return_value='True')
    def test_search_entries_date(self, mock_date):
        with unittest.mock.patch('builtins.input', return_value='d'):
            wlui.search_entries()
            mock_date.assert_called()

    @unittest.mock.patch('wlui.by_minutes', return_value='True')
    def test_search_entries_minutes(self, mock_min):
        with unittest.mock.patch('builtins.input', return_value='m'):
            wlui.search_entries()
            mock_min.assert_called()

    @unittest.mock.patch('wlui.by_term', return_value='True')
    def test_search_entries_term(self, mock_term):
        with unittest.mock.patch('builtins.input', return_value='t'):
            wlui.search_entries()
            mock_term.assert_called()

    def test_search_entries_quit(self):
        with unittest.mock.patch('builtins.input', return_value='q'):
            self.assertIsNone(wlui.search_entries())

    @unittest.mock.patch('wlui.add_entry', return_value='True')
    def test_main_menu_add(self, mock_ae):
        with unittest.mock.patch('builtins.input', side_effect=['a', 'q']):
            wlui.main_menu()
            mock_ae.assert_called()

    @unittest.mock.patch('wlui.view_entries', return_value='True')
    def test_main_menu_view(self, mock_v_ent):
        with unittest.mock.patch('builtins.input', side_effect=['v', 'q']):
            wlui.main_menu()
            mock_v_ent.assert_called()

    @unittest.mock.patch('wlui.search_entries', return_value='True')
    def test_main_menu_search(self, mock_s_ent):
        with unittest.mock.patch('builtins.input', side_effect=['s', 'q']):
            wlui.main_menu()
            mock_s_ent.assert_called()

    @unittest.mock.patch('worklog3.CardCatalog.acquire_target',
                         return_value=False)
    def test_edit_entry_no_such_entry(self, mock_at):
        with unittest.mock.patch('builtins.input', return_value=''):
            e_dict = {
                'user_name': 'Greg Universe',
                'task_name': 'Charm Blue Diamond',
                'task_minutes': 1,
                'task_notes': 'plan vetoed by consensus vote',
                'timestamp': datetime.datetime.now()
            }
            self.assertIsNone(wlui.edit_entry(e_dict))

    def test_edit_entry_good(self):
        with unittest.mock.patch('builtins.input',
                                 side_effect=['Spam',
                                              '42',
                                              '11/11/2011',
                                              'n',
                                              'y',
                                              '']):
            Entry.create(
                timestamp=datetime.datetime(2018, 1, 1, 1),
                user_name='Yellow Diamond',
                task_name='Stomp RQ',
                task_minutes=1,
                task_notes="mystery"
            )
            e_dict = {
                'user_name': 'Yellow Diamond',
                'task_name': 'Stomp RQ',
                'task_minutes': 1,
                'task_notes': "mystery",
                'timestamp': datetime.datetime(2018, 1, 1, 1)
            }

            self.assertIsNone(wlui.edit_entry(e_dict))
            CardCatalog().delete_entry(
                {'user_name': 'Yellow Diamond',
                 'task_name': 'Spam',
                 'task_minutes': 42,
                 'task_notes': "mystery",
                 'timestamp': datetime.datetime(2011, 11, 11, 1)}
            )

    def test_edit_entry_bad_then_good(self):
        with unittest.mock.patch('builtins.input',
                                 side_effect=['Spam',
                                              'fourtwo',
                                              '',
                                              '42',
                                              'Bey Day',
                                              '',
                                              '11/11/2011',
                                              'n',
                                              'y',
                                              '']):
            Entry.create(  # i assigned this to yde
                timestamp=datetime.datetime(2018, 1, 1, 1),
                user_name='Yellow Diamond',
                task_name='Stomp RQ',
                task_minutes=1,
                task_notes="mystery"
            )
            e_dict = {
                'user_name': 'Yellow Diamond',
                'task_name': 'Stomp RQ',
                'task_minutes': 1,
                'task_notes': "mystery",
                'timestamp': datetime.datetime(2018, 1, 1, 1)
            }

            self.assertIsNone(wlui.edit_entry(e_dict))
            CardCatalog().delete_entry(
                {'user_name': 'Yellow Diamond',
                 'task_name': 'Spam',
                 'task_minutes': 42,
                 'task_notes': "mystery",
                 'timestamp': datetime.datetime(2011, 11, 11, 1)}
            )

    @unittest.mock.patch('wlui.edit_entry', return_value=True)
    @unittest.mock.patch(
        'worklog3.CardCatalog.load_entries',
        return_value=[{'user_name': 'John Doe',
                       'task_name': 'Work Task',
                       'task_minutes': 60,
                       'task_notes': '',
                       'timestamp': datetime.datetime.now().date()},
                      {'user_name': 'Mayor Nana',
                       'task_name': 'protect Beach City',
                       'task_minutes': 42,
                       'task_notes': 'this is not a drill',
                       'timestamp': datetime.datetime.now().date()},
                      {'user_name': 'Ronaldo Frymann',
                       'task_name': 'defeat the cluster',
                       'task_minutes': 1,
                       'task_notes': 'not really',
                       'timestamp': datetime.datetime.now().date()}]
    )
    def test_view_entries_fwd_back_edit(self, mock_le, mock_ee):
        with unittest.mock.patch('builtins.input',
                                 side_effect=['n',
                                              'n',
                                              'n',
                                              '',
                                              'p',
                                              'p',
                                              'p',
                                              '',
                                              'e']):
            wlui.view_entries()
            mock_le.assert_called()
            mock_ee.assert_called_with(
                {'user_name': 'John Doe',
                 'task_name': 'Work Task',
                 'task_minutes': 60,
                 'task_notes': '',
                 'timestamp': datetime.datetime.now().date()}
            )

    @unittest.mock.patch('worklog3.CardCatalog.delete_entry',
                         return_value=True)
    @unittest.mock.patch(
        'worklog3.CardCatalog.load_entries',
        return_value=[{'user_name': 'John Doe',
                       'task_name': 'Work Task',
                       'task_minutes': 60,
                       'task_notes': '',
                       'timestamp': datetime.datetime.now().date()},
                      {'user_name': 'Mayor Nana',
                       'task_name': 'protect Beach City',
                       'task_minutes': 42,
                       'task_notes': 'this is not a drill',
                       'timestamp': datetime.datetime.now().date()},
                      {'user_name': 'Ronaldo Frymann',
                       'task_name': 'defeat the cluster',
                       'task_minutes': 1,
                       'task_notes': 'not really',
                       'timestamp': datetime.datetime.now().date()}]
    )
    def test_view_entries_fwd_back_delete(self, mock_le, mock_de):
        with unittest.mock.patch('builtins.input',
                                 side_effect=['n',
                                              'n',
                                              'n',
                                              '',
                                              'p',
                                              'p',
                                              'p',
                                              '',
                                              'd',
                                              'y']):
            wlui.view_entries()
            mock_le.assert_called()
            mock_de.assert_called_with(
                {'user_name': 'John Doe',
                 'task_name': 'Work Task',
                 'task_minutes': 60,
                 'task_notes': '',
                 'timestamp': datetime.datetime.now().date()}
            )

    @unittest.mock.patch('worklog3.CardCatalog.save_new',
                         return_value=True)
    def test_add_entry_good(self, mock_sn):
        with unittest.mock.patch('builtins.input',
                                 side_effect=['Sadie Miller',
                                              'Working Dead',
                                              '18',
                                              'n',
                                              'y',
                                              '']):
            wlui.add_entry()
            mock_sn.assert_called_with('Sadie Miller',
                                       'Working Dead',
                                       '18',
                                       '')

    @unittest.mock.patch('worklog3.CardCatalog.save_new',
                         return_value=True)
    def test_add_entry_bad_then_good(self, mock_sn):
        with unittest.mock.patch('builtins.input',
                                 side_effect=['badname',
                                              '',
                                              'Sadie Miller',
                                              3,
                                              '',
                                              'Working Dead',
                                              'ten',
                                              '',
                                              '18',
                                              'n',
                                              'y',
                                              '']):
            wlui.add_entry()
            mock_sn.assert_called_with('Sadie Miller',
                                       'Working Dead',
                                       '18',
                                       '')


if __name__ == '__main__':
    unittest.main()
