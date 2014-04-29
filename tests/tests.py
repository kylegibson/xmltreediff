from __future__ import (
    absolute_import,
    unicode_literals,
)

from unittest import TestCase

from xmltreediff.diff import (
    diff,
    flatten_xml_from_string,
    unflatten,
)


class DiffTestCase(TestCase):
    def test_text_changed(self):
        a = '<p>foo</p>'
        b = '<p>bar</p>'
        result = diff(a, b)
        expected = '<p><del>foo</del><ins>bar</ins></p>'
        self.assertEqual(result, expected)

    def test_new_node(self):
        a = '<a><p>foo</p></a>'
        b = '<a><p>foo</p><p>bar</p></a>'
        result = diff(a, b)
        expected = '<a><p>foo</p><ins><p>bar</p></ins></a>'
        self.assertEqual(result, expected)


class UnflattenTestCase(TestCase):
    def test_empty_string(self):
        result = unflatten('')
        self.assertEqual(result, '')

    def test_single_element(self):
        tree = [
            ['a'],
        ]
        result = unflatten(tree)
        self.assertEqual(result, '<a />')

    def test_single_element_with_text(self):
        tree = [
            ['a'],
            ['a', '!foo'],
        ]
        result = unflatten(tree)
        self.assertEqual(result, '<a>foo</a>')


class FlattenXmlTreeFromStringTestCase(TestCase):
    def test_empty_string(self):
        result = flatten_xml_from_string('')
        self.assertEqual(result, '')

    def test_single_element(self):
        result = flatten_xml_from_string('<p/>')
        expected = [
            ['p'],
        ]
        self.assertEqual(result, expected)

    def test_nested_element(self):
        result = flatten_xml_from_string('<a><b/></a>')
        expected = [
            ['a'],
            ['a', 'b'],
        ]
        self.assertEqual(result, expected)

    def test_triple_nested(self):
        result = flatten_xml_from_string('<a><b><c/><d/></b><e/></a>')
        expected = [
            ['a'],
            ['a', 'b'],
            ['a', 'b', 'c'],
            ['a', 'b', 'd'],
            ['a', 'e'],
        ]
        self.assertEqual(result, expected)

    def test_with_text_and_tail(self):
        result = flatten_xml_from_string(
            '<a>foo<b>bar</b>baz<c>cat</c>dog</a>',
        )
        expected = [
            ['a'],
            ['a', '!foo'],
            ['a', 'b'],
            ['a', 'b', '!bar'],
            ['a', '!baz'],
            ['a', 'c'],
            ['a', 'c', '!cat'],
            ['a', '!dog'],
        ]
        self.assertEqual(result, expected)

    def test_with_text_multiple(self):
        result = flatten_xml_from_string(
            '<a>foo<b>bar</b><b>baz</b></a>',
        )
        expected = [
            ['a'],
            ['a', '!foo'],
            ['a', 'b'],
            ['a', 'b', '!bar'],
            ['a', 'b'],
            ['a', 'b', '!baz'],
        ]
        self.assertEqual(result, expected)

    def test_with_tail_text_multiple(self):
        result = flatten_xml_from_string(
            '<a>foo<b>bar<c>baz</c></b><b>cat</b></a>',
        )
        expected = [
            ['a'],
            ['a', '!foo'],
            ['a', 'b'],
            ['a', 'b', '!bar'],
            ['a', 'b', 'c'],
            ['a', 'b', 'c', '!baz'],
            ['a', 'b'],
            ['a', 'b', '!cat'],
        ]
        self.assertEqual(result, expected)
