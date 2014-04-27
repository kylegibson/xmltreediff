from __future__ import (
    absolute_import,
    unicode_literals,
)

from xml.etree import cElementTree


def default_element_factory(**kwargs):
    pass


def flatten_xml_from_string(xml_data):
    if not xml_data:
        return ''
    tree = cElementTree.fromstring(xml_data)
    return flatten_xml_tree([tree])


def flatten_xml_tree(xml_tree_iterable, element_factory=None):
    if element_factory is None:
        element_factory = default_element_factory

    # Preserve the parent iter, parent item and the parent's child stack
    stack = []

    paths = []

    current_path = []

    current_iter = iter(xml_tree_iterable)
    while True:
        next_item = None
        try:
            next_item = next(current_iter)
        except StopIteration:
            # There are no more children to process in this loop
            pass

        if next_item is None:
            # We've run out of children to process at this level, so jump back
            # to the parent item
            if stack:
                parent_iter, parent_item = stack.pop()
                current_iter = parent_iter
                current_path.pop()
                if parent_item.tail:
                    new_path_level = list(current_path)
                    new_path_level.append('!%s' % parent_item.tail)
                    paths.append(new_path_level)
            else:
                # There are no more parent nodes, we're done
                break
        else:
            current_path.append(next_item.tag)
            paths.append(list(current_path))

            if next_item.text:
                text = '!%s' % next_item.text
                paths.append(list(current_path) + [text])

            # Push the current state onto the stack
            stack.append((current_iter, next_item))

            current_iter = iter(next_item)
    return paths


def diff(a, b):
    a_flatten = flatten_xml_from_string(a)
    b_flatten = flatten_xml_from_string(b)
    print a_flatten
    print b_flatten
    return b
