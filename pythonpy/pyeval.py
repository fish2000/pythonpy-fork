#!/usr/bin/env python3
from __future__ import (unicode_literals, absolute_import,
                        print_function, division)

from functools import lru_cache
from itertools import count, islice
from signal import signal, SIGPIPE, SIG_DFL

signal(SIGPIPE, SIG_DFL)

import argparse
import collections
import collections.abc
import contextlib
import importlib
import inspect
import json
import pydoc
import sys, re, io
import os, site

if 'VIRTUAL_ENV' in os.environ:
    # derived from activate_this.py from the virtualenv package
    base = os.environ['VIRTUAL_ENV']
    os.environ['PATH'] = os.pathsep.join([os.path.join(base, 'bin')] + os.environ['PATH'].split(os.pathsep))
    prev_length = len(sys.path)
    site.addsitedir(os.path.realpath(site._get_path(base)))
    sys.path[:] = sys.path[prev_length:] + sys.path[0:prev_length]
    sys.prefix = base
sys.path.insert(0, '')

cache = lambda function: lru_cache(maxsize=128, typed=True)(function)

try:
    from pythonpy.__version__ import __version__
except (ImportError, ValueError, SystemError):
    __version__ = '0.5.4'

pyversion = sys.version.split(' ')[0]
version_string = f'''Pythonpy {__version__}
Python {pyversion}'''

module_aliases = {
    'mp'    : 'matplotlib',
    'np'    : 'numpy',
    'pd'    : 'pandas',
    'tf'    : 'tensorflow',
    'xa'    : 'xarray'
}

ModuleAlias = collections.namedtuple('ModuleAlias', ('shorthand', 'modname'))
IOHandles   = collections.namedtuple('IOHandles', ('out', 'err'))

aliases     = { re.compile(rf"^{key}") : ModuleAlias(shorthand=key, modname=value) \
                                                                   for key, value \
                                                                    in module_aliases.items() }

def iterlen(iterable):
    """ iterlen(iterable) → Return the number of items in “iterable.”
        
        This will consume iterables without a “__len__()” method – be careful!
    """
    # Stolen from “more-itertools”: http://bit.ly/2LUZqCx
    try:
        return len(iterable)
    except TypeError as exc:
        if 'has no len' in str(exc):
            counter = count()
            collections.deque(zip(iterable, counter), maxlen=0)
            return next(counter)
        raise

@cache
def import_matches(query, prefix=''):
    
    for raw_module_name in frozenset(
                           re.findall(
                           rf"({prefix}[a-zA-Z_][a-zA-Z0-9_]*)\.?", query)):
        
        module_name = raw_module_name
        
        # Only de-alias module names at the top level,
        # and at most de-alias once:
        if prefix == '':
            for rgx, alias in aliases.items():
                if rgx.match(module_name):
                    module_name = rgx.sub(alias.modname, module_name)
                    break
        
        try:
            module = importlib.import_module(module_name)
        
        except (ModuleNotFoundError, ImportError):
            pass
        
        else:
            globals()[raw_module_name] = module
            if module_name != raw_module_name:
                globals()[module_name] = module
            yield module
            yield from import_matches(query, prefix=rf"{module_name}\.")

def lazy_imports(*args):
    query = ' '.join(x for x in args if x)
    yield from import_matches(query)

def current_list(input):
    return current_list.rgx.split(input)

current_list.rgx = re.compile(r'[^a-zA-Z0-9_\.]')

def inspect_source(instance):
    try:
        return ''.join(inspect.getsourcelines(instance)[0])
    except:
        return help(instance)

parser = argparse.ArgumentParser(
            formatter_class=argparse.RawDescriptionHelpFormatter,
            add_help=False)

group = parser.add_argument_group("Options")

parser.add_argument('expression', nargs='?', default='None',
                    help="e.g. “py '2 ** 32'”")

group.add_argument('-x', dest='lines_of_stdin',
                    action='store_const',
                    const=True, default=False,
                    help='treat each row of stdin as “x”')

group.add_argument('-fx', dest='filter_result',
                    action='store_const',
                    const=True, default=False,
                    help=argparse.SUPPRESS)

group.add_argument('-l', dest='list_of_stdin',
                    action='store_const',
                    const=True, default=False,
                    help='treat list of stdin as “l”')

group.add_argument('--ji', '--json_input',
                    dest='json_input',
                    action='store_const',
                    const=True, default=False,
                    help=argparse.SUPPRESS)

group.add_argument('--jo', '--json_output',
                    dest='json_output',
                    action='store_const',
                    const=True, default=False,
                    help=argparse.SUPPRESS)

group.add_argument('--si', '--split_input',
                    dest='input_delimiter',
                    help=argparse.SUPPRESS)

group.add_argument('--so', '--split_output',
                    dest='output_delimiter',
                    help=argparse.SUPPRESS)

group.add_argument('-p', '--pager',
                    dest='pager',
                    action='store_const',
                    const=True, default=False,
                    help=argparse.SUPPRESS)

group.add_argument('-c', dest='pre_cmd', help='run code before expression')
group.add_argument('-C', dest='post_cmd', help='run code after expression')

group.add_argument('--i', '--ignore_exceptions',
                    dest='ignore_exceptions',
                    action='store_const',
                    const=True, default=False,
                    help=argparse.SUPPRESS)

group.add_argument('-v', '--verbose',
                    dest='verbosity',
                    action='count', default=0,
                    help='set the verbosity level (default=0)')

group.add_argument('-V', '--version', action='version',
                    version=version_string,
                    help='show the current version and exit')

group.add_argument('-h', '--help', action='help',
                    help="show this help message and exit")

def exit(*args, **kwargs):
    """ Craft and return (without raising!) a SystemExit exception """
    exc = SystemExit("\n\t".join(args))
    return exc

@contextlib.contextmanager
def redirect(args):
    """ Redirect “stdout” and “stderr” at the same time """
    out, err = io.StringIO(), io.StringIO()
    
    with contextlib.ExitStack() as ctx:
        ctx.enter_context(contextlib.redirect_stdout(out))
        ctx.enter_context(contextlib.redirect_stderr(err))
        iohandles = IOHandles(out=out, err=err)
        
        try:
            yield iohandles
        
        except SystemExit as exc:
            raise exit("[ERROR] in cluval execution:", str(exc))
        
        except BaseException as exc:
            import traceback
            pyheader = 'pythonpy/pyeval.py'
            exprheader = 'File "<string>"'
            foundexpr = False
            lines = traceback.format_exception(*sys.exc_info())
            for line in lines:
                if pyheader in line:
                    continue
                iohandles.err.write(line)
                if not foundexpr and line.lstrip().startswith(exprheader) and not isinstance(exc, SyntaxError):
                    iohandles.err.write('    {}\n'.format(args.expression))
                    foundexpr = True
            
            raise exit(iohandles.err.getvalue())

def safe_eval(code, x):
    try:
        return eval(code)
    except:
        return None

def pyeval(argv=None):
    """ Evaluate a Python expression from a set of CLI arguments. """
    
    args = parser.parse_args(argv or sys.argv[1:])
    
    with redirect(args) as iohandles:
        
        if sum([args.list_of_stdin, args.lines_of_stdin, args.filter_result]) > 1:
            raise exit('Pythonpy accepts at most one of [-x, -l] flags\n')
        
        if args.json_input:
            
            def loads(string):
                try:
                    return json.loads(string.rstrip())
                except BaseException as exc:
                    if args.ignore_exceptions:
                        pass
                    else:
                        raise exc
            
            stdin = (loads(x) for x in sys.stdin)
        
        elif args.input_delimiter:
            stdin = (re.split(args.input_delimiter, x.rstrip()) for x in sys.stdin)
        
        else:
            stdin = (x.rstrip() for x in sys.stdin)
        
        if args.expression:
            args.expression = args.expression.replace("`", "'")
            
            if args.expression.endswith('…'):
                args.expression = args.expression[:-1]
                args.pager = True
            
            if args.expression.startswith('?') or args.expression.endswith('?'):
                
                final_atom = current_list(args.expression.rstrip('?'))[-1]
                first_atom = current_list(args.expression.lstrip('?'))[0]
                
                if args.expression.startswith('??'):
                    args.expression = f"inspect_source({first_atom})"
                elif args.expression.endswith('??'):
                    args.expression = f"inspect_source({final_atom})"
                elif args.expression.startswith('?'):
                    args.expression = f'inspect.getdoc({first_atom})'
                else:
                    args.expression = f'inspect.getdoc({final_atom})'
                args.pager = True
                
                if args.lines_of_stdin:
                    stdin = islice(stdin, 1)
            
            if args.expression.startswith('help('):
                args.pager = True
        
        if args.pre_cmd:
            args.pre_cmd = args.pre_cmd.replace("`", "'")
        
        if args.post_cmd:
            args.post_cmd = args.post_cmd.replace("`", "'")
        
        # DO THE IMPORTS:
        modules = tuple(lazy_imports(args.expression,
                                     args.pre_cmd,
                                     args.post_cmd))
        
        if args.pre_cmd:
            exec(args.pre_cmd)
        
        if args.lines_of_stdin:
            
            if args.ignore_exceptions:
                result = (safe_eval(args.expression, x) for x in stdin)
            else:
                result = (eval(args.expression) for x in stdin)
        
        elif args.filter_result:
            
            if args.ignore_exceptions:
                result = (x for x in stdin if safe_eval(args.expression, x))
            else:
                result = (x for x in stdin if eval(args.expression))
        
        elif args.list_of_stdin:
            
            locals()['l'] = list(stdin)
            result = eval(args.expression)
        
        else:
            result = eval(args.expression)
        
        def prepare(output):
            if output is None:
                return None
            elif args.json_output:
                return json.dumps(output)
            elif args.output_delimiter:
                return args.output_delimiter.join(output)
            else:
                return output
        
        if isinstance(result, collections.abc.Iterable) and not \
           isinstance(result, (str, bytes)):
            for x in result:
                formatted = prepare(x)
                if formatted is not None:
                    iohandles.out.write(f"{formatted}\n")
        else:
            formatted = prepare(result)
            if formatted is not None:
                iohandles.out.write(f"{formatted}\n")
        
        if args.post_cmd:
            exec(args.post_cmd)
        
        sys.stdout.flush()
    
    # Extract rerouted «stdout» value:
    out = iohandles.out.getvalue()
    
    # Return extracted «stdout» and whether or not to page:
    return out, args.pager

def main():
    out, pager = pyeval()
    if pager:
        pydoc.pager(out)
    else:
        print(out, end='')

if __name__ == '__main__':
    main()
