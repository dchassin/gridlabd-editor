"""Runner"""
import os, sys
import subprocess as sp
from concurrent.futures import ThreadPoolExecutor

def do_nothing(*args):
    pass

class Runner:

    def __init__(self,command,output_call=do_nothing,error_call=do_nothing):

        def log_output(self):

            while self.proc.poll() is None:
                self.output_call(self.proc.stdout.read())

        def log_error(self):

            while self.proc.poll() is None:
                self.error_call(self.proc.stderr.read())

        self.output_call = output_call
        self.error_call = error_call
        self.done = False
        if type(command) is str:
            self.command = command.split()
        else:
            self.command = command
        self.proc = sp.Popen(self.command, stdout=sp.PIPE, stderr=sp.PIPE, text=True)
        with ThreadPoolExecutor(2) as self.pool:
            p1 = self.pool.submit(log_output, self)
            p2 = self.pool.submit(log_error, self)
            p1.result()
            p2.result()

    def communicate(self,timeout=None):
        self.proc.communicate(input=None,timeout=timeout)
        self.done = True

    def wait(self,timeout=None):
        pool.shutdown(wait=True,cancel_futures=True)

import unittest

class PreferencesTest(unittest.TestCase):

    def output(self,*args):
        print("OUTPUT:",*args,file=sys.stdout)

    def error(self,*args):
        print("ERROR:",*args,file=sys.stderr)

    def test_1_version(self):
        command = "gridlabd --version=json"
        print("COMMAND:",command,flush=True,file=sys.stderr)
        runner = Runner(command,output_call=self.output,error_call=self.error)
        runner.communicate()
        runner.wait()

    def test_2_validate(self):
        command = "gridlabd -W ../../../slacgismo/gridlabd/module/assert -D keep_progress=TRUE --validate"
        print("COMMAND:",command,flush=True,file=sys.stderr)
        runner = Runner(command,output_call=self.output,error_call=self.error)
        runner.communicate()
        runner.wait()

if __name__ == '__main__':
    unittest.main()
