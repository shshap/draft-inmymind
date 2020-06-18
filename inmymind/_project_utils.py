import inspect
import logging
import pathlib
import sys

logger = logging.getLogger(__name__)


def dynamic_import(path_to_items_subpackage='', func_name_if_class=None,
                   first_word='', url=''):
    items_dict = {}
    root = pathlib.Path(path_to_items_subpackage).absolute()
    logger.debug(f'{root=}')
    sys.path.insert(0, str(root.parent))
    for path in root.iterdir():
        if path.suffix == '.py' and not path.stem.startswith('_'):
            mod = __import__(f'{root.name}.{path.stem}', fromlist=['*'])
            for attr in dir(mod):
                _handle_attr(attr, mod, items_dict, func_name_if_class, first_word, url)
    return items_dict


def _handle_attr(attr, mod, dict_items, func_name_if_class, first_word, url):
    if not attr.lower().startswith(first_word.lower()):
        return
    g = getattr(mod, attr)
    if inspect.isfunction(g):
        if func_name_if_class is None:
            return
        else:
            func = g
    elif inspect.isclass(g):
        if func_name_if_class is None:
            func = g
        else:
            try:
                func = getattr(g(url), func_name_if_class)
            except AttributeError:
                return
    else:
        return
    name = g.__name__.split('_')
    dict_items[tuple([field.lower() for field in name[1:]])] = func
