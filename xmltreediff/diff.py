from __future__ import (
    absolute_import,
    print_function,
    unicode_literals,
)

from xml.etree import cElementTree


def flatten_xml_from_string(xml_data):
    if not xml_data:
        return ''
    tree = cElementTree.fromstring(xml_data)
    return flatten_xml_tree([tree])


def unflatten(tree):
    builder = cElementTree.TreeBuilder()

    if not tree:
        return ''

    tag = None
    root_element = None
    paths = []
    for row in tree:
        current_path = []
        data = ''
        create_new_element = True
        for column in row:
            if column[0] == '!':
                create_new_element = False
                data = column[1:]
            else:
                current_path.append(column)

        tags_to_end = []

        last_path = paths[-1] if paths else []

        if not data and current_path == last_path:
            tags_to_end.append(tag)

        for i, a in enumerate(last_path):
            tag_to_end = None
            if i >= len(current_path):
                tag_to_end = a
            else:
                b = current_path[i]
                if a != b:
                    tag_to_end = a
            if tag_to_end:
                tags_to_end.append(tag_to_end)

        for tag_to_end in tags_to_end[::-1]:
            builder.end(tag_to_end)
            paths.pop()

        last_path = paths[-1] if paths else []
        if not data and current_path == last_path:
            builder.end(tag_to_end)
            paths.pop()

        tag = current_path[-1]
        if create_new_element:
            builder.start(tag)

        if data:
            builder.data(data)

        paths.append(current_path)

    builder.end(tag)

    root_element = builder.close()
    if root_element is None:
        return ''
    return cElementTree.tostring(root_element)


def flatten_xml_tree(xml_tree_iterable):
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
