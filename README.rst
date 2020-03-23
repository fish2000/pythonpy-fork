Installation
------------

::

  pip install pythonpy-fork

::

Run Tests
------------

::

  python -m pytest

::

Usage
-----------------------------------------------

Pythonpy will evaluate any python expression from the command line.

Float Arithmetic
~~~~~~~~~~~~~~~~

::

  $ py '3 * 1.5' 
  4.5

::

Import any module automatically
~~~~~~~~~~~~~~~~~~~~~~~~~~~~

::

  $ py 'math.exp(1)'
  2.71828182846

  $ py 'random.random()'
  0.103173957713
  
  $ py 'datetime.datetime.now?'
  Help on built-in function now:

  now(...)
        [tz] -> new datetime with tz's local day and time.


::

py -x 'foo(x)' will apply foo to each line of input
---------------------------------------------------

Multiply each line of input by 7
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

::

  $ py 'range(3)' | py -x 'int(x)*7'
  0
  7
  14

::

Grab the second column of a csv
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

::

  $ echo $'a1,b1,c1\na2,b2,c2' | py -x 'x.split(",")[1]'
  b1
  b2

::

Append ".txt" to every file in the directory
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

::

  $ ls | py -x '"mv `%s` `%s.txt`" % (x,x)' | sh 
  # sharp quotes are swapped out for single quotes
  # single quotes handle spaces in filenames

::

Remove every file returned by the find command
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

::

  $ find . -type f | py -x '"rm %s" % x' | sh 

::

Get only 2 digit numbers
~~~~~~~~~~~~~~~~~~~~~

::

  $ py 'range(14)' | py -x 'x if len(x) == 2 else None'
  10
  11
  12
  13

::

py -l will set l = list(sys.stdin)
-------------------------------------------

Lists are printed row by row
~~~~~~~~~~~~~~~~~~~~~~~~~~~~

::

  $ py 'range(3)'
  0
  1
  2

  $ py '[range(3)]'
  [0, 1, 2]

::

Reverse the input
~~~~~~~~~~~~~~~~~

::

  $ py 'range(3)' | py -l 'l[::-1]'
  2
  1
  0

::

Sum the input
~~~~~~~~~~~~~

::

  $ py 'range(3)' | py -l 'sum(int(x) for x in l)'
  3

::

Sort a csv by the second column
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

::

  $ echo $'a,2\nb,1' | py -l 'sorted(l, key=lambda x: x.split(",")[1])'
  b,1
  a,2

::

Count words beginning with each letter
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

::

  $ cat /usr/share/dict/words | py -x 'x[0].lower()' | py -l 'collections.Counter(l).most_common(5)'
  ('s', 11327)
  ('c', 9521)
  ('p', 7659)
  ('b', 6068)
  ('m', 5922)

::

For more examples, check out the `wiki <http://github.com/fish2000/pythonpy-fork/wiki>`__.

Pythonpy also supports `ipython`-style tab completion, which you can enable as follows:

::

  $ if command -v find_pycompletion.sh>/dev/null; then source `find_pycompletion.sh`; fi

::
