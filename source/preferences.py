"""Preferences"""

import os, json

source_path = os.path.split(__file__)[0]
config_path = os.path.expanduser("~/.gridlabd-editor")

default_filename = f"{config_path}/preferences.conf"
default_preferences = {
    "Welcome dialog enabled" : {
        "value" : True,
        "type" : bool,
        "description" : "Show welcome dialog",
        },
    "Save output filename" : {
        "value" : "output.txt",
        "type" : str,
        "description" : "File name to save output on exit",
        },
    "Save output" : {
        "value" : True,
        "type" : bool,
        "description" : "Enable saving output on exit",
        },
    "Reopen last file" : {
        "value" : True,
        "type" : bool,
        "description" : "Enable reopening last file on initial open",
        },
    "Unused classes display enabled" : {
        "value" : False,
        "type" : bool,
        "description" : "Enable display of unused classes in elements list",
        },
    "Class display enabled" : {
        "value" : True,
        "type" : bool,
        "description" : "Enable display of classes in elements list",
        },
    "Traceback enabled" : {
        "value" : True,
        "type" : bool,
        "description" : "Enable output of exception traceback data",
        },
    "GridLAB-D executable" : {
        "value" : "/usr/local/bin/gridlabd",
        "type" : str,
        "description" : "GridLAB-D executable",
        }
    }

class Preferences:

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
                self.preferences = json.load(f)
                self.filename = filename
        else:
            self.preferences = default_preferences
            self.filename = default_filename

    def save(self,filename=None):
        """Save preferences

        PARAMETERS:

            filename (str or None)   preference filename, None to user current filename

        RETURNS:

            None
        """
        if not filename:
            filename = self.filename
        if filename:
            with open(filename,"w") as f:
                json.dump(self.preferences,f,indent=4)

    def keys(self):
        return self.preferences.keys()

    def get(self,key):
        if not key in self.preferences.keys():
            raise KeyError(f"key '{key}' not a valid preference")
        return self.preferences[key]['value']

    def set(self,key,value):
        if not key in self.preferences.keys():
            raise KeyError(f"preference key '{key}' is not valid")
        elif type(value) != self.preferences[key]['type']:
            raise TypeError(f"preference type '{type(value)}' is not valid")
        last = self.preferences[key]['value']
        self.preferences[key]['value'] = value
        return last

    def dialog(self):
        raise NotImplementedError(f"preferences dialog is not implemented yet")

import unittest

class PreferencesTest(unittest.TestCase):

    def test_init(self):
        self.assertEqual(Preferences(filename=None).keys(),default_preferences.keys())

    def test_save(self):
        pref = Preferences(filename=None)
        pref.save("test.conf")

if __name__ == '__main__':
    unittest.main()