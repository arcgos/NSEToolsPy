"""
    This is a test module for testing abstract base class
"""
import pandas as pd
import unittest
import os
import logging
import json
import re
import six
from nsetools import Nse
from nsetools.utils import js_adaptor, byte_adaptor, save_file
from nsetools.nse import market_status
from tempfile import gettempdir

log = logging.getLogger('nse')
logging.basicConfig(level=logging.DEBUG)

class TestCoreAPIs(unittest.TestCase):
    def setUp(self):
        self.nse = Nse()

    def test_string_representation(self):
        self.assertEqual(str(self.nse) ,
                         "Driver Class for National Stock Exchange (NSE)")

    def test_nse_headers(self):
        ret = self.nse.nse_headers()
        self.assertIsInstance(ret, dict)

    def test_build_url_for_history(self):
        test_code = 'infy'
        url = self.nse.build_url_for_history(test_code, '04-01-2016', '30-10-2016')
        # 'test_code' should be present in the url
        self.assertIsNotNone(re.search(test_code, url))

    def test_negative_build_url_for_history(self):
            negative_codes = [1, None]
            with self.assertRaises(Exception):
                for test_code in negative_codes:
                    url = self.nse.build_url_for_history(test_code, '04-01-2016', '30-10-2016')

    def test_build_url_for_quote(self):
        test_code = 'infy'
        url = self.nse.build_url_for_quote(test_code)
        # 'test_code' should be present in the url
        self.assertIsNotNone(re.search(test_code, url))

    def test_negative_build_url_for_quote(self):
            negative_codes = [1, None]
            with self.assertRaises(Exception):
                for test_code in negative_codes:
                    url = self.nse.build_url_for_quote(test_code)
    def test_get_peer_companies(self):
        code = 'infy'
        response = self.nse.get_peer_companies(code)
        self.assertIsInstance(response, pd.DataFrame)

        # This one was causing a weird error. as the offset was different
        code = '63moons'
        response = self.nse.get_peer_companies(code)
        self.assertIsInstance(response, pd.DataFrame)

    def test_market_status(self):
        result = market_status()
        self.assertIsInstance(result, bool)

    def test_response_cleaner(self):
        test_dict = {
            'a': '10',
            'b': '10.0',
            'c': '-1,000.10',
            'd': 'vsjha18',
            'e': 10,
            'f': 10.0,
            'g': 1000.10,
            'h': True,
            'i': None,
            'j': u'10',
            'k': u'10.0',
            'l': u'1,000.10'
        }

        expected_dict = {
            'a': 10,
            'b': 10.0,
            'c': -1000.10,
            'd': 'vsjha18',
            'e': 10,
            'f': 10.0,
            'g': 1000.10,
            'h': True,
            'i': None,
            'j': 10,
            'k': 10.0,
            'l': 1000.10
        }
        ret_dict = self.nse.clean_server_response(test_dict)
        self.assertDictEqual(ret_dict, expected_dict)

    def test_get_stock_codes(self):
        sc = self.nse.get_stock_codes()
        self.assertIsNotNone(sc)
        self.assertIsInstance(sc, pd.DataFrame)
        if sc.empty:
            self.fail()

# TODO: use mock and create one test where response contains a blank line
# TODO: use mock and create one test where response doesnt contain a csv
# TODO: use mock and create one test where return is null
# TODO: test the cache feature

    def test_negative_get_quote(self):
        wrong_code = 'inf'
        self.assertEqual(self.nse.get_quote(wrong_code), None)

    def test_get_quote(self):
        resp = self.nse.get_quote('infy', '20Microns', 'abb')
        self.assertEqual(len(resp), 3)
        self.assertIsInstance(resp, pd.DataFrame)
        # test json response
        json_resp = self.nse.get_quote('infy', '20Microns', 'abb', as_json=True)
        self.assertEqual(len(json_resp), 3)
        self.assertIsInstance(json_resp[0], str)

    def test_get_history(self):
        resp = self.nse.get_history(('ABB', '04-01-2010', '30-10-2010'), ('infy', '04-01-2010', '30-10-2010'))
        self.assertEqual(len(resp), 2)
        self.assertIsInstance(resp[0], pd.DataFrame)

        resp = self.nse.get_history(('ABB', '04-01-2010', '30-10-2010'), ('infy', '04-01-2010', '30-10-2010'), as_json=True)
        self.assertEqual(len(resp), 2)
        self.assertIsInstance(resp[0], str)

    def test_is_valid_code(self):
        code = 'infy'
        self.assertTrue(self.nse.is_valid_code(code))

    def test_negative_is_valid_code(self):
        wrong_code = 'in'
        self.assertFalse(self.nse.is_valid_code(wrong_code))

    def test_get_top(self):
        # as_json = False
        # This test will remove the need to test the individual parts
        result = self.nse.get_top('gainers', 'losers', 'volume', 'active', 'advances decline', 'index list', 'JUNK')
        # Gainers/Losers/Volume/Advances Decline is supposed to return a list of dictionaries
        # Index list is supposed to return a list of strings
        # JUNK Should not return anything
        temp = []
        for item in result:
            temp.append(item)

        self.assertEqual(6, len(temp))
        gainer, loser, volume, active, adv_decline, index_list = temp[0], temp[1], temp[2], temp[3], temp[4], temp[5]
        
        # Test these individually
        self.assertIsInstance(gainer, pd.DataFrame)

        self.assertIsInstance(loser, pd.DataFrame)

        self.assertIsInstance(volume, pd.DataFrame)

        self.assertIsInstance(adv_decline, pd.DataFrame)

        self.assertIsInstance(index_list, list)

        # Now as_json = True
        result = self.nse.get_top('gainers', 'losers', 'volume', 'active', 'advances decline', 'index list', as_json=True)

        temp = []
        for item in result:
            temp.append(item)

        self.assertEqual(6, len(temp))
        gainer, loser, volume, active, adv_decline_json, index_list_json = temp[0], temp[1], temp[2], temp[3], temp[4], temp[5]

        self.assertIsInstance(gainer, str)
        self.assertIsInstance(loser, str)
        self.assertIsInstance(volume, str)
        self.assertIsInstance(active, str)

        self.assertIsInstance(adv_decline_json, str)
        self.assertEqual(len(adv_decline), len(json.loads(adv_decline_json)))

        self.assertIsInstance(index_list_json, str)
        self.assertListEqual(index_list, json.loads(index_list_json))

    def test_render_response(self):
        d = {'fname':'Arkoprabho', 'lname':'Chakraborti'}
        resp_dict = self.nse.render_response(d)
        resp_json = self.nse.render_response(d, as_json=True)
        # in case of dict, response should be a python dict
        self.assertIsInstance(resp_dict, dict)
        # in case of json, response should be a json string
        self.assertIsInstance(resp_json, str)
        # and on reconstruction it should become same as original dict
        self.assertDictEqual(d, json.loads(resp_json))

    def test_is_valid_index(self):
        code = 'NIFTY BANK'
        self.assertTrue(self.nse.is_valid_index(code))
        # test with invalid string
        code = 'some junk stuff'
        self.assertFalse(self.nse.is_valid_index(code))
        # test with lower case
        code = 'nifty bank'
        self.assertTrue(self.nse.is_valid_index(code))

    def test_get_index_quote(self):
        code = 'NIFTY BANK'
        self.assertIsInstance(self.nse.get_index_quote(code), dict)
        # with json response
        self.assertIsInstance(self.nse.get_index_quote(code, as_json=True),
                              str)
        # with wrong code
        code = 'wrong code'
        self.assertIsNone(self.nse.get_index_quote(code))

        # with lower case code
        code = 'nifty bank'
        self.assertIsInstance(self.nse.get_index_quote(code), dict)

    def test_jsadptor(self):
        buffer = 'abc:true, def:false, ghi:NaN, jkl:none'
        expected_buffer = 'abc:True, def:False, ghi:"NaN", jkl:None'
        ret = js_adaptor(buffer)
        self.assertEqual(ret, expected_buffer)

    def test_byte_adaptor(self):
        from io import BytesIO
        buffer = b'nsetools'
        fbuffer = BytesIO(buffer)
        ret_file_buffer = byte_adaptor(fbuffer)
        self.assertIsInstance(ret_file_buffer, six.StringIO)

    def test_save_file(self):
        # Call the function, check if the file has been saved at the required location
        dataframe = self.nse.get_stock_codes()
        save_file(dataframe, 'csv', path=gettempdir(), name='StockCodes')
        path = os.path.join(gettempdir(), 'StockCodes.csv')
        if not os.path.exists(path):
            self.fail()

        save_file(dataframe, 'html', path=gettempdir(), name='StockCodes')
        path = os.path.join(gettempdir(), 'StockCodes.html')
        if not os.path.exists(path):
            self.fail()

        save_file(dataframe, 'json', path=gettempdir(), name='StockCodes')
        path = os.path.join(gettempdir(), 'StockCodes.json')
        if not os.path.exists(path):
            self.fail()

        save_file(dataframe, 'tex', path=gettempdir(), name='StockCodes')
        path = os.path.join(gettempdir(), 'StockCodes.tex')
        if not os.path.exists(path):
            self.fail()

if __name__ == '__main__':
    unittest.main()
