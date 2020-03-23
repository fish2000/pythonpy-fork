#!/usr/bin/env python3
from __future__ import (unicode_literals, absolute_import,
                        print_function, division)
import sys

# if sys.version_info.major == 2:
#     reload(sys)
#     sys.setdefaultencoding('utf-8')
from itertools import islice

from signal import signal, SIGPIPE, SIG_DFL
signal(SIGPIPE, SIG_DFL)

import argparse
import collections
import collections.abc
import contextlib
import inspect
import json
import re, io

try:
    from . import __version__
except (ImportError, ValueError, SystemError):
    __version__ = '???'  # NOQA
__version_info__ = '''Pythonpy %s
Python %s''' % (__version__, sys.version.split(' ')[0])

def import_matches(query, prefix=''):
    matches = set(re.findall(r"(%s[a-zA-Z_][a-zA-Z0-9_]*)\.?" % prefix, query))
    
    for raw_module_name in matches:
        
        if re.match(r'np(\..*)?$', raw_module_name):
            module_name = re.sub('^np', 'numpy', raw_module_name)
        elif re.match(r'pd(\..*)?$', raw_module_name):
            module_name = re.sub('^pd', 'pandas', raw_module_name)
        else:
            module_name = raw_module_name
        
        try:
            module = __import__(module_name)
            globals()[raw_module_name] = module
            import_matches(query, prefix='%s.' % module_name)
        
        except ImportError as exc:
            assert exc
            pass

def lazy_imports(*args):
    query = ' '.join([x for x in args if x])
    import_matches(query)

def current_list(input):
    return re.split(r'[^a-zA-Z0-9_\.]', input)

def inspect_source(obj):
    import pydoc
    
    try:
        pydoc.pager(''.join(inspect.getsourcelines(obj)[0]))
        return None
    except:
        return help(obj)

parser = argparse.ArgumentParser(
            formatter_class=argparse.RawDescriptionHelpFormatter,
            add_help=False)

group = parser.add_argument_group("Options")

parser.add_argument('expression', nargs='?', default='None', help="e.g. py '2 ** 32'")
group.add_argument('-x', dest='lines_of_stdin', action='store_const',
                    const=True, default=False,
                    help='treat each row of stdin as x')
group.add_argument('-fx', dest='filter_result', action='store_const',
                    const=True, default=False,
                    help=argparse.SUPPRESS)
group.add_argument('-l', dest='list_of_stdin', action='store_const',
                    const=True, default=False,
                    help='treat list of stdin as l')
group.add_argument('--ji', '--json_input',
                    dest='json_input', action='store_const',
                    const=True, default=False,
                    help=argparse.SUPPRESS)
group.add_argument('--jo', '--json_output',
                    dest='json_output', action='store_const',
                    const=True, default=False,
                    help=argparse.SUPPRESS)
group.add_argument('--si', '--split_input', dest='input_delimiter',
                    help=argparse.SUPPRESS)
group.add_argument('--so', '--split_output', dest='output_delimiter',
                    help=argparse.SUPPRESS)
group.add_argument('-c', dest='pre_cmd', help='run code before expression')
group.add_argument('-C', dest='post_cmd', help='run code after expression')
group.add_argument('--i', '--ignore_exceptions',
                    dest='ignore_exceptions', action='store_const',
                    const=True, default=False,
                    help=argparse.SUPPRESS)
group.add_argument('-V', '--version', action='version', version=__version_info__, help='version info')
group.add_argument('-h', '--help', action='help', help="show this help message and exit")

def pyeval(argv=None):
    
    args = parser.parse_args(argv)
    
    with redirect(args) as iohandles:
        
        if sum([args.list_of_stdin, args.lines_of_stdin, args.filter_result]) > 1:
            iohandles.err.write('Pythonpy accepts at most one of [-x, -l] flags\n')
            raise SystemExit(code=1)
        
        if args.json_input:
            
            def loads(str_):
                try:
                    return json.loads(str_.rstrip())
                except Exception as exc:
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
            
            if args.expression.startswith('?') or args.expression.endswith('?'):
                
                final_atom = current_list(args.expression.rstrip('?'))[-1]
                first_atom = current_list(args.expression.lstrip('?'))[0]
                
                if args.expression.startswith('??'):
                    args.expression = "inspect_source(%s)" % first_atom
                elif args.expression.endswith('??'):
                    args.expression = "inspect_source(%s)" % final_atom
                elif args.expression.startswith('?'):
                    args.expression = 'help(%s)' % first_atom
                else:
                    args.expression = 'help(%s)' % final_atom
                
                if args.lines_of_stdin:
                    stdin = islice(stdin, 1)
        
        if args.pre_cmd:
            args.pre_cmd = args.pre_cmd.replace("`", "'")
        
        if args.post_cmd:
            args.post_cmd = args.post_cmd.replace("`", "'")
        
        lazy_imports(args.expression, args.pre_cmd, args.post_cmd)
        
        if args.pre_cmd:
            exec(args.pre_cmd)
        
        def safe_eval(text, x):
            try:
                return eval(text)
            except:
                return None
        
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
            
            l = list(stdin)
            result = eval(args.expression)
        
        else:
            result = eval(args.expression)
        
        def format(output):
            if output is None:
                return None
            elif args.json_output:
                return json.dumps(output)
            elif args.output_delimiter:
                return args.output_delimiter.join(output)
            else:
                return output
        
        if isinstance(result, collections.abc.Iterable) and hasattr(result, '__iter__') and not isinstance(result, str):
            for x in result:
                formatted = format(x)
                if formatted is not None:
                    try:
                        print(formatted)
                    except UnicodeEncodeError:
                        print(formatted.encode('utf-8'))
        else:
            formatted = format(result)
            if formatted is not None:
                try:
                    print(formatted)
                except UnicodeEncodeError:
                    print(formatted.encode('utf-8'))
        
        if args.post_cmd:
            exec(args.post_cmd)
        
        out = iohandles.out.getvalue()
    
    return out

IOHandles = collections.namedtuple('IOHandles', ('out', 'err'))

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
        
        except SystemExit as exit:
            raise TypeError("[ERROR] in cluval execution") from exit
        
        except Exception as exc:
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
            
            # sys.exit(1)
            raise SystemExit(code=1)
