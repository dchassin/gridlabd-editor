"""GridLAB-D Editor Model

TODO
"""

class GldModelItem:
    """TODO
    """
    attributes = ["name","iid"]
    def __init__(self,**kwargs):
        """TODO
        """
        for attr in self.attributes:
            if attr in kwargs:
                setattr(self,attr,kwargs[attr])
                del kwargs[attr]
            else:
                setattr(self,attr,None)
        self.data = {}
        self.set_data(kwargs["data"] if "data" in kwargs else kwargs)

    def get_data(self):
        """TODO
        """
        return self.data

    def set_data(self,data):
        """TODO
        """
        for key, value in data.items():
            self.data[key] = str(value)

    def set_name(self,name):
        """TODO
        """
        self.name = name

    def get_name(self):
        """TODO
        """
        return self.name

    def as_dict(self):
        """TODO
        """
        result = {"name":self.name}
        result.update(self.data)
        return result

    def as_tuple(self):
        """TODO
        """
        return (self.name,self.data)

    def __getitem__(self,name):
        """TODO
        """
        return self.data[name] if name in self.data else None

    def __setitem__(self,name,value):
        """TODO
        """
        self.data[name] = value

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
        assert isinstance(item,GldModelItem)

if __name__ == "__main__":

    import unittest

    class TestItemClass(GldModelItem):
        def __init__(self,**kwargs):
            """TODO
            """
            super().__init__(self,**kwargs)

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
                raise Exception("test failed")
            except AssertionError:
                pass

    unittest.main()
