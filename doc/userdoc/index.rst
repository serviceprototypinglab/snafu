.. Snafu documentation master file, created by
   sphinx-quickstart on Sat Apr 22 19:36:35 2017.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.

Snafu User Documentation
========================

Contents:

.. toctree::
   :maxdepth: 2

Purpose
-------

Snafu aims to be the Swiss Army Knife of Serverless Computing due to its design principles.
It should be easy to get going and use, full of features for both client-side and server-side
Function-as-a-Service tasks, robust, flexible and most useful in combination with other tools
and services.

Tutorial
--------

In case you haven't installed Snafu yet, you can do so directly from the Git sources, from the
Python Package Index, or from the Docker Hub. Run one of the following commands on your command
line (obviously without the leading $ sign). Note that Snafu runs perfectly fine from the Git
repository without installation but all commands in this tutorial will need a preceeding dotslash
(i.e. ./snafu instead of snafu).

.. code::

   $ git clone https://github.com/serviceprototypinglab/snafu.git
   $ easy_install -Z snafu
   $ docker run -ti jszhaw/snafu

Afterwards, try out Snafu on a source file containing a simple hello world function. Create one in
Python as follows.

.. code::

   $ cat > /tmp/test.py << END
     > def helloworld():return 'Hello World'
     > END

And then, run Snafu on this file. It will automatically extract the function names and parameters
from the file. There is only one function and therefore it is made available with the name test.helloworld
which results from the name of the file and the name of the function.
Furthermore, Snafu informs about its default configuration: All function invocations are logged
into a CSV file (by default, snafu.csv in the execution directory). All functions are executed
internally which requires them to be Python 3 functions. And the invocations are controlled by the
interactive command-line interface (CLI) which asks for the function name and, in case there were
any, the function parameters. The function result is printed after the timing information. Subsequently,
the next function is asked for, at which point you can cancel the tool as a single hello world function
is not terribly interesting after all.

.. code::

   $ snafu /tmp/test.py
   » module: /tmp/test.py
     function: test.helloworld
   + logger: csv
   + executor: inmemory
   + connector: cli
   Function name:test.helloworld
   [1492884560.138][139976878737152][function:test.helloworld]
   [1492884560.138][139976878737152][result:Hello World]
   [1492884560.138][139976878737152][time:0.002ms]
   [1492884560.138][139976878737152][overalltime:0.008ms]
   Hello World
   Function name:^C

The following invocation syntax is useful for batch processing. Snafu is instructed to execute one specific
function directly (-x) and to omit all unnecessary output in quiet mode (-q).

.. code::

   $ snafu -q -x test.helloworld /tmp/test.py

Now suppose you've got a number of functions stored at a major commercial cloud provider, such as IBM Bluemix
OpenWhisk, Google Cloud Functions, or AWS Lambda. You can fill up your Snafu by importing the functions as follows.
Note that the access to the provider needs to be configured beforehand, i.e. the respective command-line tools
need to be working (test with either of these: aws lamdba list-functions, wsk list, gcloud beta functions list).
In the example, functions are imported from Lambda which only supports Python 2, and are therefore (heuristically)
upgraded to Python 3.

.. code::

   $ snafu-import --source lambda --convert

That went well, did it? The next step is then hosting these functions.

.. code::

   $ snafu-control

Now, you can redirect your command-line tools to Snafu and call all functions locally without incurring provider charges.
Note that the Google Cloud CLI does not allow for such redirection and needs to be patched instead (see tools/patch-gcloud
in the Git repository).

.. code::

   $ alias aws="aws --endpoint-url http://localhost:10000 --cli-read-timeout 0"
   $ alias wsk="wsk --apihost http://localhost:10000"

Developer Information
---------------------

Snafu consists not only of the presented CLI scripts, but primarily of Python modules within the Snafu package.
Each module must be imported separately. For instance, to access the core Snafu functionality, run the following
command:

.. code::

   >>> import snafulib.snafu
   >>> dir(snafulib.snafu)
   ['Snafu', 'SnafuContext', 'SnafuFunctionSource', 'SnafuImport', 'SnafuRunner', '__builtins__', ...]

The most common use case is to instantiate a Snafu object and call its activate method which requires a list of
files or directories to scan for functions and a calling convention ("any").

Indices and tables
==================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`

