#!/usr/bin/env python3
# -*- coding: iso-8859-1 -*-
import argparse
import data
from writer import write

def insert_model(list, model):
    if model.parent and model.parent not in list:
        insert_model(list, model.parent)
    if model not in list:
        list.append(model)

def parse_data(data):
    globals = data.globals
    name = data.name
    models = []
    for i in data.models:
        insert_model(models, i)

    return {'models':models, 'globals':globals, 'name':name}



if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Run The Codegen To Automatically Generate Some Codez')
    parser.add_argument('-d', '--data', dest='data_path', default='./data.yaml', help='The path to data.yabl')
    parser.add_argument('-o', '--output', dest='out_path', default='./output', help='The output of the codegen.')
    parser.add_argument('-t', '--template', dest='template_path', default='./templates', help='The location of the templates')

    args = parser.parse_args()

    data = data.load(args.data_path)

    objects = parse_data(data)
    output = args.out_path
    templates = args.template_path
    
    write(templates, output, objects)

