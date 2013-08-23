#!/usr/bin/env python3

from collections import Counter
from datetime import datetime
from functools import partial
from random import sample
import time

from numpy import array
from yaml import load as yload

from vectorpack.packs import get_pack_by_name
from vectorpack.sorts import get_sort_key_by_name
from vectorpack.selects import get_select_by_name
from vectorpack.util import verify_mapping, negate_func, zero


def parse_sort_cmdline(sortcmd):
    args = sortcmd.split(":")

    arg = args.pop(0)
    desc = False
    if arg in [ "a", "d" ]:
        if arg is "d":
            desc = True
        arg = args.pop(0)

    sort_key = get_sort_key_by_name(arg)

    kwargs = {}
    if args:
        kwargs.update(yload("\n".join(arg.replace('=', ': ') for arg in args)))

    if desc:
        return partial(negate_func, sort_key, **kwargs)

    if kwargs:
        return partial(sort_key, **kwargs)

    return sort_key


def parse_select_cmdline(sortcmd):
    args = sortcmd.split(":")

    arg = args.pop(0)
    desc = False
    if arg in [ "a", "d" ]:
        if arg is "d":
            desc = True
        arg = args.pop(0)

    select_key = get_select_by_name(arg)

    kwargs = {}
    if args:
        kwargs.update(yload("\n".join(arg.replace('=', ': ') for arg in args)))

    if desc:
        return partial(negate_func, select_key, **kwargs)

    if kwargs:
        return partial(select_key, **kwargs)

    return select_key


def vpsolver(pack=None, select=None, itemsort=None, binsort=None, split=1, 
             problem=None):

    pack_func = get_pack_by_name(pack)
    item_key = parse_sort_cmdline(itemsort)
    bin_key = parse_sort_cmdline(binsort)
    select_key = parse_select_cmdline(select)

    itemfuncs = problem.get('itemfuncs', [])
    bins = problem.get('bins', [])

    mapping = [None] * len(itemfuncs)

    y_upper = 1.0
    y_lower = 0.0
    y_threshold = 0.001
    y = 0.0

    start_time = time.process_time()
    while y_upper - y_lower > y_threshold:
        y = (y_upper + y_lower) / 2
        item_insts = [eval(i)(y) for i in itemfuncs]
        # FIXME: could be smarter and only sort bins once...
        curr_mapping = pack_func(items=item_insts, bins=bins, 
                       item_key=item_key, bin_key=bin_key, 
                       select_key=select_key, split=split)
        if curr_mapping.count(None) > 0:
            y_upper = y
        else:
            mapping = curr_mapping[:]
            y_lower = y
    y = y_lower
    stop_time = time.process_time()

    solution = {
        'pack' : pack,
        'itemsort' : itemsort,
        'binsort' : binsort,
        'select' : select,
        'split' : split,
        'yield' : y,
        'datetime' : datetime.now(),
        'mapping' : mapping,
        'failcount' : mapping.count(None),
        'bincount' : len(Counter(mapping)),
        'verified' : verify_mapping(items=item_insts, bins=bins, mapping=mapping),
        'runtime' : stop_time - start_time,
    }
    solution.update(problem)
    return solution
