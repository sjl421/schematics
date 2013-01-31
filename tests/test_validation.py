#!/usr/bin/env python

import unittest
from schematics.models import Model
from schematics.validation import (validate_instance, ERROR_FIELD_REQUIRED,
    ERROR_FIELD_TYPE_CHECK)
from schematics.types import StringType
from schematics.types.compound import ModelType, ListType


class TestChoices(unittest.TestCase):
    def setUp(self):
        class Other(Model):
            info = ListType(StringType())

        class TestDoc(Model):
            language = StringType(choices=['en', 'de'])
            other = ModelType(Other)

        self.data_simple_valid = {'language': 'de'}
        self.data_simple_invalid = {'language': 'fr'}
        self.data_embeded_valid = {
            'language': 'de',
            'other': {
                'info': ['somevalue', 'other']
            }
        }
        self.data_embeded_invalid = {
            'language': 'fr',
            'other': {
                'info': ['somevalue', 'other']
            }
        }

        self.doc_simple_valid = TestDoc(**self.data_simple_valid)
        self.doc_simple_invalid = TestDoc(**self.data_simple_invalid)
        self.doc_embedded_valid = TestDoc(**self.data_embeded_valid)
        self.doc_embedded_invalid = TestDoc(**self.data_embeded_invalid)

    def test_choices_validates(self):
        result = validate_instance(self.doc_simple_valid)
        self.assertEqual(result.tag, 'OK')

    def test_validation_fails(self):
        result = validate_instance(self.doc_simple_invalid)
        self.assertNotEqual(result.tag, 'OK')

    def test_choices_validates_with_embedded(self):
        result = validate_instance(self.doc_embedded_valid)
        self.assertEqual(result.tag, 'OK')

    def test_validation_failes_with_embedded(self):
        result = validate_instance(self.doc_embedded_invalid)
        self.assertNotEqual(result.tag, 'OK')


class TestRequired(unittest.TestCase):

    def test_validation_fails(self):
        class TestDoc(Model):
            first_name = StringType(required=True)

        t = TestDoc()
        result = validate_instance(t)

        self.assertNotEqual(result.tag, 'OK')
        self.assertEqual(len(result.value), 1)  # Only one failure
        self.assertEqual(result.value[0].tag, ERROR_FIELD_REQUIRED)

    def test_validation_none_fails(self):
        class TestDoc(Model):
            first_name = StringType(required=True)

        t = TestDoc(first_name=None)
        result = validate_instance(t)

        self.assertNotEqual(result.tag, 'OK')
        self.assertEqual(len(result.value), 1)  # Only one failure
        self.assertEqual(result.value[0].tag, ERROR_FIELD_REQUIRED)

    def test_validation_none_dirty_pass(self):
        class TestDoc(Model):
            first_name = StringType(required=True, dirty=True)

        t = TestDoc(first_name=None)
        result = validate_instance(t)

        self.assertEqual(result.tag, 'OK')

    def test_validation_notset_dirty_fails(self):
        class TestDoc(Model):
            first_name = StringType(required=True, dirty=True)

        t = TestDoc()
        result = validate_instance(t)

        self.assertNotEqual(result.tag, 'OK')
        self.assertEqual(len(result.value), 1)  # Only one failure
        self.assertEqual(result.value[0].tag, ERROR_FIELD_REQUIRED)

    def test_validation_empty_string_pass(self):
        class TestDoc(Model):
            first_name = StringType(required=True)

        t = TestDoc(first_name='')
        result = validate_instance(t)

        self.assertEqual(result.tag, 'OK')

    def test_validation_empty_string_length_fail(self):
        class TestDoc(Model):
            first_name = StringType(required=True, min_length=1)

        t = TestDoc(first_name='')
        result = validate_instance(t)

        self.assertNotEqual(result.tag, 'OK')
        self.assertEqual(len(result.value), 1)  # Only one failure
        # Length failure, not *FIELD_REQUIRED*
        self.assertEqual(result.value[0].tag, ERROR_FIELD_TYPE_CHECK)

    def test_validation_none_string_length_pass(self):
        class TestDoc(Model):
            first_name = StringType(min_length=1)

        t = TestDoc()
        result = validate_instance(t)

        self.assertEqual(result.tag, 'OK')


if __name__ == '__main__':
    unittest.main()
