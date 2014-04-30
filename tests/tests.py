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


class AutoTestCase(TestCase):
    @classmethod
    def create(cls, spec):
        def check_assert_equal(self):
            input, expected = spec
            result = self.function_under_test(input)
            if result != expected:
                raise AssertionError('''
Result: %s
Expected: %s
Input: %s
                ''' % (
                    result,
                    expected,
                    input,
                ))
        return check_assert_equal

    @classmethod
    def generate(cls):
        for i, spec in enumerate(cls.cases):
            test_method = cls.create(spec)
            name = str('test_expected_%d' % i)
            test_method.__name__ = name
            setattr(cls, name, test_method)


class UnflattenTestCase(AutoTestCase):
    function_under_test = lambda s, *args, **kwargs: unflatten(*args, **kwargs)

    cases = (
        ('', ''),
        (
            [
                ['a'],
            ],
            '<a />',
        ),
        (
            [
                ['a'],
                ['a', '!foo'],
            ],
            '<a>foo</a>'
        ),
        (
            [
                ['a'],
                ['a', '!foo'],
                ['a', 'b'],
            ],
            '<a>foo<b /></a>'
        ),
        (
            [
                ['a'],
                ['a', '!foo'],
                ['a', 'b'],
                ['a', 'b', '!bar'],
            ],
            '<a>foo<b>bar</b></a>'
        ),
        (
            [
                ['a'],
                ['a', 'b'],
                ['a', 'b', '!foo'],
            ],
            '<a><b>foo</b></a>'
        ),
        (
            [
                ['a'],
                ['a', 'b'],
                ['a', 'b'],
            ],
            '<a><b /><b /></a>',
        ),
        (
            [
                ['a'],
                ['a', 'b'],
                ['a', 'b', 'c'],
                ['a', 'b'],
            ],
            '<a><b><c /></b><b /></a>',
        ),
        (
            [
                ['a'],
                ['a', 'b'],
                ['a', 'b', 'c'],
                ['a', 'c'],
            ],
            '<a><b><c /></b><c /></a>',
        ),
        (
            [
                ['a'],
                ['a', 'b'],
                ['a', 'b', 'c'],
                ['a', 'b', 'c', 'd'],
                ['a', '!foo'],
            ],
            '<a><b><c><d /></c></b>foo</a>',
        ),
        (
            [
                ['a'],
                ['a', 'b'],
                ['a', '!foo'],
            ],
            '<a><b />foo</a>',
        ),
    )

UnflattenTestCase.generate()


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
