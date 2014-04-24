import yaml
import structures
from collections import OrderedDict
from operator import attrgetter
namegetter = attrgetter('name') #Used for sorting

from yaml import Loader

#We need this to retain the order of named items
#Otherwise variable and function orders would be lost
#Borrowed and Python 3ified from Eric Naeseth's solution
#http://stackoverflow.com/a/5121963/1430838

class OrderedDictYAMLLoader(Loader):
    """
    A YAML loader that loads mappings into ordered dictionaries.
    """

    def __init__(self, *args, **kwargs):
        yaml.Loader.__init__(self, *args, **kwargs)

        self.add_constructor('tag:yaml.org,2002:map', type(self).construct_yaml_map)
        self.add_constructor('tag:yaml.org,2002:omap', type(self).construct_yaml_map)

    def construct_yaml_map(self, node):
        data = OrderedDict()
        yield data
        value = self.construct_mapping(node)
        data.update(value)

    def construct_mapping(self, node, deep=False):
        if isinstance(node, yaml.MappingNode):
            self.flatten_mapping(node)
        else:
            raise yaml.constructor.ConstructorError(None, None,
                'expected a mapping node, but found %s' % node.id, node.start_mark)

        mapping = OrderedDict()
        for key_node, value_node in node.value:
            key = self.construct_object(key_node, deep=deep)
            value = self.construct_object(value_node, deep=deep)
            mapping[key] = value
        return mapping

class GameData(object):
    def __init__(self, data):
        self.models = []
        self.globals = []
        self.name = data.get('game_name', 'The nameless one.')
        self.version = data.get('game_version', 1)

        if 'globals' in data:
            self.parse_globals(data['globals'])
        if 'functions' in data:
            self.parse_functions(data['functions'])
        if 'models' in data:
            self.parse_models(data['models'])

        self.map_types()

    def parse_globals(self, globals):
        self.globals = [self.parse_var(i) for i in globals.items()]
        self.globals.sort(key=namegetter)

    def parse_functions(self, functions):
        self.functions = [self.parse_func(i) for i in functions.items()]
        self.functions.sort(key=namegetter)

    def parse_models(self, models):
        parents = {i: j.get('parent', None) for i, j in models.items()}
        while parents:
            eligible = [i for i in parents if parents[i] not in parents]
            if not eligible:
                raise ValueError('Circular inheritance tree')
            for i in eligible:
                self.models.append(self.parse_model(i, models[i]))
                del parents[i]
        self.models.sort(key=namegetter)


    def parse_var(self, var):
        name, data = var
        type = data.get('type', None)
        through = data.get('through', None)
        to = data.get('to', through)
        doc = data.get('doc', '')

        return structures.Variable(name, type, through, to, doc)

    def parse_func(self, func):
        name, data = func
        doc = data.get('doc', '')
        arguments = data.get('arguments', {})

        arguments = [self.parse_var(i) for i in arguments.items()]

        return structures.Function(name, arguments, doc)


    def parse_model(self, name, model):
        data = model.get('data', {})
        doc = model.get('doc', '')
        type = model.get('type', 'Model')
        functions = model.get('functions', {})
        parent = model.get('parent', None)
        plural = model.get('plural', name+'s')

        data = [self.parse_var(i) for i in data.items()]
        data.sort(key=namegetter)

        functions = [self.parse_func(i) for i in functions.items()]
        functions.sort(key=namegetter)

        return structures.Model(name, data=data, doc=doc, type=type,
                functions=functions, plural=plural, parent=parent)
    
    def variables(self, globs=True, data=True, args=True):
        if globs:
            for i in self.globals:
                yield i
            if args:
                for j in self.functions:
                    for k in j.arguments:
                        yield k
        for i in self.models:
            if data:
                for j in i.data:
                    yield j
            if args:
                for j in i.functions:
                    for k in j.arguments:
                        yield k
    
    def map_types(self):
        for var in self.variables():
            if not isinstance(var.type, str):
                continue
            if var.type == 'int':
                var.type = int
            elif var.type == 'str':
                var.type = str
            elif var.type == 'float':
                var.type = float
            elif var.type == 'bool':
                var.type = bool
            else:
                model = [i for i in self.models if i.name == var.type]
                if not model:
                    raise ValueError('{} is not a known type'.format(var.type))
                var.type = model[0]
    
    def connect_var(self, model, var, depth = 0):
        if depth > 10:
            print('Max relation following exceeded for {} on {}').format(
                model.name, var.name)
        if var.type:
            return
        if not var.through:
            return
        medium = [i for i in model.data if i.name == var.through]
        other = medium.type
        remote = [i for i in other if i.name == var.to]
        self.connect_var(other, remote, depth+1)
        var.type = remote.type
    
    def connect_vars(self):
        for var in self.variables(globs=False, args=False):
            self.connect_var(var)

def load(location = 'data.yaml'):
    f = open(location, 'r')
    data = yaml.load(f, OrderedDictYAMLLoader)

    return GameData(data)

if __name__ == '__main__':
    load()
