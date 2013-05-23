#!/usr/bin/env python
#-*- coding: utf-8 -*-
#vim: set ts=4 sw=4 et fdm=marker : */

"""
Closure Tables Tree models.
"""
from django.db import models
from django.db.models.query_utils import Q
from ctt.decorators import filtered_qs
from django.utils.translation import ugettext as _


class CTTModel(models.Model):
    parent = models.ForeignKey('self', null=True, blank=True)
    level = models.IntegerField(default=0, blank=True)
    _tpm = None # overwrite by core.register()
    tpd = None # overwrite by core.register()
    tpa = None # overwrite by core.register()
    _cls = None

    class Meta:
        abstract = True

    class CTTMeta:
        parent_field = 'parent'

    def __unicode__(self):
        if hasattr(self, 'name'):
            return self.name
        return unicode(self.id)

    def save(self, force_insert=False, force_update=False, using=None):
        is_new = self.pk is None
        if not is_new:
            old_parent = self._cls.objects.get(pk=self.pk).parent
        else:
            old_parent = None
        if self.parent:
            self.level = self.parent.level + 1
        else:
            self.level = 0
        super(CTTModel, self).save(force_insert, force_update, using)
        if is_new:
            self.insert_at(self.parent, save=False, allow_existing_pk=True)
        elif not self.parent and not old_parent:
            pass
        elif not self.parent or not old_parent:
            self.move_to(self.parent)
        elif old_parent.pk != self.parent.pk:
            self.move_to(self.parent)

    def get_ancestors(self, ascending=False, include_self=False):
        ancestors = self._cls.objects.filter(tpa__descendant_id=self.id)
        if not include_self:
            ancestors = ancestors.exclude(id=self.id)
        if ascending:
            ancestors = ancestors.order_by('tpa__path_len')
        else:
            ancestors = ancestors.order_by('-tpa__path_len')
        return ancestors

    @filtered_qs
    def get_children(self):
        nodes = self._cls.objects.filter(
            Q(tpd__ancestor_id=self.id) & Q(tpd__path_len=1)
        )
        return nodes

    def get_descendant_count(self):
        return self.get_descendants().count()

    def get_descendants(self, include_self=False):
        nodes = self._cls.objects.filter(tpd__ancestor_id=self.id)
        if not include_self:
            nodes = nodes.exclude(id=self.id)
        return nodes

    def get_leafnodes(self, include_self=False):
        nodes = self.get_descendants(include_self=include_self)
        nodes = nodes.exclude(tpa__path_len__gt=0)
        return nodes

    def get_level(self):
        return self.level

    def _get_next_from_qs(self, qs):
        take = False
        for item in qs:
            if take:
                return item
            if item == self:
                take = True
        return None

    def get_next_sibling(self, **filters):
        """
        jak chcesz mieć dobrą kolejność to korzystaj z CTTOrderableModel!
        """
        siblings = self.get_siblings(include_self=True).filter(**filters)
        return self._get_next_from_qs(siblings)

    def get_previous_sibling(self, **filters):
        """
        jak chcesz mieć dobrą kolejność to korzystaj z CTTOrderableModel!
        """
        siblings = self.get_siblings(include_self=True).filter(**filters)
        return self._get_next_from_qs(siblings.reverse())

    def get_siblings(self, include_self=False):
        if not self.parent:
            nodes = self._cls.objects.filter(id=self.id)
        else:
            nodes = self._cls.objects.filter(
                Q(tpd__ancestor_id=self.parent_id) & Q(tpd__path_len=1)
            )
        if not include_self:
            nodes = nodes.exclude(id=self.id)
        return nodes

    def get_root(self):
        return self.tpd.latest('path_len').ancestor

    def insert_at(self, target, position='first-child', save=False,
                  allow_existing_pk=False):
        """
        manager.insert_node
        """
        if not self.pk:
            self.save()
            return

        if self.pk and not allow_existing_pk and\
           self._cls.objects.filter(pk=self.pk).exists():
            raise ValueError(
                _('Cannot insert a node which has already been saved.'))

        if target:
            self.parent = target
            path = target.get_ancestors(ascending=True,
                include_self=True).only('id')
        else:
            path = []
        tree_paths = [self._tpm(ancestor_id=self.id, descendant_id=self.id,
            path_len=0), ]
        path_len = 1
        for node in path:
            tree_paths.append(
                self._tpm(ancestor_id=node.id, descendant_id=self.id,
                    path_len=path_len)
            )
            path_len += 1
        self._tpm.objects.bulk_create(tree_paths)

        if save:
            self.save()


    def is_ancestor_of(self, other, include_self=False):
        nodes = other.get_ancestors(include_self=include_self)
        return self in nodes

    def is_child_node(self):
        return not self.is_root_node()

    def is_descendant_of(self, other, include_self=False):
        nodes = other.get_descendants(include_self=include_self)
        return self in nodes


    def is_leaf_node(self):
        return self._cls.objects.filter(
            tpd__ancestor_id=self.id).count() == 1

    def is_root_node(self):
        return self.level == 0

    def _get_unique_ancestors(self, target, others=False, include_self=False,
                              include_target=False):
        """
            1
           / \
          2   5
         / \   \
        3   4   6

        3._get_unique_ancestors(6) = 2
        3._get_unique_ancestors(6, True) = 5

        ! include_target zadziała tylko dla others=True
        ! include_self zadziała tylko dla others=False

        pozniej to opisze jakos...
        :param others:
        :return:
        """
        #        ancestors = self._cls.objects.filter(tpa__descendant_id=self.id)
        if others:
            uni_ancestors = self._cls.objects.filter(
                Q(tpa__descendant_id=target.id)
                &
                ~Q(tpa__descendant_id=self.id)
            )
        else:
            uni_ancestors = self._cls.objects.filter(
                Q(tpa__descendant_id=self.id)
                &
                ~Q(tpa__descendant_id=target.id)
            )
        if not include_self:
            uni_ancestors = uni_ancestors.exclude(id=self.id)
        if not include_target:
            uni_ancestors = uni_ancestors.exclude(id=target.id)
        return uni_ancestors

    def move_to(self, target, position='first-child'):
        if self in target.get_ancestors(include_self=True):
            raise ValueError(_('Cannot move node to its descendant or itself.'))

        old_parent = self._cls.objects.get(pk=self.pk).parent
        if old_parent is target:
            return

        self.tpd.all().delete()
        self.insert_at(target, save=True, allow_existing_pk=True)

        descendants = self.get_descendants()
        for node in descendants:
            node.tpd.all().delete()
            node.insert_at(node.parent, save=False, allow_existing_pk=True)

    @classmethod
    def _rebuild_tree(cls):
        """
        mało sprytne, ale pewne :)
        :param cls:
        :return:
        """
        cls._tpm.objects.all().delete()
        for node in cls._cls.objects.all().order_by('level'):
            node.insert_at(node.parent, allow_existing_pk=True)

    @classmethod
    def _rebuild_qs(cls, qs):
        """
        Przebudowuje wszystkie ścieżki przechodzące przez qs, powolne,
        używaj _rebuild_tree chyba że wiesz co robisz.
        """

        def item_descendants(item, result=None):
            if not result:
                result = []

            children = list(cls._cls.objects.filter(parent=item))
            result.extend(children)
            for c in children:
                item_descendants(c, result)

            return result

        def item_ancestors(item, result=None):
            if not result:
                result = []

            while item:
                result.append(item)
                item = item.parent

            return result

        related_nodes = set()
        for item in qs:
            # Get parents:
            related_nodes = related_nodes.union(item_ancestors(item))
            related_nodes = related_nodes.union(item_descendants(item))

        tpms = cls._tpm.objects.filter(
            ancestor__in=related_nodes,
            descendant__in=related_nodes)

        tpms.delete()

        for node in sorted(related_nodes, key=lambda i: i.level):
            node.insert_at(node.parent, allow_existing_pk=True)


class CTTOrderableModel(CTTModel):
    order = models.IntegerField()
    _interval = 10

    class Meta:
        abstract = True
        ordering = ('order',)

    def get_next_sibling(self, **filters):
        siblings = self.get_siblings().filter(**filters)
        ret_node = siblings.filter(order__gt=self.order)
        if not ret_node:
            return None
        return ret_node[0]

    def get_previous_sibling(self, **filters):
        siblings = self.get_siblings().filter(**filters)
        ret_node = siblings.filter(order__lt=self.order).reverse()
        if not ret_node:
            return None
        return ret_node[0]

    def get_children(self):
        return super(CTTOrderableModel, self).get_children().order_by('order')

    def get_siblings(self, include_self=False):
        return super(CTTOrderableModel, self).get_siblings(
            include_self).order_by('order')

    def save(self, force_insert=False, force_update=False, using=None):
        self._fix_order()
        super(CTTOrderableModel, self).save(force_insert, force_update, using)

    def _push_forward(self, from_pos):
        new_order = from_pos + self._interval
        siblings = self.get_siblings()
        to_push = siblings.filter(order__gt=self.order, order__lte=new_order).\
        order_by('order')
        if to_push.exists():
            to_push[0]._push_forward(new_order)

        self.order = new_order
        self.save()

    def move_before(self, sibling):
        before = self.get_siblings().filter(order__lt=sibling.order).\
        order_by('-order')
        if before.exists():
            self.order = before[0].order + 1
        else:
            self.order = sibling.order - self._interval

    def move_after(self, sibling):
        self.order = sibling.order + 1

    def _fix_order(self):
        if not self.order:
            if self.get_siblings().exists():
                max_order_sibling = self.get_siblings().order_by('-order')[0]
                self.order = max_order_sibling.order + self._interval
            else:
                self.order = 0

        self._check_order_conflicts()

    def _check_order_conflicts(self):
        conflicts = self.get_siblings().filter(order=self.order)
        if self.pk:
            conflicts = conflicts.exclude(pk=self.pk)

        if conflicts.exists():
            conflicts[0]._push_forward(self.order)
