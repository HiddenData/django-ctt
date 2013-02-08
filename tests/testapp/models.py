#!/usr/bin/env python
#-*- coding: utf-8 -*-
#vim: set ts=4 sw=4 et fdm=marker : */
from django.db import models
import ctt
from ctt.models import CTTModel, CTTOrderableModel

class Node(CTTModel):
    name = models.CharField(max_length=255)


ctt.register(Node)


class NodeOrderable(CTTOrderableModel):
    name = models.CharField(max_length=255)


ctt.register(NodeOrderable)
