"""GridLAB-D Editor Model

The model module manages GLM models for the GridLAB-D Editor.
"""

import json

ATTRIBUTES = ["itype","iparent","iid"]

class GldModelException(Exception):
    pass

class GldModelItem:
    """Abstract class for model items
    """
    def __init__(self,**kwargs):
        """TODO
        """
        self.data = {}
        self.set_data(kwargs)

    def get_data(self,key=None,strict=False):
        """get model item data
        """
        if key == None:
            return self.data
        elif type(key) is str:
            if key in self.data:
                return self.data[key]
            elif not strict:
                return None
            else:
                raise GldModelException("key '{key}' not found")
        else:
            raise GldModelException("data key must be a string")

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

class GldModelModule(GldModelItem):
    """TODO
    """
    def __init__(self,**kwargs):
        """TODO
        """
        kwargs["itype"] = "module"
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
            model.add_item(GldModelModule(name=module))
            for name,values in data["globals"].items():
                if name.startswith(f"{module}::"):
                    print("GLOBAL:",name,values)
                    item = GldModelGlobal(name=name.split("::")[1],value=values["value"])
                    model.add_item(item)

class GldModelClass(GldModelItem):
    """TODO
    """
    def __init__(self,**kwargs):
        """TODO
        """
        kwargs["itype"] = "class"
        super().__init__(**kwargs)

    def glm(self):
        """TODO
        """
        result = [f"class {self.get_data('name')} {{"]
        result.extend([f"    {name} \"{value}\";" for name,value in self.items() if name != "name"])
        result.append("}")
        return super().glm() + "\n".join(result)

class GldModelObject(GldModelItem):
    """TODO
    """
    def __init__(self,**kwargs):
        """TODO
        """
        kwargs["itype"] = "object"
        super().__init__(**kwargs)

    def glm(self):
        """TODO
        """
        result = [f"object {self.get_data('name')} {{"]
        result.extend([f"    {name} \"{value}\";" for name, value in self.items() if name != "name"])
        result.append("}")
        return super().glm() + "\n".join(result)

class GldModelObject(GldModelItem):
    """TODO
    """
    def __init__(self,**kwargs):
        """TODO
        """
        kwargs["itype"] = "object"
        super().__init__(**kwargs)

class GldModelClock(GldModelItem):
    """TODO
    """
    def __init__(self,**kwargs):
        """TODO
        """
        kwargs["itype"] = "clock"
        super().__init__(**kwargs)

class GldModelInput(GldModelItem):
    """TODO
    """
    def __init__(self,**kwargs):
        kwargs["itype"] = "input"
        super().__init__(**kwargs)

class GldModelGlobal(GldModelItem):
    """TODO
    """
    def __init__(self,**kwargs):
        """TODO
        """
        kwargs["itype"] = "global"
        super().__init__(**kwargs)

class GldModelInclude(GldModelItem):
    """TODO
    """
    def __init__(self,**kwargs):
        """TODO
        """
        kwargs["itype"] = "include"
        super().__init__(**kwargs)

class GldModelOutput(GldModelItem):
    """TODO
    """
    def __init__(self,**kwargs):
        """TODO
        """
        kwargs["itype"] = "output"
        super().__init__(**kwargs)

class GldModelFilter(GldModelItem):
    """TODO
    """
    def __init__(self,**kwargs):
        """TODO
        """
        kwargs["itype"] = "filter"
        super().__init__(**kwargs)

class GldModelSchedule(GldModelItem):
    """TODO
    """
    def __init__(self,**kwargs):
        """TODO
        """
        kwargs["itype"] = "schedule"
        super().__init__(**kwargs)

class GldModelGroup(GldModelItem):
    """TODO
    """
    def __init__(self,**kwargs):
        """TODO
        """
        kwargs["itype"] = "group"
        super().__init__(**kwargs)

class GldModelTemplate(GldModelItem):
    """TODO
    """
    def __init__(self,**kwargs):
        """TODO
        """
        kwargs["itype"] = "template"
        super().__init__(**kwargs)

class GldModelCode(GldModelItem):
    """TODO
    """
    def __init__(self,**kwargs):
        """TODO
        """
        kwargs["itype"] = "code"
        super().__init__(**kwargs)

class GldModelSource(GldModelItem):
    """TODO
    """
    def __init__(self,**kwargs):
        super().__init__(**kwargs)

class GldModelComment(GldModelItem):
    """TODO
    """
    def __init__(self,**kwargs):
        """TODO
        """
        super().__init__(**kwargs)
        self.type = "comment"

class GldModel :
    """TODO
    """
    def __init__(self,*args,**kwargs):
        """TODO
        """
        self.data = []

    def add_item(self,item):
        """TODO
        """
        if not isinstance(item,GldModelItem):
            raise GldModelException("item is not a GldModelItem")
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

            assert data["application"] == "gridlabd", GldModelException(f"{filename} does not contain a GridLAB-D model")
            
            # load modules
            for itemtype in globals():
                itemcls = eval(itemtype)
                if itemtype not in ["GldModel","GldModelItem"] and itemtype.startswith("GldModel") and hasattr(itemcls,"load"):
                    itemcls.load(self,data)
        print(self.glm()) # TODO delete this

    def glm(self):
        return "\n".join([item.glm() for item in self.data])     

if __name__ == "__main__":

    import unittest

    class TestItemClass(GldModelItem):
        def __init__(self,**kwargs):
            """TODO
            """
            super().__init__(**kwargs)

    class testGldModelItem(unittest.TestCase):

        def test_class(self):
            # check class valid instance
            self.assertTrue(isinstance(TestItemClass(),GldModelItem))

        def test_class(self):
            # check class iid capture
            item = TestItemClass(name="test",iid="I123",value="456")
            self.assertEqual(item.iid,"I123")

    class testGldModel(unittest.TestCase):

        def test_add_item_ok(self):
            # check valid add_item()
            model = GldModel()
            class TestClass(GldModelItem):
                pass
            model.add_item(TestClass())

        def test_add_item_badtype(self):    
            # check invalid add_item()
            model = GldModel()
            try:
                model.add_item(1)
                raise AssertionError("GldModel failed to detect invalid item")
            except GldModelException:
                pass

    class testGldModelModule(unittest.TestCase):

        def test_init_ok(self):
            # check normal arglist constructor
            module = GldModelModule(name="test",value="123")
            self.assertEqual(module.itype,"module")
            self.assertEqual(module.iparent,None)
            self.assertEqual(module.iid,None)
            self.assertEqual(module.get_data(),{'name': 'test', 'value': '123'})
            self.assertEqual(module.get_data("name"),"test")
            self.assertEqual(module.get_data("value"),"123")
            self.assertEqual(module["name"],"test")
            self.assertEqual(module["value"],"123")
            self.assertEqual(module.dict(),{'name': 'test', 'value': '123'})
            self.assertEqual(module.list(),[('name', 'test'), ('value', '123')])
            self.assertEqual(module.json(),'{"name": "test", "value": "123"}')
            self.assertEqual(module.glm(),'// {"itype": "module", "iparent": null, "iid": null}\n' + 
                'module test {\n    value "123";\n}')

        def test_init_none(self):
            # check no-data arglist constructor
            module = GldModelModule(name="test")
            self.assertEqual(module.get_data("name"),"test")
            self.assertEqual(module["value"],None)

        def test_init_data(self):
            # check data block constructor
            data={"name":"test","value":"123"}
            module = GldModelModule(**data)
            self.assertEqual(module.get_data(),{'name': 'test', 'value': '123'})
            self.assertEqual(module.get_data("name"),"test")
            self.assertEqual(module.get_data("value"),"123")
            self.assertEqual(module["name"],"test")
            self.assertEqual(module["value"],"123")
            self.assertEqual(module.dict(),{'name': 'test', 'value': '123'})
            self.assertEqual(module.list(),[('name', 'test'), ('value', '123')])
            self.assertEqual(module.json(),'{"name": "test", "value": "123"}')
            self.assertEqual(module.glm(),'// {"itype": "module", "iparent": null, "iid": null}\n' + 
                'module test {\n    value "123";\n}')

        def test_set_data(self):
            # check data set
            module = GldModelModule(name="test",value="123")
            module["value"] = "456"
            self.assertEqual(module["value"],"456")

        def test_set_iid(self):
            # check iid usage
            module = GldModelModule(name="test",value="123",iid="I012")
            self.assertEqual(module.iid,"I012")
            self.assertEqual(module.iparent,None)

        def test_set_iparent(self):
            # check iid usage
            module = GldModelModule(name="test",value="123",iparent="I012")
            self.assertEqual(module.iid,None)
            self.assertEqual(module.iparent,"I012")

        def test_model_glm(self):
            # check glm syntax
            model = GldModel()
            model.add_item(GldModelModule(name="test1",value="123"))
            model.add_item(GldModelModule(name="test2",value="456"))
            self.assertEqual(model.glm(),'// {"itype": "module", "iparent": null, "iid": null}\n' + 
                'module test1 {\n    value "123";\n}\n' + 
                '// {"itype": "module", "iparent": null, "iid": null}\n' + 
                'module test2 {\n    value "456";\n}')

        def test_model_load(self):
            model = GldModel()
            model.load("../example/network.json")

    unittest.main()
