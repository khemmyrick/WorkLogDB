from collections import OrderedDict
import datetime
import unittest
import unittest.mock

# from peewee import *
import wlui
from models import Entry
from worklog3 import CardCatalog


class UserInterfaceTests(unittest.TestCase):
    @unittest.mock.patch('wlui.add_entry', return_value='True')
    def test_main_menu_add(self, mock_ae):
        with unittest.mock.patch('builtins.input', side_effect=['a', 'q']):
            wlui.main_menu()
            mock_ae.assert_called()
            # self.assertRaises('StopIterationError', wlui.main_menu)

    @unittest.mock.patch('wlui.view_entries', return_value='True')
    def test_main_menu_view(self, mock_v_ent):
        with unittest.mock.patch('builtins.input', side_effect=['v', 'q']):
            wlui.main_menu()
            mock_v_ent.assert_called()
            # self.assertRaises('StopIterationError', wlui.main_menu)

    @unittest.mock.patch('wlui.search_entries', return_value='True')
    def test_main_menu_search(self, mock_s_ent):
        with unittest.mock.patch('builtins.input', side_effect=['s', 'q']):
            wlui.main_menu()
            mock_s_ent.assert_called()
            # self.assertRaises('StopIterationError', wlui.main_menu)

if __name__ == '__main__':
    unittest.main()
