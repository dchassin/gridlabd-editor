"""GridLAB-D Editor Model

The model module manages GLM models for the GridLAB-D Editor.
"""

import os, sys, subprocess
import json
import tempfile

IID = "IID"
ITYPE = "ITYPE"
IPARENT = "IPARENT"
ATTRIBUTES = [ITYPE,IPARENT,IID]

class GleModelException(Exception):
    pass

class GleModelError(Exception):
    pass

class GleModelItem:
    """Abstract class for model items
    """
    def __init__(self,**kwargs):
        """Abstract contstructor for model item
        """
        self.data = {}
        self.set_data(kwargs)

    def get_data(self,key=None,strict=False):
        """Get model item data

        Arguments:
        - key       key of data item to get (None returns all data as dict)
        - strict    flag to enable GleModelError exception if key not found

        Returns:
        - str       data value if found, None if not found

        Exceptions:
        - GleModelError: key not found
        - GleModelException: key is not a string
        """
        if key == None:
            return self.data
        elif type(key) is str:
            if key in self.data:
                return self.data[key]
            elif not strict:
                return None
            else:
                raise GleModelError("key '{key}' not found")
        else:
            raise GleModelException("key '{key}' is not a string'")

    def set_data(self,data):
        """TODO
        """
        self.data.update(dict([(key,value) for key,value in data.items() if key not in ATTRIBUTES]))
        for key in ATTRIBUTES:
            if key in data:
                setattr(self,key,data[key])
            else:
                setattr(self,key,None)

    def zip(self,attr=False):
        if attr:
            return zip(ATTRIBUTES,[getattr(self,attr) for attr in ATTRIBUTES])
        else:
            return zip(self.data.keys(),self.data.values())

    def items(self,attr=False):
        return self.dict(attr=attr).items()

    def dict(self,key=None,attr=False):
        """TODO
        """
        if attr:
            if key == None:
                return dict(self.zip(True))
            else:
                return getattr(self,key)
        elif key == None:
            return self.data
        else:
            return {self.data["key"]: dict([(tag,value) for tag,value in self.data if tag != key])}

    def list(self,key=None,attr=False):
        """TODO
        """
        if attr:
            if key == None:
                return 
        return list(self.data.items())

    def json(self,key=None,attr=False):
        """TODO
        """
        return json.dumps(self.dict(key,attr))

    def glm(self):
        tag = json.dumps(dict(zip(ATTRIBUTES,[getattr(self,attr) for attr in ATTRIBUTES])))
        return f"""// {tag}\n""";

    def __getitem__(self,name):
        """TODO
        """
        return self.data[name] if name in self.data else None

    def __setitem__(self,name,value):
        """TODO
        """
        self.data[name] = value

class GleModelModule(GleModelItem):
    """TODO
    """
    def __init__(self,**kwargs):
        """TODO
        """
        kwargs[ITYPE] = "module"
        super().__init__(**kwargs)

    def glm(self):
        """TODO
        """
        result = [f"module {self.get_data('name')} {{"]
        result.extend([f"    {name} \"{value}\";" for name,value in self.items() if name != "name"])
        result.append("}")
        return super().glm() + "\n".join(result)

    @staticmethod
    def load(model,data):
        for module in data["modules"]:
            mod = GleModelModule(name=module)
            model.add_item(mod)
            for name,values in data["globals"].items():
                if name.startswith(f"{module}::"):
                    mod.set_data({name.split("::")[1]:values["value"]})

class GleModelClass(GleModelItem):
    """TODO
    """
    def __init__(self,**kwargs):
        """TODO
        """
        kwargs[ITYPE] = "class"
        super().__init__(**kwargs)

    def glm(self):
        """TODO
        """
        result = [f"class {self.get_data('name')} {{"]
        result.extend([f"    {name} \"{value}\";" for name,value in self.items() if name != "name"])
        result.append("}")
        return super().glm() + "\n".join(result)

class GleModelObject(GleModelItem):
    """TODO
    """
    def __init__(self,**kwargs):
        """TODO
        """
        kwargs[ITYPE] = "object"
        super().__init__(**kwargs)

    def glm(self):
        """TODO
        """
        result = [f"object {self.get_data('class')} {{"]
        result.extend([f"    {name} \"{value}\";" for name, value in self.items() if not name in ["class","id","rank"]])
        result.append("}")
        return super().glm() + "\n".join(result)

    @staticmethod
    def load(model,data):
        for name,spec in data["objects"].items():
            obj = GleModelObject(name=name,**spec)
            model.add_item(obj)

class GleModelClock(GleModelItem):
    """TODO
    """
    def __init__(self,**kwargs):
        """TODO
        """
        kwargs[ITYPE] = "clock"
        super().__init__(**kwargs)

class GleModelInput(GleModelItem):
    """TODO
    """
    def __init__(self,**kwargs):
        kwargs[ITYPE] = "input"
        super().__init__(**kwargs)

class GleModelGlobal(GleModelItem):
    """TODO
    """
    def __init__(self,**kwargs):
        """TODO
        """
        kwargs[ITYPE] = "global"
        super().__init__(**kwargs)

    def glm(self):
        """TODO
        """
        return super().glm() + f"#set {self.get_data('name')}={self.get_data('value')}"

    @staticmethod
    def load(model,data):
        for name,spec in data["globals"].items():
            if not "::" in name:
                var = GleModelGlobal(name=name,**spec)
                model.add_item(var)

class GleModelInclude(GleModelItem):
    """TODO
    """
    def __init__(self,**kwargs):
        """TODO
        """
        kwargs[ITYPE] = "include"
        super().__init__(**kwargs)

class GleModelOutput(GleModelItem):
    """TODO
    """
    def __init__(self,**kwargs):
        """TODO
        """
        kwargs[ITYPE] = "output"
        super().__init__(**kwargs)

class GleModelFilter(GleModelItem):
    """TODO
    """
    def __init__(self,**kwargs):
        """TODO
        """
        kwargs[ITYPE] = "filter"
        super().__init__(**kwargs)

class GleModelSchedule(GleModelItem):
    """TODO
    """
    def __init__(self,**kwargs):
        """TODO
        """
        kwargs[ITYPE] = "schedule"
        super().__init__(**kwargs)

class GleModelGroup(GleModelItem):
    """TODO
    """
    def __init__(self,**kwargs):
        """TODO
        """
        kwargs[ITYPE] = "group"
        super().__init__(**kwargs)

class GleModelTemplate(GleModelItem):
    """TODO
    """
    def __init__(self,**kwargs):
        """TODO
        """
        kwargs[ITYPE] = "template"
        super().__init__(**kwargs)

class GleModelCode(GleModelItem):
    """TODO
    """
    def __init__(self,**kwargs):
        """TODO
        """
        kwargs[ITYPE] = "code"
        super().__init__(**kwargs)

class GleModelSource(GleModelItem):
    """TODO
    """
    def __init__(self,**kwargs):
        super().__init__(**kwargs)

class GleModelComment(GleModelItem):
    """TODO
    """
    def __init__(self,**kwargs):
        """TODO
        """
        super().__init__(**kwargs)
        self.type = "comment"

class GleModel :
    """TODO
    """
    def __init__(self,*args,**kwargs):
        """TODO
        """
        self.data = []

    def add_item(self,item):
        """TODO
        """
        if not isinstance(item,GleModelItem):
            raise GleModelException("item is not a GleModelItem")
        self.data.append(item)

    def del_item(self,item):
        """TODO
        """
        TODO

    def load(self,filename):
        with open(filename,"r") as glm:
            if filename.endswith(".glm"):
                TODO("convert GLM to JSON")
            else:          
                data = json.load(glm)

            if "application" not in data or data["application"] != "gridlabd":
                raise GleModelException(f"{filename} does not contain a GridLAB-D model")
            
            # load items
            for itemtype in globals():
                itemcls = eval(itemtype)
                if itemtype not in ["GleModel","GleModelItem"] \
                        and itemtype.startswith("GleModel") \
                        and hasattr(itemcls,"load"):
                    itemcls.load(self,data)

    def glm(self):
        return "\n".join([item.glm() for item in self.data]) 

    def run(self,workdir=".",saveglm='onerror'):
        assert saveglm in ['never','always','onerror'], GldModelException(f"saveglm='{saveglm}' is invalid")
        with tempfile.NamedTemporaryFile(dir=workdir,suffix=".glm") as tmpname:
            glm = self.glm()
            tmpname.write(glm.encode('utf-8'))
            tmpname.flush()
            rc = subprocess.run(["gridlabd","-W",workdir,tmpname.name],capture_output=True)
            self.result = rc
            self.result.stdout = self.result.stdout.decode('utf-8')
            self.result.stderr = self.result.stderr.decode('utf-8')
            if saveglm == 'always' or ( rc.returncode != 0 and saveglm == 'error' ):
                self.result.glm = glm
            return rc
        return None
    
if __name__ == "__main__":

    import unittest

    class TestItemClass(GleModelItem):
        def __init__(self,**kwargs):
            """TODO
            """
            super().__init__(**kwargs)

    class testGleModelItem(unittest.TestCase):

        def test_class(self):
            # check class valid instance
            self.assertTrue(isinstance(TestItemClass(),GleModelItem))

        def test_class(self):
            # check class IID capture
            item = TestItemClass(name="test",IID="I123",value="456")
            self.assertEqual(item.IID,"I123")

    class testGleModel(unittest.TestCase):

        def test_add_item_ok(self):
            # check valid add_item()
            model = GleModel()
            class TestClass(GleModelItem):
                pass
            model.add_item(TestClass())

        def test_add_item_badtype(self):    
            # check invalid add_item()
            model = GleModel()
            try:
                model.add_item(1)
                raise AssertionError("GleModel failed to detect invalid item")
            except GleModelException:
                pass

    class testGleModelModule(unittest.TestCase):

        def test_init_ok(self):
            # check normal arglist constructor
            module = GleModelModule(name="test",value="123")
            self.assertEqual(module.ITYPE,"module")
            self.assertEqual(module.IPARENT,None)
            self.assertEqual(module.IID,None)
            self.assertEqual(module.get_data(),{'name': 'test', 'value': '123'})
            self.assertEqual(module.get_data("name"),"test")
            self.assertEqual(module.get_data("value"),"123")
            self.assertEqual(module["name"],"test")
            self.assertEqual(module["value"],"123")
            self.assertEqual(module.dict(),{'name': 'test', 'value': '123'})
            self.assertEqual(module.list(),[('name', 'test'), ('value', '123')])
            self.assertEqual(module.json(),'{"name": "test", "value": "123"}')
            self.assertEqual(module.glm(),
                '// {"ITYPE": "module", "IPARENT": null, "IID": null}\n' + 
                'module test {\n    value "123";\n}')

        def test_init_none(self):
            # check no-data arglist constructor
            module = GleModelModule(name="test")
            self.assertEqual(module.get_data("name"),"test")
            self.assertEqual(module["value"],None)

        def test_init_data(self):
            # check data block constructor
            data={"name":"test","value":"123"}
            module = GleModelModule(**data)
            self.assertEqual(module.get_data(),{'name': 'test', 'value': '123'})
            self.assertEqual(module.get_data("name"),"test")
            self.assertEqual(module.get_data("value"),"123")
            self.assertEqual(module["name"],"test")
            self.assertEqual(module["value"],"123")
            self.assertEqual(module.dict(),{'name': 'test', 'value': '123'})
            self.assertEqual(module.list(),[('name', 'test'), ('value', '123')])
            self.assertEqual(module.json(),'{"name": "test", "value": "123"}')
            self.assertEqual(module.glm(),
                '// {"ITYPE": "module", "IPARENT": null, "IID": null}\n' + 
                'module test {\n    value "123";\n}')

        def test_set_data(self):
            # check data set
            module = GleModelModule(name="test",value="123")
            module["value"] = "456"
            self.assertEqual(module["value"],"456")

        def test_set_iid(self):
            # check IID usage
            module = GleModelModule(name="test",value="123",IID="I012")
            self.assertEqual(module.IID,"I012")
            self.assertEqual(module.IPARENT,None)

        def test_set_iparent(self):
            # check iparent usage
            module = GleModelModule(name="test",value="123",IPARENT="I012")
            self.assertEqual(module.IID,None)
            self.assertEqual(module.IPARENT,"I012")

        def test_model_glm(self):
            # check glm syntax
            model = GleModel()
            model.add_item(GleModelModule(name="test1",value="123"))
            model.add_item(GleModelModule(name="test2",value="456"))
            self.assertEqual(model.glm(),
                '// {"ITYPE": "module", "IPARENT": null, "IID": null}\n' + 
                'module test1 {\n    value "123";\n}\n' + 
                '// {"ITYPE": "module", "IPARENT": null, "IID": null}\n' + 
                'module test2 {\n    value "456";\n}')

        def test_model_run(self):
            model = GleModel()
            model.load("unittest/valid_glm.json")
            result = model.run(saveglm='always')
            with open("unittest/test.glm","w") as fh:
                fh.write(result.glm)
            with open("unittest/test.out","w") as fh:
                fh.write(result.stdout)
            with open("unittest/test.err","w") as fh:
                fh.write(result.stderr)
            self.assertEqual(result.returncode,0)

        def test_model_load_bad(self):
            model = GleModel()
            try:
                model.load("unittest/invalid_glm.json")
                raise AssertionError("GleModel.load() failed to detect an invalid file")
            except GleModelException:
                pass

    unittest.main()
