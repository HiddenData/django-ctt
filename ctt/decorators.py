#!/usr/bin/env python
#-*- coding: utf-8 -*-
#vim: set ts=4 sw=4 et fdm=marker : */
import functools


def filtered_qs(func):
    """
    #TODO: zrobić, obsługę funkcji z argumentami
    :param func:
    :return:
    """

    @functools.wraps(func)
    def wrapped(self, *args, **kwargs):
        ret_qs = func(self)
        return ret_qs.filter(*args, **kwargs)

    return wrapped

