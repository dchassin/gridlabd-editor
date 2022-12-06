"""GridLAB-D Editor Model

TODO
"""

import json

ATTRIBUTES = ["name","type","group","iid"]

class GldModelException(Exception):
    pass

class GldModelItem:
    """TODO
    """
    def __init__(self,**kwargs):
        """TODO
        """
        for attr in ATTRIBUTES:
            if attr in kwargs: 
                setattr(self,attr,kwargs[attr])
                del kwargs[attr]
            else:
                setattr(self,attr,None)
        self.data = {}
        self.set_data(kwargs["data"] if "data" in kwargs else kwargs)

    def get_data(self,without=ATTRIBUTES):
        """TODO
        """
        result = {}
        for attr in ATTRIBUTES:
            if without == None or not attr in without:
                result[attr] = getattr(self,attr)
        result.update(self.data)
        return result

    def set_data(self,data):
        """TODO
        """
        for key, value in data.items():
            if key in ATTRIBUTES:
                setattr(self,attr,value)
            else:
                self.data[key] = str(value)

    def dict(self,tagged=True,without=ATTRIBUTES):
        """TODO
        """
        if not self.name:
            return {}
        if tagged:
            return {self.name : self.get_data(without=ATTRIBUTES if not with_attributes else None)}
        else:
            return self.get_data(without)

    def tuple(self,without=ATTRIBUTES):
        """TODO
        """
        return (self.name,self.get_data(without))

    def json(self,tagged=True,without=ATTRIBUTES):
        """TODO
        """
        data = {}
        return json.dumps(self.dict(tagged,without))

    def glm(self):
        return None;        

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
        kwargs["type"] = "module"
        super().__init__(**kwargs)

    def glm(self):
        """TODO
        """
        result = [f"module {self.name} {{"]
        result.extend([f"    {name} \"{value}\";" for name,value in self.data.items()])
        result.append("}")
        return "\n".join(result)

class GldModelClass(GldModelItem):
    """TODO
    """
    def __init__(self,**kwargs):
        """TODO
        """
        kwargs["type"] = "class"
        super().__init__(**kwargs)

class GldModelObject(GldModelItem):
    """TODO
    """
    def __init__(self,**kwargs):
        """TODO
        """
        kwargs["type"] = "object"
        super().__init__(**kwargs)

class GldModelObject(GldModelItem):
    """TODO
    """
    def __init__(self,**kwargs):
        """TODO
        """
        kwargs["type"] = "object"
        super().__init__(**kwargs)

class GldModelClock(GldModelItem):
    """TODO
    """
    def __init__(self,**kwargs):
        """TODO
        """
        kwargs["type"] = "clock"
        super().__init__(**kwargs)

class GldModelInput(GldModelItem):
    """TODO
    """
    def __init__(self,**kwargs):
        kwargs["type"] = "input"
        super().__init__(**kwargs)

class GldModelGlobal(GldModelItem):
    """TODO
    """
    def __init__(self,**kwargs):
        """TODO
        """
        kwargs["type"] = "global"
        super().__init__(**kwargs)

class GldModelInclude(GldModelItem):
    """TODO
    """
    def __init__(self,**kwargs):
        """TODO
        """
        kwargs["type"] = "include"
        super().__init__(**kwargs)

class GldModelOutput(GldModelItem):
    """TODO
    """
    def __init__(self,**kwargs):
        """TODO
        """
        kwargs["type"] = "output"
        super().__init__(**kwargs)

class GldModelFilter(GldModelItem):
    """TODO
    """
    def __init__(self,**kwargs):
        """TODO
        """
        kwargs["type"] = "filter"
        super().__init__(**kwargs)

class GldModelSchedule(GldModelItem):
    """TODO
    """
    def __init__(self,**kwargs):
        """TODO
        """
        kwargs["type"] = "schedule"
        super().__init__(**kwargs)

class GldModelGroup(GldModelItem):
    """TODO
    """
    def __init__(self,**kwargs):
        """TODO
        """
        kwargs["type"] = "group"
        super().__init__(**kwargs)

class GldModelTemplate(GldModelItem):
    """TODO
    """
    def __init__(self,**kwargs):
        """TODO
        """
        kwargs["type"] = "template"
        super().__init__(**kwargs)

class GldModelCode(GldModelItem):
    """TODO
    """
    def __init__(self,**kwargs):
        """TODO
        """
        kwargs["type"] = "code"
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
            self.assertEqual(module.name,"test")
            self.assertEqual(module["value"],"123")

        def test_init_none(self):
            # check no-data arglist constructor
            module = GldModelModule(name="test")
            self.assertEqual(module.name,"test")
            self.assertEqual(module["value"],None)

        def test_init_anon_none(self):
            # check default arglist constructor
            module = GldModelModule()
            self.assertEqual(module.name,None)
            self.assertEqual(module["value"],None)
            module.set_data({"value":"123"})
            self.assertEqual(module["value"],"123")

        def test_init_anon(self):
            # check no-name arglist constructor
            module = GldModelModule(value="123")
            self.assertEqual(module.name,None)
            self.assertEqual(module["value"],"123")

        def test_init_data(self):
            # check data block constructor
            data={"name":"test","value":"123"}
            module = GldModelModule(**data)
            self.assertEqual(module.name,"test")
            self.assertEqual(module.get_data(),{"value":"123"})
            self.assertEqual(module["value"],"123")
            self.assertEqual(module.tuple(),("test",{"value":"123"}))
            self.assertEqual(module.dict(tagged=False,without=['iid','type','group']),data)

        def test_set_data(self):
            # check data set
            module = GldModelModule(name="test",value="123")
            module["value"] = "456"
            self.assertEqual(module["value"],"456")

        def test_set_iid(self):
            # check iid usage
            module = GldModelModule(name="test",value="123",iid="I012")
            self.assertEqual(module.iid,"I012")

        def test_module_glm(self):
            # check glm syntax
            module = GldModelModule(name="test",value="123",iid="I012",group="A")
            self.assertEqual(module.glm(),"module test {\n    value \"123\";\n}")

    unittest.main()
