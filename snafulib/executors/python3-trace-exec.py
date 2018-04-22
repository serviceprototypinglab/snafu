# Snafu: Snake Functions - Python3 Executor (Exec Module)

import sys
import os
import time
import json
import base64
import pickle
import psutil
import datetime
import uuid


class Context:
    def __init__(self):
        self.SnafuContext = self


    # def __new__(self):
    #	self.SnafuContext = self
    #	return self
frame_time_dict = {'frame': time.time()}
open_connections_old = []
open_connections = []
open_files_old = []
open_files = []
saved_variables = {'last_line': 0, 'last_time': -1}
proc = psutil.Process(os.getpid())

time_now = datetime.datetime.fromtimestamp(time.time()).strftime('%y%m%d-%H%M')
short_uuid = uuid.uuid4().hex[0:8]
func_name = sys.argv[2]
file_to_print_to_name = "trace_log-" + func_name + \
    "-" + time_now + '-' + short_uuid + ".log"
file_to_print_to = open(file_to_print_to_name, 'w')

print("Printing trace to " + file_to_print_to_name, file=sys.stderr)


def trace(frame, event, arg):
    # Potential optimization: put caller_string and function_string into a
    # dictionary

    # getting what code was called
    line_no = frame.f_lineno
    funcname = frame.f_code.co_name
    filename = frame.f_code.co_filename
    function_string = str(filename) + '.' + str(funcname)

    # monitor performance metrics
    interval = 10
    if saved_variables['last_time'] == -1:
        proc.cpu_percent()
        proc.memory_percent()
        saved_variables['last_time'] = time.time()
    if int(100 * (time.time() - saved_variables['last_time'])) > interval:
        print('performance -- CPU: ' +
              str(proc.cpu_percent()) +
              '% - Memory: ' +
              str(proc.memory_percent()) +
              '%', file=file_to_print_to)
        saved_variables['last_time'] = time.time()
    # monitor network connections
    open_conections = proc.connections()
    # check for newly closed connections
    for connection in open_connections_old:
        if connection not in open_conections:
            protocol = 'udp' if connection.status == psutil.CONN_NONE else 'tcp'
            print('Connection CLOSED by ' + function_string + ': ' + protocol +
                  ' connection from ' + connection.laddr.ip + ':' + str(connection.laddr.port) +
                  ' to ' + connection.raddr.ip + ':' + str(connection.laddr.port), file=file_to_print_to)
            open_connections_old.remove(connection)
    # check for newly opened connections
    for connection in open_conections:
        if connection not in open_connections_old:
            protocol = 'udp' if connection.status == psutil.CONN_NONE else 'tcp'
            print('Connection OPENED by ' + function_string + ': ' + protocol +
                  ' connection from ' + connection.laddr.ip + ':' + str(connection.laddr.port) +
                  ' to ' + connection.raddr.ip + ':' + str(connection.laddr.port), file=file_to_print_to)
            open_connections_old.append(connection)

    open_files = proc.open_files()
    for open_file in open_files_old:
        if open_file not in open_files:
            acces_type = open_file.mode
            print(
                'File CLOSED by ' +
                function_string +
                ' - Path: ' +
                open_file.path,
                file=file_to_print_to)  # TODO give more details about file
            open_files_old.remove(open_file)
    for open_file in open_files:
        if open_file not in open_files_old:
            acces_type = open_file.mode
            print(
                'File OPENED by ' +
                function_string +
                ' in mode \'' +
                acces_type +
                '\' - Path: ' +
                open_file.path,
                file=file_to_print_to)  # TODO give more details about file
            open_files_old.append(open_file)

    # getting who called the code
    has_caller = frame.f_back is not None
    caller_string = ''
    if has_caller:
        caller = frame.f_back
        caller_funcname = caller.f_code.co_name
        caller_filename = caller.f_code.co_filename
        caller_string = caller_filename + '.' + caller_funcname

    if event == 'call':
        # inserting start time for the frame
        frame_time_dict[frame] = time.time()
        print(
            'call from \t' +
            caller_string +
            ' to ' +
            function_string,
            file=file_to_print_to)
    if event == 'return':
        # taking out the time for frame
        time_elapsed_ms = round(
            (time.time() - frame_time_dict[frame]) * 1000, 6)
        print(
            'return from \t' +
            function_string +
            ' to ' +
            caller_string +
            ' - time elapsed: ' +
            str(time_elapsed_ms) +
            "ms",
            file=file_to_print_to)
    if event == 'exception':
        # TODO manually get traceback by calling the f_back objects and saving
        # last called line per frame
        print('exception in \t' + function_string + ' at line ' + \
              str(saved_variables['last_line']) + ': ' + str(arg), file=file_to_print_to)
    if event == 'line':
        saved_variables['last_line'] = frame.f_lineno
    # need to return tracefunc so that it still works after functioncalls
    return trace


def execute(filename, func, funcargs, envvars):
    funcargs = json.loads(funcargs)
    envvars = json.loads(envvars)

    for i, funcarg in enumerate(funcargs):
        if type(funcarg) == str and funcarg.startswith("pickle:"):
            sys.modules["lib"] = Context()
            sys.modules["lib.snafu"] = Context()
            #funcarg = pickle.loads(base64.b64decode(funcarg.split(":")[1]))
            # FIXME: SnafuContext as in python2-exec module
            funcarg = None

    sys.path.append(".")
    os.chdir(os.path.dirname(filename))
    mod = __import__(os.path.basename(filename[:-3]))
    func = getattr(mod, func)

    for envvar in envvars:
        os.environ[envvar] = envvars[envvar]

    stime = time.time()
    try:
        # activate tracing
        sys.settrace(trace)
        res = func(*funcargs)
        # deactivate tracing
        sys.settrace(None)
        success = True
    except Exception as e:
        res = e
        success = False
    dtime = (time.time() - stime) * 1000

    # return dtime, success, res
    return "{} {} {}".format(
        dtime,
        success,
        "{}".format(res).replace(
            "'",
            "\""))


print(execute(sys.argv[1], sys.argv[2], sys.argv[3], sys.argv[4]))
