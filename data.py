import yaml
try:
    from yaml import CLoader as Loader, CDumper as Dumper
except ImportError:
    from yaml import Loader, Dumper

def load(location = 'data.yaml'):
    f = open(location, 'r')
    data = yaml.load(f, Loader)
    print data

if __name__ == '__main__':
    load()
