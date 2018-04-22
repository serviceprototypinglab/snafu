import json
import subprocess
import pickle
import base64
import sys
import time


def strbool(x):
    return True if x == "True" else False


def trace(frame, event, arg):
    line_no = frame.f_lineno
    funcname = frame.f_code.co_name
    filename = frame.f_code.co_filename
    print(event + ' to ' + str(filename) + '.' + str(funcname))


def execute(func, funcargs, envvars, sourceinfos):
    for i, funcarg in enumerate(funcargs):
        if "__class__" in dir(
                funcarg) and funcarg.__class__.__name__ == "SnafuContext":
            funcargs[i] = "pickle:" + \
                base64.b64encode(pickle.dumps(funcarg)).decode("utf-8")

    funcargs = json.dumps(funcargs)
    envvars = json.dumps(envvars)

    p = subprocess.run(
        "python3 snafulib/executors/python3-trace-exec.py {} {} '{}' '{}' ".format(
            sourceinfos.source,
            func.__name__,
            funcargs,
            envvars),
        stdout=subprocess.PIPE,
        shell=True)

    try:
        dtime, success, *res = p.stdout.decode("utf-8").strip().split(" ")
    except BaseException:
        dtime = 0.0
        success = False
        res = []
    dtime = float(dtime)
    success = strbool(success)
    res = " ".join(res)
    return dtime, success, res
