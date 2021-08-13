"""Runner"""
import os, sys, json
import subprocess as sp
from concurrent.futures import ThreadPoolExecutor

class Runner:

    def __init__(self,command,output_call=None,error_call=None,output_format='text',timeout=None):

        try:
            self.output_format = dict(text=str,json=json.loads)[output_format]
            self.output_hold = dict(text=False,json=True)[output_format]
        except:
            raise ParameterError(f"output_format '{output_format}' is not valid")

        if output_call and not self.output_hold:
            def log_output(self):
                while self.proc.poll() is None:
                    text = self.proc.stdout.readline().strip()
                    if text:
                        self.output_call(text)
                text = self.proc.stderr.read().strip()
                if text:
                    self.output_call(text)
        else:
            def log_output(self):
                while self.proc.poll() is None:
                    text = self.proc.stdout.readline().strip()
                    if text:
                        self.output_data.append(text)
                text = self.proc.stdout.read().strip()
                if text:
                    self.output_data.append(text)
        self.output_data = []
        self.output_call = output_call

        if error_call:
            def log_error(self):
                while self.proc.poll() is None:
                    text = self.proc.stderr.readline().strip()
                    if text:
                        self.error_call(text)
                text = self.proc.stderr.read().strip()
                if text:
                    self.error_call(text)
        else:
            def log_error(self):
                while self.proc.poll() is None:
                    text = self.proc.stderr.readline().strip()
                    if text:
                        self.error_data.append(text)
                text = self.proc.stderr.read().strip()
                if text:
                    self.error_data.append(text)
        self.error_data = []
        self.error_call = error_call

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

        self.proc.communicate(input=None,timeout=timeout)
        if self.output_hold and self.output_call:
            self.output_call(self.output_format("\n".join(self.output_data)))

        self.pool.shutdown(wait=True,cancel_futures=True)

    def get_output(self,join=None):
        if type(self.output_data) is list:
            if join:
                return join.join(self.output_data).strip()
            else:
                return self.output_format("\n".join(self.output_data))
        else:
            return self.output_format(self.output_data)

    def get_errors(self,join=None):
        if join and type(self.error_data) is list:
            return join.join(self.error_data).strip()
        else:
            return self.error_data

import unittest

class PreferencesTest(unittest.TestCase):

    def output(self,*args):
        self.output_data = args[0]

    def error(self,*args):
        self.error_data = args[0]

    def test_1_version(self):
        import gridlabd
        title = gridlabd.__title__
        command = "gridlabd --version=package"
        runner = Runner(command)
        self.assertEqual(runner.get_output(join='\n'),title)
        self.assertEqual(runner.get_errors(join='\n'),'')

    def test_1_version_text(self):
        import gridlabd
        title = gridlabd.__title__
        command = "gridlabd --version=package"
        self.output_data = None
        self.error_data = None
        runner = Runner(command,output_call=self.output,error_call=self.error,output_format='text')
        self.assertEqual(self.output_data,title)
        self.assertEqual(self.error_data,None)

    def test_1_version_json(self):
        command = "gridlabd --version=json"
        runner = Runner(command,output_format='json')
        data = runner.get_output()
        self.assertEqual(data["application"],"gridlabd")
        self.assertEqual(runner.get_errors(),[])

    def test_2_validate(self):
        command = "gridlabd -W ../../../slacgismo/gridlabd/module/assert -D keep_progress=TRUE --validate"
        runner = Runner(command,output_call=print,error_call=self.error)
        self.assertEqual(runner.get_errors(),[])

if __name__ == '__main__':
    unittest.main()
