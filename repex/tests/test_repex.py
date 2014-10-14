########
# Copyright (c) 2014 GigaSpaces Technologies Ltd. All rights reserved
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#        http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
#    * WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#    * See the License for the specific language governing permissions and
#    * limitations under the License.

__author__ = 'nir0s'

import repex.repex as rpx
import repex.logger as logger

import testtools
import os
from testfixtures import log_capture
import logging


TEST_DIR = '{0}/test_dir'.format(os.path.expanduser("~"))
TEST_FILE_NAME = 'test_file'
TEST_FILE = TEST_DIR + '/' + TEST_FILE_NAME
TEST_RESOURCES_DIR = 'repex/tests/resources/'
TEST_RESOURCES_DIR_PATTERN = 'repex/tests/resource.*'
MOCK_CONFIG_FILE = os.path.join(TEST_RESOURCES_DIR, 'mock_files.yaml')
MOCK_CONFIG_MULTIPLE_FILES = os.path.join(TEST_RESOURCES_DIR,
                                          'mock_multiple_files.yaml')
MOCK_TEST_FILE = os.path.join(TEST_RESOURCES_DIR, 'mock_VERSION')
BAD_CONFIG_FILE = os.path.join(TEST_RESOURCES_DIR, 'bad_mock_files.yaml')
EMPTY_CONFIG_FILE = os.path.join(TEST_RESOURCES_DIR, 'empty_mock_files.yaml')

# list of files to include in replacement relative to TEST_RESOURCES_DIR
FILES = [
    'multiple/folders/mock_VERSION',
    'multiple/mock_VERSION'
]
# list of files to exclude in replacement relative to TEST_RESOURCES_DIR
EXCLUDED_FILES = [
    'multiple/excluded/mock_VERSION'
]
EXCLUDED_DIRS = [
    'multiple/excluded'
]


class TestBase(testtools.TestCase):

    @log_capture()
    def test_set_global_verbosity_level(self, capture):
        lgr = logger.init(base_level=logging.INFO)

        rpx._set_global_verbosity_level(is_verbose_output=False)
        lgr.debug('TEST_LOGGER_OUTPUT')
        capture.check()
        lgr.info('TEST_LOGGER_OUTPUT')
        capture.check(('user', 'INFO', 'TEST_LOGGER_OUTPUT'))

        rpx._set_global_verbosity_level(is_verbose_output=True)
        lgr.debug('TEST_LOGGER_OUTPUT')
        capture.check(
            ('user', 'INFO', 'TEST_LOGGER_OUTPUT'),
            ('user', 'DEBUG', 'TEST_LOGGER_OUTPUT'))

    def test_import_config_file(self):
        outcome = rpx.import_config(MOCK_CONFIG_FILE)
        self.assertEquals(type(outcome), dict)
        self.assertIn('paths', outcome.keys())

    def test_fail_import_config_file(self):
        ex = self.assertRaises(RuntimeError, rpx.import_config, '')
        self.assertEquals(str(ex), 'cannot access config file')

    def test_import_bad_config_file_mapping(self):
        ex = self.assertRaises(Exception, rpx.import_config, BAD_CONFIG_FILE)
        self.assertIn('mapping values are not allowed here', str(ex))

    def test_iterate_no_config_supplied(self):
        ex = self.assertRaises(TypeError, rpx.iterate)
        self.assertIn('takes at least 1 argument', str(ex))

    def test_iterate_no_files(self):
        ex = self.assertRaises(
            rpx.RepexError, rpx.iterate, EMPTY_CONFIG_FILE)
        self.assertEqual(str(ex), 'no paths configured')

    def test_iterate(self):
        output_file = MOCK_TEST_FILE + '.test'
        v = {'version': '3.1.0-m3'}
        rpx.iterate(MOCK_CONFIG_FILE, v)
        with open(output_file) as f:
            self.assertIn('3.1.0-m3', f.read())
        os.remove(output_file)

    def test_iterate_with_vars(self):
        output_file = MOCK_TEST_FILE + '.test'
        v = {'version': '3.1.0-m3'}
        rpx.iterate(MOCK_CONFIG_FILE, v)
        with open(output_file) as f:
            self.assertIn('3.1.0-m3', f.read())
        os.remove(output_file)

    def test_iterate_variables_not_dict(self):
        ex = self.assertRaises(
            RuntimeError, rpx.iterate, MOCK_CONFIG_FILE, variables='x')
        self.assertEqual(str(ex), 'variables must be of type dict')

    def test_match_not_found_in_file_force_match_and_pattern(self):
        p = rpx.Repex(MOCK_TEST_FILE, 'NONEXISTING STRING', 'X', '')
        self.assertFalse(p.validate_before(True, True, must_include=[]))

    def test_match_not_found_in_file_no_force(self):
        p = rpx.Repex(MOCK_TEST_FILE, 'NONEXISTING STRING', 'X', '')
        self.assertTrue(p.validate_before(False, False, must_include=[]))

    def test_match_not_found_in_file_force_match(self):
        p = rpx.Repex(MOCK_TEST_FILE, 'NONEXISTING STRING', 'X', '')
        self.assertFalse(p.validate_before(True, False, must_include=[]))

    def test_match_not_found_in_file_force_pattern(self):
        p = rpx.Repex(MOCK_TEST_FILE, 'NONEXISTING STRING', 'X', '')
        self.assertTrue(p.validate_before(False, True, must_include=[]))

    def test_pattern_found_in_match_force_pattern(self):
        p = rpx.Repex(MOCK_TEST_FILE, 'version', 'ver', '')
        self.assertTrue(p.validate_before(False, True, must_include=[]))

    def test_pattern_not_found_in_match_force_pattern(self):
        p = rpx.Repex(MOCK_TEST_FILE, 'version', 'X', '')
        self.assertFalse(p.validate_before(False, True, must_include=[]))

    def test_pattern_not_found_in_match_force_match(self):
        p = rpx.Repex(MOCK_TEST_FILE, 'version', 'X', '')
        self.assertTrue(p.validate_before(True, False, must_include=[]))

    def test_pattern_not_found_in_match_no_force(self):
        p = rpx.Repex(MOCK_TEST_FILE, 'version', 'X', '')
        self.assertTrue(p.validate_before(False, False, must_include=[]))

    def test_file_validation_failed(self):
        file = {
            'path': MOCK_TEST_FILE,
            'match': 'MISSING_MATCH',
            'replace': 'MISSING_PATTERN',
            'with': '',
            'to_file': MOCK_TEST_FILE + '.test',
            'validate_before': True
        }
        try:
            rpx.handle_file(file, verbose=True)
        except rpx.RepexError as ex:
            self.assertEqual(str(ex), 'prevalidation failed')

    def test_file_no_permissions_to_write_to_file(self):
        file = {
            'path': MOCK_TEST_FILE,
            'match': '3.1.0-m2',
            'replace': '3.1.0-m2',
            'with': '3.1.0-m3',
            'to_file': '/mock.test'
        }
        try:
            rpx.handle_file(file, verbose=True)
        except IOError as ex:
            self.assertIn('Permission denied', str(ex))

    def test_file_must_include_missing(self):
        file = {
            'path': MOCK_TEST_FILE,
            'match': '3.1.0-m2',
            'replace': '3.1.0',
            'with': '',
            'to_file': MOCK_TEST_FILE + '.test',
            'validate_before': True,
            'must_include': [
                'MISSING_INCLUSION'
            ]
        }
        try:
            rpx.handle_file(file, verbose=True)
        except rpx.RepexError as ex:
            self.assertEqual(str(ex), 'prevalidation failed')

    def test_iterate_multiple_files(self):
        v = {
            'preversion': '3.1.0-m2',
            'version': '3.1.0-m3'
        }
        # iterate once
        rpx.iterate(MOCK_CONFIG_MULTIPLE_FILES, v, True)
        # verify that all files were modified
        for fl in FILES:
            with open(os.path.join(TEST_RESOURCES_DIR, fl)) as f:
                self.assertIn('3.1.0-m3', f.read())
        # all other than the excluded ones
        for fl in EXCLUDED_FILES:
            with open(os.path.join(TEST_RESOURCES_DIR, fl)) as f:
                self.assertIn('3.1.0-m2', f.read())
        v['preversion'] = '3.1.0-m3'
        v['version'] = '3.1.0-m2'
        rpx.iterate(MOCK_CONFIG_MULTIPLE_FILES, v)
        for fl in FILES:
            with open(os.path.join(TEST_RESOURCES_DIR, fl)) as f:
                self.assertIn('3.1.0-m2', f.read())
        for fl in EXCLUDED_FILES:
            with open(os.path.join(TEST_RESOURCES_DIR, fl)) as f:
                self.assertIn('3.1.0-m2', f.read())

    def test_get_all_files_no_exclusion(self):
        files = rpx.get_all_files(
            'mock_VERSION', TEST_RESOURCES_DIR_PATTERN, TEST_RESOURCES_DIR)
        for f in FILES + EXCLUDED_FILES:
            self.assertIn(os.path.join(TEST_RESOURCES_DIR, f), files)

    def test_get_all_files_with_file_exclusion(self):
        files = rpx.get_all_files(
            'mock_VERSION', TEST_RESOURCES_DIR_PATTERN, TEST_RESOURCES_DIR,
            EXCLUDED_FILES)
        for f in EXCLUDED_FILES:
            self.assertIn(
                'repex/tests/resources/multiple/folders/mock_VERSION', files)
            self.assertIn(
                'repex/tests/resources/multiple/mock_VERSION', files)
        for f in EXCLUDED_FILES:
            self.assertNotIn(
                'repex/tests/resources/multiple/excluded/mock_VERSION', files)

    def test_get_all_files_with_dir_exclusion(self):
        files = rpx.get_all_files(
            'mock_VERSION', TEST_RESOURCES_DIR_PATTERN, TEST_RESOURCES_DIR,
            EXCLUDED_DIRS)
        for f in EXCLUDED_FILES:
            self.assertIn(
                'repex/tests/resources/multiple/folders/mock_VERSION', files)
            self.assertIn(
                'repex/tests/resources/multiple/mock_VERSION', files)
        for f in EXCLUDED_FILES:
            self.assertNotIn(
                'repex/tests/resources/multiple/excluded/mock_VERSION', files)

    def test_get_all_files_excluded_list_is_str(self):
        ex = self.assertRaises(
            rpx.RepexError, rpx.get_all_files,
            'mock_VERSION', TEST_RESOURCES_DIR_PATTERN,
            TEST_RESOURCES_DIR, 'INVALID_EXCLUDED_LIST')
        self.assertIn('excluded_paths must be of type list', str(ex))
