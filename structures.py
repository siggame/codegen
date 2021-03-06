# -*- coding: iso-8859-1 -*-
from copy import copy
from operator import attrgetter
namegetter = attrgetter('name') #Used for sorting

models = {}

class Model(object):
    data = []
    functions = []
    name = ''
    plural = ''
    doc = ''
    type = ''
    parent = None
    def __init__(self, name, **kwargs):
        self.data = [ Variable('id', int, None, None, 'Unique Identifier') ]
        self.functions = []
        self.name = name
        self.plural = name + 's'
        self.type = 'Model'

        if 'parent' in kwargs and kwargs['parent']:
            self.parent = models[kwargs['parent']]
            self.data = copy(self.parent.data)
            self.functions = copy(self.parent.functions)
        if 'data' in kwargs:
            data = kwargs['data']
            self.data.extend(data)
        if 'functions' in kwargs:
            functions = kwargs['functions']
            self.functions.extend(functions)
        if 'doc' in kwargs:
            self.doc = kwargs['doc']
        if 'type' in kwargs:
            self.type = kwargs['type']
        if 'plural' in kwargs:
            self.plural = kwargs['plural']

        self.data.sort(key=namegetter)
        self.functions.sort(key=namegetter)
        

        models[name] = self

    @property
    def locals(self):
        return [i for i in self.data
                if not i.through
                and not isinstance(i.type, Model)]

    @property
    def remotes(self):
        return [i for i in self.data if i.through]

    @property
    def relations(self):
        return [i for i in self.data
                if not i.through
                and isinstance(i.type, Model)]

class Variable(object):
    name = ''
    type = None
    doc = ''

    def __init__(self, name, type = None, through = None, to = None, doc=''):
        self.name = name
        self.type = type
        self.through = through
        self.to = to
        self.doc = doc

class Animation(object):
    name = ''
    data = []

    def __init__(self, name, **kwargs):
        self.data = []
        self.name = name
        if 'data' in kwargs:
            data = kwargs['data']
            self.data.extend(data)


class Function(object):
    name = ''
    arguments = []
    result = None
    doc = ''

    def __init__(self, name, arguments=[], doc=''):
        self.name = name
        self.arguments = arguments
        self.doc = doc
