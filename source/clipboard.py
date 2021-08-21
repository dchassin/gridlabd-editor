#
# Clipboard
#

class Clipboard:

    source_value = None
    source_type = None

    def __init__(self,main):
        self.main = main

    def copy(self,type,value,append=False):
        source_type = type
        source_value = value
        if not append:
            self.main.clipboard_clear()
        self.main.clipboard_append(json.dumps(value))

    def paste(self,type='*'):
        if type == '*' or type == source_type:
            return source_value
        else:
            return None

    def get_type(self):
        return source_type

    def get_value(self):
        return source_value

    def is_type(self,type):
        return type == source_type
