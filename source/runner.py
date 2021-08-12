"""Runner"""
import os, sys
import subprocess as sp
from concurrent.futures import ThreadPoolExecutor

class Runner:

    def __init__(self,command,timeout=None,output=sys.stdout,error=sys.stderr):

        def log_output(proc):

            while proc.poll() is None:
                print("[stdout] ",proc.stdout.read(),flush=True,file=sys.stderr)

        def log_error(proc):

            while proc.poll() is None:
                print("[strerr] ",proc.stderr.read(),flush=True,file=sys.stderr)

        proc = sp.Popen(command.split(), stdout=sp.PIPE, stderr=sp.PIPE, text=True)
        with ThreadPoolExecutor(2) as pool:
            print("COMMAND:",command,flush=True,file=sys.stderr)
            p1 = pool.submit(log_output, proc)
            p2 = pool.submit(log_error, proc)
            p1.result()
            p2.result()
        proc.communicate(input=None,timeout=timeout)
        pool.shutdown(wait=True,cancel_futures=True)

import unittest

class PreferencesTest(unittest.TestCase):

    def test_1_version(self):
        runner = Runner("gridlabd --version")

    def test_2_validate(self):
        runner = Runner("gridlabd -W ../../../slacgismo/gridlabd/module/assert -D keep_progress=TRUE --validate")

if __name__ == '__main__':
    unittest.main()
