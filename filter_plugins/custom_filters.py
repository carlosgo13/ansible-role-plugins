from jinja2.utils import soft_unicode
from collections import defaultdict
import copy
import itertools


def is_hash(d):
    return callable(getattr(d, 'get', None))


def merge_dicts(x, y):
    z = x.copy()
    z.update(y)
    return z


def merge_dicts_reverse(x, y):
    return merge_dicts(y, x)


def filename(basename):
    return (basename.split('.')[0])


def map_format(value, pattern):
    """
    Apply python string formatting on an object:
    .. sourcecode:: jinja
        {{ "%s - %s"|format("Hello?", "Foo!") }}
            -> Hello? - Foo!
    """
    if type(value) == str and type(pattern) == str:
        try:
            result = soft_unicode(pattern) % value
        except TypeError:
            result = pattern
    elif is_hash(value) and is_hash(pattern):
        def constant_factory(value):
            return lambda: value
        p = defaultdict(constant_factory("%s"))
        p.update(pattern)
        result = dict([
            [k, map_format(v, p[k])] for k, v in value.items()
        ])
    else:
        assert False, \
            f"unsupported argument types " + \
            "(#{type(value)}, #{type(pattern)})!= (str, str) | (dict, dict)"
    return result


def reverse_record(record):
    def reverse_address(addr):
        rev = '.'.join(addr.split('.')[::-1])
        return("{0}.{1}".format(rev, 'in-addr.arpa'))
    return ({
        'host': reverse_address(record['ip-address']),
        'ip-address': record['host'],
        'type': 'PTR'
    })


def with_ext(basename, ext):
    return ("{0}.{1}".format(filename(basename), ext))


def zone_fwd(zone, servers):
    return({
        'zone "{0}" IN'.format(zone): {
            'type': 'forward',
            'forward': 'only',
            'forwarders': servers
        }
    })


def head(x):
    return(x[0])


def tail(x):
    return(x[1::])


def split_with(x, d):
    return(x.split(d))


def join_with(x, d):
    return d.join(x)


def alias_keys(d, alias={}):
    new_dict = copy.deepcopy(d)
    for k, v in list(alias.items()):
        new_dict[v] = new_dict[k]
    return new_dict


def select_attributes(d, atts):
    new_dict = {}
    for k, v in list(d.items()):
        if k in atts:
            new_dict[k] = d[k]
    return new_dict


def drop_attributes(d, x):
    new_dict = copy.deepcopy(d)
    for y in list(itertools.chain.from_iterable([x])):
        if y in d:
            del new_dict[y]
    return new_dict


def to_dict(x, key=None):
    if key is None:
        result = dict(x)
    else:
        if type(key) == str:
            result = {key: x}
        if is_hash(key):
            result = dict([
                [k, map_format(x, v)] for k, v in key.items()
            ])
    return result


def merge_item(item, key_attr):
    return dict(merge_dicts(item[1], to_dict(item[0], key_attr)))


def key_item(item, key_attr, remove_key=True):
    new_item = copy.deepcopy(item)
    if remove_key:
        del new_item[key_attr]
    return [item[key_attr], new_item]


def dict_to_list(d, key_attr):
    return [merge_item(item, key_attr) for item in d.items()]


def list_to_dict(l, key_attr, remove_key=True):
    return dict([key_item(x, key_attr, remove_key) for x in l])


class FilterModule(object):
    ''' jinja2 filters '''

    def filters(self):
        return {
            'split_with': split_with,
            'join_with': join_with,
            'head': head,
            'tail': tail,
            'map_format': map_format,
            'reverse_record': reverse_record,
            'zone_fwd': zone_fwd,
            'alias_keys': alias_keys,
            'merge_dicts': merge_dicts,
            'select_attributes': select_attributes,
            'merge_dicts_reverse': merge_dicts_reverse,
            'to_dict': to_dict,
            'merge_item': merge_item,
            'key_item': key_item,
            'dict_to_list': dict_to_list,
            'list_to_dict': list_to_dict
        }
