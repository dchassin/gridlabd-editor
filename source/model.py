"""GridLAB-D Editor Model

The model module manages GLM models for the GridLAB-D Editor.
"""

import os, sys, subprocess, asyncio
import json
import tempfile

IID = "IID"
ITYPE = "ITYPE"
IPARENT = "IPARENT"
ATTRIBUTES = [ITYPE,IPARENT,IID]

HIDDEN_PROPERTIES = [
    "class",
    "id",
    "rank",
    "flags",
    ]
HIDDEN_GLOBALS = [
    ]

class GldModelException(Exception):
    pass

class GldModelError(Exception):
    pass

################################################################################
#
# Model items
#
################################################################################

class GldModelItem:
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
        - strict    flag to enable GldModelError exception if key not found

        Returns:
        - str       data value if found, None if not found

        Exceptions:
        - GldModelError: key not found
        - GldModelException: key is not a string
        """
        if key == None:
            return self.data
        elif type(key) is str:
            if key in self.data:
                return self.data[key]
            elif not strict:
                return None
            else:
                raise GldModelError("key '{key}' not found")
        else:
            raise GldModelException("key '{key}' is not a string'")

    def set_data(self,data):
        """Set model data"""
        self.data.update(dict([(key,value) \
            for key,value in data.items() if key not in ATTRIBUTES]))
        for key in ATTRIBUTES:
            if key in data:
                setattr(self,key,data[key])
            else:
                setattr(self,key,None)

    def zip(self,attr=False):
        """Return zip of model data or model attributes

        Arguments:
        - attr  Flag to choose model data or model attributes

        Returns:
        zip - model data or model attributes
        """
        if attr:
            return zip(ATTRIBUTES,[getattr(self,attr) \
                for attr in ATTRIBUTES])
        else:
            return zip(self.data.keys(),self.data.values())

    def items(self,attr=False):
        """Return model data or attributes as items tuples"""
        return self.dict(attr=attr).items()

    def dict(self,key=None,attr=False):
        """Return model data or attributes as dict

        Arguments:
        - attr  Flag to choose model data or model attributes

        Returns:
        dict - model data or model attributes
        """
        if attr:
            if key == None:
                return dict(self.zip(True))
            else:
                return getattr(self,key)
        elif key == None:
            return self.data
        else:
            return {self.data["key"]: dict([(tag,value) \
                for tag,value in self.data if tag != key])}

    def list(self,attr=False):
        """Return model data or attributes as list of tuples

        Arguments:
        - attr  Flag to choose model data or model attributes

        Returns:
        list - model data or model attributes
        """
        return list(self.items(attr))

    def json(self,key=None,attr=False):
        """Return model data or attributes as json string

        Arguments:
        - attr  Flag to choose model data or model attributes

        Returns:
        json - model data or model attributes
        """
        return json.dumps(self.dict(key,attr))

    def glm(self):
        """Return GLM string of model"""
        tag = json.dumps(dict(zip(ATTRIBUTES,[getattr(self,attr) \
            for attr in ATTRIBUTES])))
        return f"""// {tag}\n""";

    def __getitem__(self,name):
        """Get a data item"""
        return self.data[name] if name in self.data else None

    def __setitem__(self,name,value):
        """Set a data item"""
        self.data[name] = value

class GldModelModule(GldModelItem):
    """Model module item"""
    def __init__(self,**kwargs):
        """Construct a module item"""
        kwargs[ITYPE] = "module"
        super().__init__(**kwargs)

    def glm(self):
        """Get GLM of module item"""
        result = [f"module {self.get_data('name')} {{"]
        result.extend([f"    {name} \"{value}\";" \
            for name,value in self.items() if name != "name"])
        result.append("}")
        return super().glm() + "\n".join(result)

    @staticmethod
    def load(model,data):
        """Load a module items contained data"""
        for module in data["modules"]:
            mod = GldModelModule(name=module)
            model.add_item(mod)
            for name,values in data["globals"].items():
                if name.startswith(f"{module}::"):
                    mod.set_data({name.split("::")[1]:values["value"]})

class GldModelClass(GldModelItem):
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
        result.extend([f"    {name} \"{value}\";" \
            for name,value in self.items() if name != "name"])
        result.append("}")
        return super().glm() + "\n".join(result)

class GldModelObject(GldModelItem):
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
        result.extend([f"    {name} \"{value}\";" \
            for name, value in self.items() \
            if not name in HIDDEN_PROPERTIES and value != ""])
        result.append("}")
        return super().glm() + "\n".join(result)

    @staticmethod
    def load(model,data):
        for name,spec in data["objects"].items():
            obj = GldModelObject(name=name,**spec)
            model.add_item(obj)

class GldModelClock(GldModelItem):
    """TODO
    """
    def __init__(self,**kwargs):
        """TODO
        """
        kwargs[ITYPE] = "clock"
        super().__init__(**kwargs)

    def glm(self):
        """TODO
        """
        result = ["clock {"]
        result.extend([f"    {name} \"{value}\"" \
            for name, value in self.items()])
        result.append("}")
        return super().glm() + "\n".join(result)

    def load(model,data):
        spec = {}
        for name in ["timezone","starttime","stoptime"]:
            if name in data["globals"]:
                spec[name] = data["globals"][name]["value"]
            else:
                spec[name] = None

class GldModelInput(GldModelItem):
    """TODO
    """
    def __init__(self,**kwargs):
        kwargs[ITYPE] = "input"
        super().__init__(**kwargs)

class GldModelGlobal(GldModelItem):
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
        name = self.get_data('name')
        value = self.get_data('value')
        access = self.get_data('access')
        initial = self.get_data('initial')
        if name not in HIDDEN_GLOBALS \
                and access == "PUBLIC" \
                and value not in [initial,""]:
            return super().glm() + f"#set {name}={value}"
        else:
            return super().glm() + \
                f"// {name}={value} is {access} with initial={initial}"

    @staticmethod
    def load(model,data):
        for name,spec in data["globals"].items():
            if not "::" in name:
                var = GldModelGlobal(name=name,**spec)
                model.add_item(var)

class GldModelInclude(GldModelItem):
    """TODO
    """
    def __init__(self,**kwargs):
        """TODO
        """
        kwargs[ITYPE] = "include"
        super().__init__(**kwargs)

class GldModelOutput(GldModelItem):
    """TODO
    """
    def __init__(self,**kwargs):
        """TODO
        """
        kwargs[ITYPE] = "output"
        super().__init__(**kwargs)

class GldModelFilter(GldModelItem):
    """TODO
    """
    def __init__(self,**kwargs):
        """TODO
        """
        kwargs[ITYPE] = "filter"
        super().__init__(**kwargs)

class GldModelSchedule(GldModelItem):
    """TODO
    """
    def __init__(self,**kwargs):
        """TODO
        """
        kwargs[ITYPE] = "schedule"
        super().__init__(**kwargs)

class GldModelGroup(GldModelItem):
    """TODO
    """
    def __init__(self,**kwargs):
        """TODO
        """
        kwargs[ITYPE] = "group"
        super().__init__(**kwargs)

class GldModelTemplate(GldModelItem):
    """TODO
    """
    def __init__(self,**kwargs):
        """TODO
        """
        kwargs[ITYPE] = "template"
        super().__init__(**kwargs)

class GldModelCode(GldModelItem):
    """TODO
    """
    def __init__(self,**kwargs):
        """TODO
        """
        kwargs[ITYPE] = "code"
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

################################################################################
#
# Models
#
################################################################################

class GldModel :
    """GridLAB-D editor model implementation class"""
    def __init__(self,**kwargs):
        """Construct a new model

        Arguments:
        - filename      file to initially load
        """
        self.data = {}
        self.index = []
        self.result = None
        if "filename" in kwargs:
            self.load(kwargs["filename"])
            del kwargs["filename"]
        if len(kwargs) > 0:
            raise GldModelException(f"keyword '{kwargs[0]} is not valid")

    @staticmethod
    def guid():
        """Generate a unique id for an item"""
        import random
        return random.randint(0,2**64-1)

    def add_item(self,item,at=-1):
        """Add an item to model

        Arguments:
        - item  item to add (must be derived from GldModelItem)
        - at    optional location in index at which to add item (-1 for tail)

        Returns:
        - guid  locator key for the item
        """
        if not isinstance(item,GldModelItem):
            raise GldModelException("item is not a GldModelItem")
        guid = self.guid()
        self.data[guid] = item
        self.index.insert(at if at >= 0 else len(self.index)-at+1,guid)
        return guid

    def del_item(self,guid):
        """Delete an item from the model using the locator key"""
        self.index.remove(guid)
        del self.data[guid]

    def keys(self):
        """Model iterator for key guids"""
        for key in self.index:
            yield key

    def values(self):
        """Model iterator for values"""
        for key in self.index:
            yield self.data[key]

    def items(self):
        """Model iterator for model key,value pairs"""
        for key in self.index:
            yield key, self.data[key]

    def to_json(self):
        return json.dumps({"index":self.index,"data":self.data})

    def load_json(self,filename):
        """Load a model from a JSON file"""
        with open(filename,"r") as glm:
            data = json.load(glm)

            # check if this is a valid JSON file
            if "application" not in data or data["application"] != "gridlabd":
                raise GldModelException(f"{filename} is not a GridLAB-D model")

            self.from_json(data)

    def from_json(self,data):
        """Load model from JSON data"""
        # load items by scanning through classes derived from GldModelItem
        for itemtype in globals():
            itemcls = eval(itemtype)
            if itemtype not in ["GldModel","GldModelItem"] \
                    and itemtype.startswith("GldModel") \
                    and hasattr(itemcls,"load"):
                itemcls.load(self,data)

    def load(self,filename):
        """Load a model from a file

        Supports GLM, GLD, and general JSON formatted files
        """

        # convert GLM to JSON
        if filename.endswith(".gld"):
            gld = json.load(filename)
            self.index = gld["index"]
            self.data = gld["data"]
        else:
            if filename.endswith(".glm"):
                glmname = filename
                filename = filename[:-4] + ".json"
                os.system(f"gridlabd -C {glmname} -o {filename}")
            self.load_json(filename)

    def glm(self):
        """Compile a GLM file from the model"""
        return "\n".join([self.data[guid].glm() for guid in self.index]) 

    def save(self,filename):
        if filename.endswith(".glm"):
            with open(filename,"w") as fh:
                fh.write(self.glm)
        elif filename.endswith(".gld"):
            with open(filename,"w") as fh:
                data = {}
                for key,value in self.data.items():
                    data[key] = value.dict()
                jsondata = {
                    "application" : "gridlabd-editor",
                    "version" : "1.0.1",
                    "index" : self.index,
                    "data" : data
                    }
                json.dump(jsondata,fh,indent=4)
        elif filename.endswith(".json"):
            with tempfile.NamedTemporaryFile(dir="/tmp",suffix=".glm") as tmpname:
                glm = self.glm()
                tmpname.write(glm.encode('utf-8'))
                tmpname.flush()
                command = ["gridlabd","-W","/tmp",tmpname,"-o",filename]

    def run(self,pre_options=[],post_options=[],workdir=".",
            saveglm='onerror',timeout=60,exception=True):
        """Run a GridLAB-D simulation

        Compile

        Arguments:
        - pre_options  list of options to provide before the GLM model is loaded
        - post-options list of options to provide after the GLM model is loaded 
        - workdir      working directory to use 
        - saveglm      condition under which GLM is saved in result 
        - timeout      simulation timeout limit in seconds 

        Returns:
        - subprocess.CompletedProcess on success
        - subprocess.SubprocessError on failure
        """
        self.result = None
        assert saveglm in ['never','always','onerror'], \
            GldModelException(f"saveglm='{saveglm}' is invalid")
        with tempfile.NamedTemporaryFile(dir=workdir,suffix=".glm") as tmpname:
            glm = self.glm()
            tmpname.write(glm.encode('utf-8'))
            tmpname.flush()
            command = ["gridlabd","-W",workdir]
            command.extend(pre_options)
            command.append(tmpname.name)
            command.extend(post_options)
            try:
                self.result = subprocess.run(command,
                    capture_output = True,
                    timeout = timeout if timeout else None)
                self.result.stdout = self.result.stdout.decode('utf-8')
                self.result.stderr = self.result.stderr.decode('utf-8')
            except Exception as err:
                if exception:
                    raise
                self.result = err
                self.result.returncode = -1
                self.result.stdout = ""
                e_type, e_value, e_trace = sys.exc_info()
                self.result.stderr = f"EXCEPTION: {e_type.__name__} {e_value}"
            if saveglm == 'always' \
                    or ( self.result.returncode != 0 and saveglm == 'error' ):
                setattr(self.result,"glm",glm)
            else:
                setattr(self.result,"glm",None)
        return self.result

################################################################################
#
# Unit tests
#
################################################################################

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
            # check class IID capture
            item = TestItemClass(name="test",IID="I123",value="456")
            self.assertEqual(item.IID,"I123")

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
            self.assertEqual(module.glm(),
                '// {"ITYPE": "module", "IPARENT": null, "IID": null}\n' + 
                'module test {\n    value "123";\n}')

        def test_set_data(self):
            # check data set
            module = GldModelModule(name="test",value="123")
            module["value"] = "456"
            self.assertEqual(module["value"],"456")

        def test_set_iid(self):
            # check IID usage
            module = GldModelModule(name="test",value="123",IID="I012")
            self.assertEqual(module.IID,"I012")
            self.assertEqual(module.IPARENT,None)

        def test_set_iparent(self):
            # check iparent usage
            module = GldModelModule(name="test",value="123",IPARENT="I012")
            self.assertEqual(module.IID,None)
            self.assertEqual(module.IPARENT,"I012")

        def test_model_glm(self):
            # check glm syntax
            model = GldModel()
            model.add_item(GldModelModule(name="test1",value="123"))
            model.add_item(GldModelModule(name="test2",value="456"))
            self.assertEqual(model.glm(),
                '// {"ITYPE": "module", "IPARENT": null, "IID": null}\n' + 
                'module test1 {\n    value "123";\n}\n' + 
                '// {"ITYPE": "module", "IPARENT": null, "IID": null}\n' + 
                'module test2 {\n    value "456";\n}')

        def test_model_run(self):
            model = GldModel()
            model.load("unittest/valid_glm.json")
            result = model.run(saveglm='always')
            with open("unittest/test.glm","w") as fh:
                fh.write(result.glm)
            with open("unittest/test.out","w") as fh:
                fh.write(result.stdout)
            with open("unittest/test.err","w") as fh:
                fh.write(result.stderr)
            self.assertEqual(result.returncode,0)

        def test_model_run_timeout(self):
            model = GldModel()
            model.load("unittest/valid_glm.json")
            r = model.run(saveglm='never',timeout=0.1,exception=False)
            self.assertEqual(r.returncode,-1)
            self.assertTrue(r.stderr.startswith("EXCEPTION: TimeoutExpired"))

        def test_model_load_error(self):
            model = GldModel()
            try:
                model.load("unittest/invalid_glm.json")
                raise AssertionError("GldModel.load() did not fail")
            except GldModelException:
                pass

        def test_iterators(self):
            model = GldModel()
            model.load("unittest/valid_glm.json")
            for num,key in enumerate(model.keys()):
                self.assertEqual(key,model.index[num])
            for num,value in enumerate(model.values()):
                self.assertEqual(value,model.data[model.index[num]])
            for num,item in enumerate(model.items()):
                key,value = item
                self.assertEqual(key,model.index[num])
                self.assertEqual(value,model.data[key])

        def test_load_glm(self):
            model = GldModel(filename="unittest/IEEE-13.glm")
            self.assertEqual(len(list(model.keys())),201)

        def test_load_json(self):
            model = GldModel(filename="unittest/IEEE-13.json")
            self.assertEqual(len(list(model.keys())),201)

        def test_load_fail(self):
            try:
                GldModel(filename="unittest/invalid_glm.json")
                raise AssertionError("GldModel(filename='unittest/invalid_glm.json') did not fail")
            except GldModelException:
                pass

        def test_save_gld(self):
            model = GldModel(filename="unittest/IEEE-13.glm")
            model.save("unittest/IEEE-13.gld")

    unittest.main()
