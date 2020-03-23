#!/usr/bin/env python2
from __future__ import (unicode_literals, absolute_import,
                        print_function, division)
import sys
import re
from collections import defaultdict

import rlcompleter


def current_raw(input):
    if len(input[-1]) > 0 and input[-1][0] in '"\'':
        return input[-1][1:] 
    return input[-1]


def current_list(input):
    return re.split(r'[^a-zA-Z0-9_\.]', current_raw(input))


def current_prefix(input):
    return current_list(input)[-1]


def prior(input):
    return input[:-1]


def lazy_imports(*args):
    query = ' '.join([x for x in args if x])
    regex = re.compile("([a-zA-Z_][a-zA-Z0-9_]*)\.?")
    matches = regex.findall(query)
    for raw_module_name in matches:
        if re.match('np(\..*)?$', raw_module_name):
            module_name = re.sub('^np', 'numpy', raw_module_name)
        elif re.match('pd(\..*)?$', raw_module_name):
            module_name = re.sub('^pd', 'pandas', raw_module_name)
        else:
            module_name = raw_module_name
        try:
            module = __import__(module_name)
            globals()[raw_module_name] = module
        except ImportError as e:
            pass


def complete_all(prefix, completion_args):
    lazy_imports(prefix, completion_args['c_arg'])
    if completion_args:
        if completion_args['x_arg']:
            x = str()
        if completion_args['l_arg']:
            l = list()
        if completion_args['c_arg']:
            exec(completion_args['c_arg'].strip('"\'').replace("`", "'"))
    context = locals()
    context.update(globals())
    completer = rlcompleter.Completer(context)
    idx = 0
    options_set = set()
    while completer.complete(prefix, idx):
        options_set.add(completer.complete(prefix, idx))
        idx += 1

    module_completion, module_list = get_completerlib()
    try:
        options = module_completion("import " + prefix) or []
    except: #module_completion may throw exception (e.g. on 'import sqlalchemy_utils.')
        options = []
    if options:
        options = [x.rstrip(' ') for x in options if x.startswith(prefix)]

    return options + list(options_set)


def parse_string(input):
    if current_raw(input).startswith('--'):
        return ['--si', '--so', '--ji', '--jo', '--i']
    elif current_raw(input).startswith('-'):
        return ['-h', '-x', '-fx', '-l', '-c', '-C']
    elif len(prior(input)) > 0 and prior(input)[-1] == '-c':
        if 'import'.startswith(current_raw(input)):
            options = ["'import"]
        elif current_raw(input).startswith('import ') or current_raw(input).startswith('from '):
            module_completion, module_list = get_completerlib()
            options = module_completion(current_raw(input)) or []
            if options:
                options = [x.rstrip(' ') for x in options if x.startswith(current_prefix(input))]
        else:
            options = complete_all(current_prefix(input), defaultdict(lambda: None))
            if current_prefix(input).endswith('.'):
                options = [x for x in options if '._' not in x]
        return options
    elif current_raw(input) == '':
        options = ['sys', 'json', 're', 'csv', 'datetime', 'hashlib', 'itertools', 'math', 'os', 'random', 'shutil'] 
        if '-x' in input[:-1] or '-fx' in input[:-1]:
            options += 'x'
        if '-l' in input[:-1]:
            options += 'l'
        return options
    else:
        completion_args = defaultdict(lambda: None)
        if '-x' in prior(input) or '-fx' in prior(input):
            completion_args['x_arg'] = True
        if '-l' in prior(input):
            completion_args['l_arg'] = True
        if '-c' in prior(input):
            c_index = prior(input).index('-c')
            if (c_index + 1) < len(prior(input)):
                completion_args['c_arg'] = prior(input)[c_index + 1]
        options = complete_all(current_prefix(input), completion_args)
        if current_prefix(input).endswith('.'):
            options = [x for x in options if '._' not in x]
        return options


def get_completerlib():
    """Implementations for various useful completers.

    These are all loaded by default by IPython.
    """
    #-----------------------------------------------------------------------------
    #  Copyright (C) 2010-2011 The IPython Development Team.
    #
    #  Distributed under the terms of the BSD License.
    #
    #  The full license is in the file COPYING.txt, distributed with this software.
    #-----------------------------------------------------------------------------

    #-----------------------------------------------------------------------------
    # Imports
    #-----------------------------------------------------------------------------
    #from __future__ import print_function

    import inspect
    import os
    #import re
    #import sys

    try:
        # Python >= 3.3
        from importlib.machinery import all_suffixes
        _suffixes = all_suffixes()
    except ImportError:
        from imp import get_suffixes
        _suffixes = [ s[0] for s in get_suffixes() ]

    # Third-party imports
    from time import time
    from zipimport import zipimporter

    TIMEOUT_STORAGE = 2

    TIMEOUT_GIVEUP = 20

    # Regular expression for the python import statement
    import_re = re.compile(r'(?P<name>[a-zA-Z_][a-zA-Z0-9_]*?)'
                           r'(?P<package>[/\\]__init__)?'
                           r'(?P<suffix>%s)$' %
                           r'|'.join(re.escape(s) for s in _suffixes))

    # RE for the ipython %run command (python + ipython scripts)
    magic_run_re = re.compile(r'.*(\.ipy|\.ipynb|\.py[w]?)$')

    def module_list(path):
        """
        Return the list containing the names of the modules available in the given
        folder.
        """
        # sys.path has the cwd as an empty string, but isdir/listdir need it as '.'
        if path == '':
            path = '.'

        # A few local constants to be used in loops below
        pjoin = os.path.join

        if os.path.isdir(path):
            # Build a list of all files in the directory and all files
            # in its subdirectories. For performance reasons, do not
            # recurse more than one level into subdirectories.
            files = []
            for root, dirs, nondirs in os.walk(path):
                subdir = root[len(path)+1:]
                if subdir:
                    files.extend(pjoin(subdir, f) for f in nondirs)
                    dirs[:] = [] # Do not recurse into additional subdirectories.
                else:
                    files.extend(nondirs)

        else:
            try:
                files = list(zipimporter(path)._files.keys())
            except:
                files = []

        # Build a list of modules which match the import_re regex.
        modules = []
        for f in files:
            m = import_re.match(f)
            if m:
                modules.append(m.group('name'))
        return list(set(modules))


    def get_root_modules():
        """
        Returns a list containing the names of all the modules available in the
        folders of the pythonpath.

        ip.db['rootmodules_cache'] maps sys.path entries to list of modules.
        """
        #ip = get_ipython()
        #rootmodules_cache = ip.db.get('rootmodules_cache', {})
        rootmodules_cache = {}
        rootmodules = list(sys.builtin_module_names)
        start_time = time()
        #store = False
        for path in sys.path:
            try:
                modules = rootmodules_cache[path]
            except KeyError:
                modules = module_list(path)
                try:
                    modules.remove('__init__')
                except ValueError:
                    pass
                if path not in ('', '.'): # cwd modules should not be cached
                    rootmodules_cache[path] = modules
                if time() - start_time > TIMEOUT_STORAGE and not store:
                    #store = True
                    #print("\nCaching the list of root modules, please wait!")
                    #print("(This will only be done once - type '%rehashx' to "
                          #"reset cache!)\n")
                    sys.stdout.flush()
                if time() - start_time > TIMEOUT_GIVEUP:
                    print("This is taking too long, we give up.\n")
                    return []
            rootmodules.extend(modules)
        #if store:
            #ip.db['rootmodules_cache'] = rootmodules_cache
        rootmodules = list(set(rootmodules))
        return rootmodules


    def is_importable(module, attr, only_modules):
        if only_modules:
            return inspect.ismodule(getattr(module, attr))
        else:
            return not(attr[:2] == '__' and attr[-2:] == '__')


    def try_import(mod, only_modules=False):
        try:
            m = __import__(mod)
        except:
            return []
        mods = mod.split('.')
        for module in mods[1:]:
            m = getattr(m, module)

        m_is_init = hasattr(m, '__file__') and '__init__' in m.__file__

        completions = []
        if (not hasattr(m, '__file__')) or (not only_modules) or m_is_init:
            completions.extend( [attr for attr in dir(m) if
                                 is_importable(m, attr, only_modules)])

        completions.extend(getattr(m, '__all__', []))
        if m_is_init:
            completions.extend(module_list(os.path.dirname(m.__file__)))
        completions = set(completions)
        if '__init__' in completions:
            completions.remove('__init__')
        return list(completions)


    def module_completion(line):
        """
        Returns a list containing the completion possibilities for an import line.

        The line looks like this :
        'import xml.d'
        'from xml.dom import'
        """

        words = line.split(' ')
        nwords = len(words)

        # from whatever <tab> -> 'import '
        if nwords == 3 and words[0] == 'from':
            return ['import ']

        # 'from xy<tab>' or 'import xy<tab>'
        if nwords < 3 and (words[0] in ['import','from']) :
            if nwords == 1:
                return get_root_modules()
            mod = words[1].split('.')
            if len(mod) < 2:
                return get_root_modules()
            completion_list = try_import('.'.join(mod[:-1]), True)
            return ['.'.join(mod[:-1] + [el]) for el in completion_list]

        # 'from xyz import abc<tab>'
        if nwords >= 3 and words[0] == 'from':
            mod = words[1]
            return try_import(mod)

    return module_completion, module_list


def remove_trailing_paren(str_):
    if str_.endswith('('):
        return str_[:-1]
    return str_


def main():
    input = sys.argv[1:]
    if len(input) == 0:
        return
    elif '<' in input or '>' in input:
        print('_longopt')
        return
    else:
        options = list(set(map(remove_trailing_paren, parse_string(input))))

        if len(options) == 0:
            return

        if len(current_list(input)) > 1 and max(map(len, options)) + 1 >= len(current_raw(input)):
            options.append(current_prefix(input))

        if len(options) <= 1:
            options = options + [x + "'" for x in options]
        print(' '.join(options))


if __name__ == '__main__':
    main()
