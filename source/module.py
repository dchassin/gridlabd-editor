"""GridLAB-D Editor Module Model Item

TODO
"""

from model import GldModelItem

class GldModelModule(GldModelItem):
    """TODO
    """
    def __init__(self,**kwargs):
        """TODO
        """
        super().__init__(self,**kwargs)

if __name__ == "__main__":

    import unittest

    class TestGldModelModule(unittest.TestCase):

        def test_init_ok(self):
            # check normal arglist constructor
            module = GldModelModule(name="test",value="123")
            self.assertEqual(module.get_name(),"test")
            self.assertEqual(module["value"],"123")

        def test_init_none(self):
            # check no-data arglist constructor
            module = GldModelModule(name="test")
            self.assertEqual(module.get_name(),"test")
            self.assertEqual(module["value"],None)

        def test_init_anon_none(self):
            # check default arglist constructor
            module = GldModelModule()
            self.assertEqual(module.get_name(),None)
            self.assertEqual(module["value"],None)

        def test_init_anon(self):
            # check no-name arglist constructor
            module = GldModelModule(value="123")
            self.assertEqual(module.get_name(),None)
            self.assertEqual(module["value"],"123")

        def test_init_data(self):
            # check data block constructor
            data={"name":"test","value":"123"}
            module = GldModelModule(data=data)
            self.assertEqual(module.get_name(),"test")
            self.assertEqual(module.get_data(),{"value":"123"})
            self.assertEqual(module["value"],"123")
            self.assertEqual(module.as_tuple(),("test",{"value":"123"}))
            self.assertEqual(module.as_dict(),data)

        def test_set_data(self):
            # check data set
            module = GldModelModule(name="test",value="123")
            module["value"] = "456"
            self.assertEqual(module["value"],"456")

        def test_set_iid(self):
            # check iid usage
            module = GldModelModule(name="test",value="123",iid="I012")
            self.assertEqual(module.get_attr("iid"),"I012")

    unittest.main()
