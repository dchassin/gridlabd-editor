"""GridLAB-D Runner"""
import os, sys, json
import subprocess as sp
from concurrent.futures import ThreadPoolExecutor

class Runner:
    """GridLAB-D Runner Class

    Example 1 - Successful run

        >>> runner = Runner('echo hello')
        >>> runner.get_output()
        'hello'

    Example 2 - Non-zero return code
    
        >>> runner = Runner('false')
        >>> runner.Runner('echo hello').get_returncode()
        1

    Example 3 - Command not found

        >>> runner.Runner('bad').get_exception()
        (<class 'FileNotFoundError'>, FileNotFoundError(2, 'No such file or directory'), <traceback object at 0x105cfbf40>)

    Example 4 - Capture text output

        >>> runner.Runner('curl -I https://google.com/',output_call=print)
        HTTP/2 301
        location: https://www.google.com/
        content-type: text/html; charset=UTF-8
        date: Fri, 13 Aug 2021 19:56:02 GMT
        expires: Sun, 12 Sep 2021 19:56:02 GMT
        cache-control: public, max-age=2592000
        server: gws
        content-length: 220
        x-xss-protection: 0
        x-frame-options: SAMEORIGIN
        alt-svc: h3=":443"; ma=2592000,h3-29=":443"; ma=2592000,h3-T051=":443"; ma=2592000,h3-Q050=":443"; ma=2592000,h3-Q046=":443"; ma=2592000,h3-Q043=":443"; ma=2592000,quic=":443"; ma=2592000; v="46,43"
        <runner.Runner object at 0x1093a06d0>

    Example 5 - Capture JSON output

        >>> runner.Runner("gridlabd --version=json",output_format='json').get_output()["application"]
        'gridlabd'

    """
    def __init__(self,command,
            output_call = None,
            error_call = None,
            output_format = 'text',
            timeout = None,
            exceptions = []):
        """
        command (str or list)   Command and optional arguments

        output_call (callable)  Output callback function output_call(str)

        error_call (callable)   Error callback function error_call(str)

        output_format (str)     Valid formats are 'text' and 'json'

        timeout (int)           Communications wait timeout in seconds

        exceptions (list)       List of exceptions that are raised if caught
        """
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
        try:
            self.proc = sp.Popen(self.command, stdout=sp.PIPE, stderr=sp.PIPE, text=True, encoding='utf-8')
            with ThreadPoolExecutor(2) as self.pool:
                p1 = self.pool.submit(log_output, self)
                p2 = self.pool.submit(log_error, self)
                p1.result()
                p2.result()

            self.proc.communicate(input=None,timeout=timeout)
            if self.output_hold and self.output_call:
                self.output_call(self.output_format("\n".join(self.output_data)))

            self.pool.shutdown(wait=True,cancel_futures=True)
            self.returncode = self.proc.returncode
            self.exception = None
        except Exception as err:
            self.returncode = None
            self.exception = sys.exc_info()
            if any(map(lambda c: issubclass(self.exception[0],c),exceptions)):
                raise err

    def get_output(self,join=None,split=None):
        """Get output

            join (None or str)   Specifies whether and how to join output lists 

            split (None or str)  Specifies whether and how to join output strings

        The output is collected and delivered in the format requested at __init__.
        """
        if type(self.output_data) is list:
            if join:
                return join.join(self.output_data).strip()
            else:
                return self.output_format("\n".join(self.output_data))
        elif type(self.output_data) is str:
            if split:
                return self.output_format(self,output_data).split(split)
            else:
                return self.output_format(self.output_data)
        else:
            raise RuntimeError("output data type '{type(self.output_data)}' is not valid")

    def get_errors(self,join=None):
        """Get errors

            join (None or str)   Specifies whether and how to join error lists 

        The errors collected and delivered in the format requested at __init__.
        """
        if join and type(self.error_data) is list:
            return join.join(self.error_data).strip()
        else:
            return self.error_data

    def get_exception(self,join=None):
        """Get exception information

            join (None or str)   Specified whether and how to join exception information
        """
        if join and self.exception:
            import traceback
            return join.join(traceback.TracebackException(*self.exception).format())
        else:
            return self.exception

    def get_returncode(self):
        """Get return code"""
        return self.returncode

import unittest

class __RunnerTest(unittest.TestCase):

    def output(self,*args):
        self.output_data = args[0]

    def error(self,*args):
        self.error_data = args[0]

    def test_1_version(self):
        import gridlabd
        title = gridlabd.__title__
        command = "gridlabd --version=package"
        runner = Runner(command)
        self.assertEqual(runner.get_output('\n'),title)
        self.assertEqual(runner.get_errors(),[])

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
        data = runner.get_output(join=None)
        self.assertEqual(data["application"],"gridlabd")
        self.assertEqual(runner.get_errors(),[])

    def test_2_validate(self):
        command = "gridlabd -W ../../../slacgismo/gridlabd/module/assert -D keep_progress=TRUE --validate"
        runner = Runner(command,output_call=print,error_call=self.error)
        self.assertEqual(runner.get_errors(),[])

if __name__ == '__main__':
    unittest.main()
