#!/usr/bin/env python
# -*- coding: utf-8 -*-
# vim: set ts=4 sw=4 et fdm=marker : */
from django.db import models


class TreePathModel(models.Model):
    #    ancestor = models.ForeignKey('Node', related_name='tpa')
    #    descendant = models.ForeignKey('Node', related_name='tpd')
    path_len = models.IntegerField(db_index=True)

    class Meta:
        unique_together = ('ancestor', 'descendant')
        abstract = True
        index_together = [
            ["ancestor", "descendant", "path_len"],
        ]

    def __unicode__(self):
        return '%s -> %s (%d)' % (self.ancestor, self.descendant, self.path_len)


def register(cls):
    """
    generuje TreePathModel dla podanego modelu
    :param cls:
    :return:
    """
    tpcls = type(cls.__name__ + 'TreePath',
                 (TreePathModel,),
                 {'__module__': cls.__module__})
    ancestor_field = models.ForeignKey(cls, related_name='tpa')
    descendant_field = models.ForeignKey(cls, related_name='tpd')
    ancestor_field.contribute_to_class(tpcls, 'ancestor')
    descendant_field.contribute_to_class(tpcls, 'descendant')
    cls._tpm = tpcls
    cls._cls = cls
    return tpcls
