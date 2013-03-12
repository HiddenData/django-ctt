#!/usr/bin/env python
#-*- coding: utf-8 -*-
#vim: set ts=4 sw=4 et fdm=marker : */

from django.test import TestCase
from testapp.models import Node, NodeOrderable


class CTTDummyTest(TestCase):
    def setUp(self):
        """
            1
           / \
          2   5
         / \
        3   4
        """
        self._create_tree()

    def _create_tree(self):
        self.n1 = Node.objects.create(name='1')
        self.n2 = Node.objects.create(name='2', parent=self.n1)
        self.n3 = Node.objects.create(name='3', parent=self.n2)
        self.n4 = Node.objects.create(name='4', parent=self.n2)
        self.n5 = Node.objects.create(name='5', parent=self.n1)
        self.n6 = Node.objects.create(name='6')
        self.root = self.n1

    def tearDown(self):
        Node.objects.all().delete()

    def test_get_descendants(self):
        """

        """
        descendants = self.root.get_descendants()
        self.assertTrue(self.n2 in descendants)
        self.assertTrue(self.n3 in descendants)
        self.assertTrue(self.n4 in descendants)
        self.assertTrue(self.n5 in descendants)
        self.assertFalse(self.n1 in descendants)

    def test_get_descendants_inc_self(self):
        descendants = self.root.get_descendants(include_self=True)
        self.assertTrue(self.n2 in descendants)
        self.assertTrue(self.n3 in descendants)
        self.assertTrue(self.n4 in descendants)
        self.assertTrue(self.n5 in descendants)
        self.assertTrue(self.n1 in descendants)

    def test_get_children(self):
        children = self.root.get_children()
        self.assertTrue(self.n2 in children)
        self.assertTrue(self.n5 in children)
        self.assertFalse(self.n3 in children)
        self.assertFalse(self.n4 in children)
        self.assertFalse(self.n1 in children)

    def test_ancestors(self):
        ancestors = self.n3.get_ancestors()
        self.assertTrue(self.n2 in ancestors)
        self.assertTrue(self.n1 in ancestors)
        self.assertFalse(self.n3 in ancestors)
        self.assertFalse(self.n4 in ancestors)
        self.assertFalse(self.n5 in ancestors)

    def test_ancestors_inc_self(self):
        ancestors = self.n3.get_ancestors(include_self=True)
        self.assertTrue(self.n2 in ancestors)
        self.assertTrue(self.n1 in ancestors)
        self.assertTrue(self.n3 in ancestors)
        self.assertFalse(self.n4 in ancestors)
        self.assertFalse(self.n5 in ancestors)

    def test_ancestors_order_asc(self):
        ancestors = self.n3.get_ancestors(ascending=True, include_self=True)
        self.assertEqual(self.n3, ancestors[0])
        self.assertEqual(self.n2, ancestors[1])
        self.assertEqual(self.n1, ancestors[2])

    def test_ancestors_order_desc(self):
        ancestors = self.n3.get_ancestors(ascending=False, include_self=True)
        self.assertEqual(self.n3, ancestors[2])
        self.assertEqual(self.n2, ancestors[1])
        self.assertEqual(self.n1, ancestors[0])

    def test_get_level(self):
        self.assertEqual(self.n1.get_level(), 0)
        self.assertEqual(self.n2.get_level(), 1)
        self.assertEqual(self.n3.get_level(), 2)
        self.assertEqual(self.n4.get_level(), 2)
        self.assertEqual(self.n5.get_level(), 1)

    def test_get_root(self):
        self.assertEqual(self.n1.get_root(), self.n1)
        self.assertEqual(self.n2.get_root(), self.n1)
        self.assertEqual(self.n3.get_root(), self.n1)
        self.assertEqual(self.n4.get_root(), self.n1)
        self.assertEqual(self.n5.get_root(), self.n1)

    def test_get_siblings(self):
        n1s = self.n1.get_siblings()
        self.assertEqual(n1s.count(), 0)

        n2s = self.n2.get_siblings()
        self.assertEqual(n2s.count(), 1)
        self.assertTrue(self.n5 in n2s)

        n5s = self.n5.get_siblings()
        self.assertEqual(n5s.count(), 1)
        self.assertTrue(self.n2 in n5s)

        n3s = self.n3.get_siblings()
        self.assertEqual(n3s.count(), 1)
        self.assertTrue(self.n4 in n3s)

        n4s = self.n4.get_siblings()
        self.assertEqual(n4s.count(), 1)
        self.assertTrue(self.n3 in n4s)

    def test_get_siblings_inc_self(self):
        n1s = self.n1.get_siblings(include_self=True)
        self.assertEqual(n1s.count(), 1)
        self.assertEqual(self.n1, n1s[0])

        n2s = self.n2.get_siblings(include_self=True)
        self.assertEqual(n2s.count(), 2)
        self.assertTrue(self.n2 in n2s)
        self.assertTrue(self.n5 in n2s)

        n5s = self.n5.get_siblings(include_self=True)
        self.assertEqual(n5s.count(), 2)
        self.assertTrue(self.n2 in n5s)
        self.assertTrue(self.n5 in n5s)

        n3s = self.n3.get_siblings(include_self=True)
        self.assertEqual(n3s.count(), 2)
        self.assertTrue(self.n3 in n3s)
        self.assertTrue(self.n4 in n3s)

        n4s = self.n4.get_siblings(include_self=True)
        self.assertEqual(n4s.count(), 2)
        self.assertTrue(self.n3 in n4s)
        self.assertTrue(self.n4 in n4s)

    def test_is_root_node(self):
        self.assertTrue(self.n1.is_root_node())
        self.assertFalse(self.n2.is_root_node())
        self.assertFalse(self.n3.is_root_node())
        self.assertFalse(self.n4.is_root_node())
        self.assertFalse(self.n5.is_root_node())

    def test_get_next_sibling(self):
        """
        kolejność będzie bądź jaka więc sprawdzam tylko, czy nie ma za dużo
        siblingów
        """
        self.assertTrue(self.n3.get_next_sibling() in (None, self.n4))
        self.assertTrue(self.n4.get_next_sibling() in (None, self.n3))

        self.assertTrue(self.n2.get_next_sibling() in (None, self.n5))
        self.assertTrue(self.n5.get_next_sibling() in (None, self.n2))

        if self.n3.get_next_sibling():
            self.assertEqual(self.n4, self.n3.get_next_sibling())
        else:
            self.assertEqual(self.n3, self.n4.get_next_sibling())

        if self.n2.get_next_sibling():
            self.assertEqual(self.n5, self.n2.get_next_sibling())
        else:
            self.assertEqual(self.n2, self.n5.get_next_sibling())

        if self.n3.get_next_sibling():
            self.assertNotEqual(self.n5, self.n3.get_next_sibling())
        else:
            self.assertNotEqual(self.n3, self.n5.get_next_sibling())

    def test_get_previous_sibling(self):
        """
        kolejność będzie bądź jaka więc sprawdzam tylko, czy nie ma za dużo
        siblingów
        """
        self.assertTrue(self.n3.get_previous_sibling() in (None, self.n4))
        self.assertTrue(self.n4.get_previous_sibling() in (None, self.n3))

        self.assertTrue(self.n2.get_previous_sibling() in (None, self.n5))
        self.assertTrue(self.n5.get_previous_sibling() in (None, self.n2))

        if self.n3.get_previous_sibling():
            self.assertEqual(self.n4, self.n3.get_previous_sibling())
        else:
            self.assertEqual(self.n3, self.n4.get_previous_sibling())

        if self.n2.get_previous_sibling():
            self.assertEqual(self.n5, self.n2.get_previous_sibling())
        else:
            self.assertEqual(self.n2, self.n5.get_previous_sibling())

        if self.n3.get_previous_sibling():
            self.assertNotEqual(self.n5, self.n3.get_previous_sibling())
        else:
            self.assertNotEqual(self.n3, self.n5.get_previous_sibling())

    def test_get_leafnodes(self):
        self.assertTrue(self.n3 in self.n1.get_leafnodes())
        self.assertTrue(self.n4 in self.n1.get_leafnodes())
        self.assertTrue(self.n5 in self.n1.get_leafnodes())
        self.assertFalse(self.n2 in self.n1.get_leafnodes())
        self.assertFalse(self.n1 in self.n1.get_leafnodes())

        self.assertTrue(self.n3 in self.n2.get_leafnodes())
        self.assertTrue(self.n4 in self.n2.get_leafnodes())
        self.assertFalse(self.n5 in self.n2.get_leafnodes())
        self.assertFalse(self.n2 in self.n2.get_leafnodes())
        self.assertFalse(self.n1 in self.n2.get_leafnodes())

        self.assertFalse(self.n3 in self.n3.get_leafnodes())
        self.assertFalse(self.n4 in self.n4.get_leafnodes())
        self.assertFalse(self.n5 in self.n5.get_leafnodes())

    def test_get_leafnodes_inc_self(self):
        self.assertTrue(self.n3 in self.n1.get_leafnodes(include_self=True))
        self.assertTrue(self.n4 in self.n1.get_leafnodes(include_self=True))
        self.assertTrue(self.n5 in self.n1.get_leafnodes(include_self=True))
        self.assertFalse(self.n2 in self.n1.get_leafnodes(include_self=True))
        self.assertFalse(self.n1 in self.n1.get_leafnodes(include_self=True))

        self.assertTrue(self.n3 in self.n2.get_leafnodes(include_self=True))
        self.assertTrue(self.n4 in self.n2.get_leafnodes(include_self=True))
        self.assertFalse(self.n5 in self.n2.get_leafnodes(include_self=True))
        self.assertFalse(self.n2 in self.n2.get_leafnodes(include_self=True))
        self.assertFalse(self.n1 in self.n2.get_leafnodes(include_self=True))

        self.assertTrue(self.n3 in self.n3.get_leafnodes(include_self=True))
        self.assertTrue(self.n4 in self.n4.get_leafnodes(include_self=True))
        self.assertTrue(self.n5 in self.n5.get_leafnodes(include_self=True))

    def test_is_leafnode(self):
        self.assertTrue(self.n3.is_leaf_node())
        self.assertTrue(self.n4.is_leaf_node())
        self.assertTrue(self.n5.is_leaf_node())
        self.assertFalse(self.n1.is_leaf_node())
        self.assertFalse(self.n2.is_leaf_node())

    def test_is_descendant_of(self):
        self.assertTrue(self.n2.is_descendant_of(self.n1))
        self.assertTrue(self.n3.is_descendant_of(self.n1))
        self.assertTrue(self.n4.is_descendant_of(self.n1))
        self.assertTrue(self.n5.is_descendant_of(self.n1))
        self.assertFalse(self.n1.is_descendant_of(self.n1))

        self.assertTrue(self.n3.is_descendant_of(self.n2))
        self.assertTrue(self.n4.is_descendant_of(self.n2))

        self.assertFalse(self.n3.is_descendant_of(self.n5))
        self.assertFalse(self.n2.is_descendant_of(self.n5))
        self.assertFalse(self.n4.is_descendant_of(self.n5))

    def test_is_descendant_of_inc_self(self):
        self.assertTrue(self.n2.is_descendant_of(self.n1, include_self=True))
        self.assertTrue(self.n3.is_descendant_of(self.n1, include_self=True))
        self.assertTrue(self.n4.is_descendant_of(self.n1, include_self=True))
        self.assertTrue(self.n5.is_descendant_of(self.n1, include_self=True))
        self.assertTrue(self.n1.is_descendant_of(self.n1, include_self=True))

        self.assertTrue(self.n3.is_descendant_of(self.n2, include_self=True))
        self.assertTrue(self.n4.is_descendant_of(self.n2, include_self=True))

        self.assertFalse(self.n3.is_descendant_of(self.n5, include_self=True))
        self.assertFalse(self.n2.is_descendant_of(self.n5, include_self=True))
        self.assertFalse(self.n4.is_descendant_of(self.n5, include_self=True))

    def test_is_childnode(self):
        self.assertFalse(self.n1.is_child_node())
        self.assertTrue(self.n2.is_child_node())
        self.assertTrue(self.n3.is_child_node())
        self.assertTrue(self.n4.is_child_node())
        self.assertTrue(self.n5.is_child_node())

    def test_is_ancestor_of(self):
        self.assertFalse(self.n2.is_ancestor_of(self.n1))
        self.assertFalse(self.n3.is_ancestor_of(self.n1))
        self.assertFalse(self.n4.is_ancestor_of(self.n1))
        self.assertFalse(self.n5.is_ancestor_of(self.n1))
        self.assertFalse(self.n1.is_ancestor_of(self.n1))

        self.assertFalse(self.n3.is_ancestor_of(self.n2))
        self.assertFalse(self.n4.is_ancestor_of(self.n2))

        self.assertFalse(self.n3.is_ancestor_of(self.n5))
        self.assertFalse(self.n2.is_ancestor_of(self.n5))
        self.assertFalse(self.n4.is_ancestor_of(self.n5))

    def test_is_ancestor_of_inc_self(self):
        self.assertFalse(self.n2.is_ancestor_of(self.n1, include_self=True))
        self.assertFalse(self.n3.is_ancestor_of(self.n1, include_self=True))
        self.assertFalse(self.n4.is_ancestor_of(self.n1, include_self=True))
        self.assertFalse(self.n5.is_ancestor_of(self.n1, include_self=True))
        self.assertTrue(self.n1.is_ancestor_of(self.n1, include_self=True))

        self.assertFalse(self.n3.is_ancestor_of(self.n2, include_self=True))
        self.assertFalse(self.n4.is_ancestor_of(self.n2, include_self=True))

        self.assertFalse(self.n3.is_ancestor_of(self.n5, include_self=True))
        self.assertFalse(self.n2.is_ancestor_of(self.n5, include_self=True))
        self.assertFalse(self.n4.is_ancestor_of(self.n5, include_self=True))

    def test_delete_leaf(self):
        self.assertEqual(Node._tpm.objects.count(), 12)
        self.n5.delete()
        self.assertEqual(Node._tpm.objects.count(), 10)
        self.n2.delete()
        self.assertEqual(Node._tpm.objects.count(), 2)
        self.assertEqual(Node.objects.count(), 2)

    def test_delete(self):
        self.n2.delete()
        self.assertEqual(Node._tpm.objects.count(), 4)
        self.assertEqual(Node.objects.count(), 3)

    def test_get_unique_ancestors(self):
        n7 = Node.objects.create(name='7', parent=self.n5)
        tst1 = self.n3._get_unique_ancestors(n7)
        self.assertTrue(self.n2 in tst1)
        self.assertFalse(self.n5 in tst1)
        self.assertFalse(self.n1 in tst1)
        self.assertFalse(self.n3 in tst1)
        self.assertFalse(self.n4 in tst1)
        self.assertFalse(self.n6 in tst1)
        self.assertFalse(n7 in tst1)

    def test_get_unique_ancestors_2(self):
        n7 = Node.objects.create(name='7', parent=self.n5)
        n8 = Node.objects.create(name='8', parent=self.n3)
        tst1 = n8._get_unique_ancestors(n7)
        self.assertTrue(self.n2 in tst1)
        self.assertTrue(self.n3 in tst1)
        self.assertFalse(self.n5 in tst1)
        self.assertFalse(self.n1 in tst1)
        self.assertFalse(self.n4 in tst1)
        self.assertFalse(self.n6 in tst1)
        self.assertFalse(n7 in tst1)
        self.assertFalse(n8 in tst1)

    def test_get_unique_ancestors_inc_self(self):
        n7 = Node.objects.create(name='7', parent=self.n5)
        tst1 = self.n3._get_unique_ancestors(n7, include_self=True)
        self.assertTrue(self.n2 in tst1)
        self.assertFalse(self.n5 in tst1)
        self.assertFalse(self.n1 in tst1)
        self.assertTrue(self.n3 in tst1)
        self.assertFalse(self.n4 in tst1)
        self.assertFalse(self.n6 in tst1)
        self.assertFalse(n7 in tst1)

    def test_get_unique_ancestors_inc_target(self):
        n7 = Node.objects.create(name='7', parent=self.n5)
        tst1 = self.n3._get_unique_ancestors(n7, include_target=True)
        self.assertTrue(self.n2 in tst1)
        self.assertFalse(n7 in tst1)
        self.assertFalse(self.n5 in tst1)
        self.assertFalse(self.n1 in tst1)
        self.assertFalse(self.n3 in tst1)
        self.assertFalse(self.n4 in tst1)
        self.assertFalse(self.n6 in tst1)

    def test_get_unique_ancestors_others(self):
        n7 = Node.objects.create(name='7', parent=self.n5)
        tst1 = self.n3._get_unique_ancestors(n7, others=True)
        self.assertTrue(self.n5 in tst1)
        self.assertFalse(self.n2 in tst1)
        self.assertFalse(self.n1 in tst1)
        self.assertFalse(self.n3 in tst1)
        self.assertFalse(self.n4 in tst1)
        self.assertFalse(self.n6 in tst1)
        self.assertFalse(n7 in tst1)

    def test_get_unique_ancestors_others_2(self):
        n7 = Node.objects.create(name='7', parent=self.n5)
        n8 = Node.objects.create(name='8', parent=self.n3)
        tst1 = n8._get_unique_ancestors(n7, others=True)
        self.assertTrue(self.n5 in tst1)
        self.assertFalse(self.n3 in tst1)
        self.assertFalse(self.n2 in tst1)
        self.assertFalse(self.n1 in tst1)
        self.assertFalse(self.n4 in tst1)
        self.assertFalse(self.n6 in tst1)
        self.assertFalse(n7 in tst1)
        self.assertFalse(n8 in tst1)

    def test_get_unique_ancestors_others_inc_self(self):
        n7 = Node.objects.create(name='7', parent=self.n5)
        tst1 = self.n3._get_unique_ancestors(n7, others=True, include_self=True)
        self.assertTrue(self.n5 in tst1)
        self.assertFalse(self.n3 in tst1)
        self.assertFalse(self.n2 in tst1)
        self.assertFalse(self.n1 in tst1)
        self.assertFalse(self.n4 in tst1)
        self.assertFalse(self.n6 in tst1)
        self.assertFalse(n7 in tst1)

    def test_get_unique_ancestors_others_inc_target(self):
        n7 = Node.objects.create(name='7', parent=self.n5)
        tst1 = self.n3._get_unique_ancestors(n7, others=True,
            include_target=True)
        self.assertTrue(self.n5 in tst1)
        self.assertTrue(n7 in tst1)
        self.assertFalse(self.n1 in tst1)
        self.assertFalse(self.n3 in tst1)
        self.assertFalse(self.n4 in tst1)
        self.assertFalse(self.n6 in tst1)
        self.assertFalse(self.n2 in tst1)

    def test_move_to_descendant(self):
        self.assertRaises(ValueError, self.n1.move_to, self.n2)

    def test_move_to_self(self):
        self.assertRaises(ValueError, self.n1.move_to, self.n1)

    def test_move_to(self):
        self.n3.move_to(self.n5)
        self.assertEqual(self.n3.parent, self.n5)
        self.assertNotEqual(self.n3.parent, self.n2)
        self.assertTrue(self.n5 in self.n3.get_ancestors())
        self.assertFalse(self.n2 in self.n3.get_ancestors())

    def test_move_to_by_save(self):
        self.assertEqual(self.n3.parent, self.n2)
        self.n3.parent = self.n5
        self.n3.save()
        self.assertEqual(self.n3.parent, self.n5)
        self.assertNotEqual(self.n3.parent, self.n2)
        self.assertTrue(self.n5 in self.n3.get_ancestors())
        self.assertFalse(self.n2 in self.n3.get_ancestors())

    def test_move_branch(self):
        self.n2.move_to(self.n5)

        self.assertEqual(self.n2.parent, self.n5)
        self.assertNotEqual(self.n2.parent, self.n1)

        self.assertTrue(self.n1 in self.n2.get_ancestors())
        self.assertTrue(self.n5 in self.n2.get_ancestors())

        self.assertTrue(self.n1 in self.n3.get_ancestors())
        self.assertTrue(self.n2 in self.n3.get_ancestors())
        self.assertTrue(self.n5 in self.n3.get_ancestors())

        self.assertTrue(self.n1 in self.n4.get_ancestors())
        self.assertTrue(self.n2 in self.n4.get_ancestors())
        self.assertTrue(self.n5 in self.n4.get_ancestors())

        self.assertFalse(self.n3 in self.n3.get_ancestors())
        self.assertFalse(self.n4 in self.n3.get_ancestors())
        self.assertFalse(self.n6 in self.n3.get_ancestors())

        self.assertFalse(self.n3 in self.n4.get_ancestors())
        self.assertFalse(self.n4 in self.n4.get_ancestors())
        self.assertFalse(self.n6 in self.n4.get_ancestors())

    def test_move_branch_by_save(self):
        self.n2.parent = self.n5
        self.n2.save()

        self.assertEqual(self.n2.parent, self.n5)
        self.assertNotEqual(self.n2.parent, self.n1)

        self.assertTrue(self.n1 in self.n2.get_ancestors())
        self.assertTrue(self.n5 in self.n2.get_ancestors())

        self.assertTrue(self.n1 in self.n3.get_ancestors())
        self.assertTrue(self.n2 in self.n3.get_ancestors())
        self.assertTrue(self.n5 in self.n3.get_ancestors())

        self.assertTrue(self.n1 in self.n4.get_ancestors())
        self.assertTrue(self.n2 in self.n4.get_ancestors())
        self.assertTrue(self.n5 in self.n4.get_ancestors())

        self.assertFalse(self.n3 in self.n3.get_ancestors())
        self.assertFalse(self.n4 in self.n3.get_ancestors())
        self.assertFalse(self.n6 in self.n3.get_ancestors())

        self.assertFalse(self.n3 in self.n4.get_ancestors())
        self.assertFalse(self.n4 in self.n4.get_ancestors())
        self.assertFalse(self.n6 in self.n4.get_ancestors())

    def test_level(self):
        for node in (self.n1, self.n2, self.n3, self.n4, self.n5, self.n6):
            self.assertEqual(node.level, node.get_level())

    def test_level_saved(self):
        for node in (self.n1, self.n2, self.n3, self.n4, self.n5, self.n6):
            readnode = Node.objects.get(pk=node.pk)
            self.assertEqual(readnode.level, node.get_level())


class CTTDummyOrderableTest(TestCase):
    def setUp(self):
        """
            1
           / \
          2   5
         / \
        3   4
        """
        self.n1 = NodeOrderable.objects.create(name='1')
        self.n2 = NodeOrderable.objects.create(name='2', parent=self.n1)
        self.n3 = NodeOrderable.objects.create(name='3', parent=self.n2)
        self.n4 = NodeOrderable.objects.create(name='4', parent=self.n2)
        self.n5 = NodeOrderable.objects.create(name='5', parent=self.n1)
        self.n6 = NodeOrderable.objects.create(name='6')

        self.root = self.n1

    def tearDown(self):
        NodeOrderable.objects.all().delete()

    def test_get_descendants(self):
        """

        """
        descendants = self.root.get_descendants()
        self.assertTrue(self.n2 in descendants)
        self.assertTrue(self.n3 in descendants)
        self.assertTrue(self.n4 in descendants)
        self.assertTrue(self.n5 in descendants)
        self.assertFalse(self.n1 in descendants)

    def test_original_order(self):
        self.assertEqual(self.n3.get_next_sibling(), self.n4)
        self.assertEqual(self.n4.get_previous_sibling(), self.n3)
        self.assertNotEqual(self.n4.get_next_sibling(), self.n3)
        self.assertNotEqual(self.n3.get_previous_sibling(), self.n4)

    def test_original_order_added(self):
        n7 = NodeOrderable.objects.create(name='7', parent=self.n2)
        self.assertEqual(n7.get_next_sibling(), None)
        self.assertEqual(n7.get_previous_sibling(), self.n4)

    def test_override_order(self):
        n7 = NodeOrderable.objects.create(name='7', parent=self.n2,
            order=self.n4.order)
        self.assertEqual(n7.get_next_sibling(), self.n4)
        self.assertEqual(n7.get_previous_sibling(), self.n3)

    def test_middle_order(self):
        n7 = NodeOrderable.objects.create(name='7', parent=self.n2,
            order=self.n4.order-1)
        self.assertEqual(n7.get_next_sibling(), self.n4)
        self.assertEqual(n7.get_previous_sibling(), self.n3)


class RebuildTreeMixin(object):

    def _create_tree(self):
        """
            1
           / \
          2   5
         / \
        3   4
        """
        # Create nodes in order that would break rebuild tree if it didn't
        # order them correctly
        self.n1 = Node.objects.create(name='1')
        self.n3 = Node.objects.create(name='3', parent=None)
        self.n4 = Node.objects.create(name='4', parent=None)
        self.n2 = Node.objects.create(name='2', parent=self.n1)
        self.n5 = Node.objects.create(name='5', parent=self.n1)
        self.n6 = Node.objects.create(name='6')
        self.root = self.n1
        self.n3.move_to(self.n2)
        self.n4.move_to(self.n2)


class CTTDummyRebuildTest(RebuildTreeMixin, CTTDummyTest):
    def setUp(self):
        super(CTTDummyRebuildTest, self).setUp()
        tpms_before = Node._tpm.objects.count()
        Node._tpm.objects.all().delete()
        self.assertNotEqual(tpms_before, Node._tpm.objects.count())
        Node._rebuild_tree()
        self.assertEqual(tpms_before, Node._tpm.objects.count())


class CTTDummyOrderableRebuildTest(RebuildTreeMixin, CTTDummyOrderableTest):
    def setUp(self):
        super(CTTDummyOrderableRebuildTest, self).setUp()
        tpms_before = NodeOrderable._tpm.objects.count()
        NodeOrderable._tpm.objects.all().delete()
        self.assertNotEqual(tpms_before, NodeOrderable._tpm.objects.count())
        NodeOrderable._rebuild_tree()
        self.assertEqual(tpms_before, NodeOrderable._tpm.objects.count())
