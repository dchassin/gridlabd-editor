from runner import Runner

def gridlabd(*args,format="text"):
    command = ["gridlabd"]
    command.extend(args)
    return Runner(command,output_format=format)

module_list = []
def modules():
    if not module_list:
        result = gridlabd("--modlist").get_output().splitlines()
        for modinfo in result[2:]:
            name = modinfo.partition(' ')[0]
            module_list.append(name)
    return module_list

class_list = {}
def classes(module):
    if not module in class_list.keys():
        result = gridlabd("--modhelp=json",module,format="json")
        class_list[module] = result.get_output()["classes"]
    return class_list[module]

import unittest

class __UtilitiesTest(unittest.TestCase):

    def output(self,*args):
        self.output_data = args[0]

    def error(self,*args):
        self.error_data = args[0]

    def test_1_version(self):
        from gridlabd import title
        result = gridlabd("--version=package")
        self.assertEqual(result.get_output('\n'),title())
        self.assertEqual(result.get_errors(),[])

    def test_2_modules(self):
        self.assertTrue("assert" in modules())

    def test_3_classes(self):
        self.assertTrue("assert" in classes("assert"))

if __name__ == '__main__':
    unittest.main()

