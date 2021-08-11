"""Preferences"""

import os

source_path = os.path.split(__file__)[0]
config_path = os.path.expanduser("~/.gridlabd-editor")

default_filename = f"{config_path}/preferences.conf"
default_preferences = {
    "Welcome dialog enabled" : {
        "value" : False, # TODO: this should be True 
        "description" : "Show welcome dialog",
        },
    "Save output filename" : {
        "value" : "output.txt",
        "description" : "File name to save output on exit",
        },
    "Save output" : {
        "value" : True,
        "description" : "Enable saving output on exit",
        },
    "Reopen last file" : {
        "value" : True,
        "description" : "Enable reopening last file on initial open",
        },
    "Unused classes display enabled" : {
        "value" : False,
        "description" : "Enable display of unused classes in elements list",
        },
    "Class display enabled" : {
        "value" : True,
        "description" : "Enable display of classes in elements list",
        },
    "Traceback enabled" : {
        "value" : True,
        "description" : "Enable output of exception traceback data",
        },
    "GridLAB-D executable" : {
        "value" : "/usr/local/bin/gridlabd",
        "description" : "GridLAB-D executable",
        }
    }

class Preferences(dict):

    def __init__(self,filename=default_filename):
        """Create preferences object

        PARAMETERS:

        RETURNS:

            Preference object
        """
        self.load(None)
        if filename:
            try:
                self.load(filename)
            except FileNotFoundError:
                pass

    def load(self,filename):
        """Load preferences"

        PARAMETERS:

            filename (str or None)    preference filename, None resets to default

        RETURNS:

            None
        """
        if filename:
            with open(filename,"r") as f:
                self = json.load(f)
                self.filename = filename
        else:
            self = default_preferences
            self.filename = default_filename

    def save(self,filename=None):
        """Save preferences

        PARAMETERS:

            filename (str or None)   preference filename, None to user current filename

        RETURNS:

            None
        """

        raise NotImplementedError(f"Preferences.save(filename={filename}) is not implemented yet")

import unittest

class PreferencesTest(unittest.TestCase):

    def test_init(self):
        self.assertEqual(Preferences(filename=None).keys(),default_preferences.keys())

if __name__ == '__main__':
    print(Preferences(filename=None))
    unittest.main()