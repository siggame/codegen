from mako.template import Template

import structures
import util
import os.path, os
from copy import deepcopy
import runpy

def write(source, dest, data):
    data = deepcopy(data)
    data['Model'] = structures.Model
    data['capitalize'] = util.capitalize
    data['lowercase'] = util.lowercase
    write_directory(source, dest, data)

def write_directory(source, dest, data):
    data = deepcopy(data)
    os.makedirs(dest, exist_ok=True)

    files = os.listdir(source)
    if '__helpers__.py' in files:
        #we want to use helpers.py to define extra values
        #so execute it and extract the new data
        #provide the existing data to maximize power!
        full_path = os.path.join(source, '__helpers__.py')
        data = runpy.run_path(full_path, data)

        #remove __builtins__ and other junk
        data = {k:v for k, v in data.items() if '__' not in k}

        files.remove('__helpers__.py')
    
    for path in files:
        full_path = os.path.join(source, path)
        if os.path.isfile(full_path):
            write_file(source, dest, data, path)
        elif os.path.isdir(full_path):
            template = Template(path)
            leaf = template.render(**data)
            full_dest = os.path.join(dest, leaf)
            write_directory(full_path, full_dest, data)

def write_file(source, dest, data, path):
    data = deepcopy(data)
    data['rerun_for'] = util.make_rerunner(data)
    full_path = os.path.join(source, path)

    #compile and save the template
    template = Template(filename=full_path)
    try:
        result = template.render(**data)
    #this is a bit fancy:
    #we have a special exception saying to rerun the file iterating over values
    #this way, you can say in-file to rerun it on each model for example
    except util.RecurException as err:
        for v in err.values:
            #so we iterate over the values and set the name
            data[err.name] = v
            #and try again
            write_file(source, dest, data, path)
        #and the recurred write should have done the work, so we stop now
        return
    
    #calculate the destination path
    template = Template(path)
    leaf = template.render(**data)
    outpath = os.path.join(dest, leaf)

    #write the file
    output = open(outpath, 'w')
    output.write(result)
    output.close()
