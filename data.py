import yaml
import structures
try:
    from yaml import CLoader as Loader, CDumper as Dumper
except ImportError:
    from yaml import Loader, Dumper

class GameData(object):
    def __init__(self, data):
        self.models = []
        self.globals = []
        self.name = data.get('game_name', 'The nameless one.')

        if 'globals' in data:
            self.parse_globals(data['globals'])
        if 'models' in data:
            self.parse_models(data['models'])

    def parse_globals(self, globals):
        self.globals = [self.parse_var(i) for i in globals.items()]

    def parse_models(self, models):
        parents = {i: j.get('parent', None) for i, j in models.items()}
        while parents:
            eligible = [i for i in parents if parents[i] not in parents]
            if not eligible:
                raise ValueError('Circular inheritance tree')
            for i in eligible:
                self.models.append(self.parse_model(i, models[i]))
                del parents[i]

    def parse_var(self, var):
        name, data = var
        type = data['type']
        doc = data.get('doc', '')

        return structures.Variable(name, type, doc)

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

        data = [self.parse_var(i) for i in data.items()]
        functions = [self.parse_func(i) for i in functions.items()]

        return structures.Model(name, data=data, doc=doc, type=type,
                parent=parent)


def load(location = 'data.yaml'):
    f = open(location, 'r')
    data = yaml.load(f, Loader)

    return GameData(data)

if __name__ == '__main__':
    load()
