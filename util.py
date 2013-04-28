# -*- coding: iso-8859-1 -*-
def capitalize(str):
  if not str:
    return str
  return str[0].upper() + str[1:]

def lowercase(str):
  if not str:
    return str
  return str[0].lower() + str[1:]

def depends(model):
  depends = set()
  for variable in model.data:
    if variable.type not in [int, str, float, bool, chr, None]:
      depends.add(variable.type)
  for func in model.functions + model.properties:
    if func.result not in [int, str, float, bool, chr, None]:
      depends.add(func.result)
    for variable in func.arguments:
      if variable.type not in [int, str, float, bool, chr, None]:
        depends.add(variable.type)
  return depends

def make_rerunner(data):
    def rerun_for(name, values):
        if name in data:
            return
        message = 'File must be run iterating %s over %s' % (name, values)
        raise RecurException(name, values, message)
    return rerun_for

class RecurException(Exception):
    def __init__(self, name, values, message):
        Exception.__init__(self, message)
        self.name = name
        self.values = values
