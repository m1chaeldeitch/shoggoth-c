# Serialization refactor
# The idea is to be able to do the following transformations:
#       File (C) ->  AST
#       AST      ->  Dict
#       Dict     ->  JSON
# And the reverse order ( JSON -> Dict -> AST)

import pycparser
import json
import re

from pycparser import c_ast
from pycparser.plyparser import Coord

'''Used for identification of internal attributes of a node'''
RE_INTERNAL_ATTR = re.compile('__.*__')


'''Gets only the child attributes of an input node'''
def get_child_attr(node):
    node_class = node.__class__

    local_attribs = set(node_class.attr_names)
    all_attribs = []

    for attrib in node_class.__slots__:
        if not RE_INTERNAL_ATTR.match(attrib):
            all_attribs.append(attrib)

    all_attribs = set(all_attribs)
    return all_attribs - local_attribs

'''Returns a JSON representation of the C source file'''
def file_to_json(file_name):
    #   File (c) -> ast -> dict -> json
    ast_rep = pycparser.parse_file(file_name)
    dictionary_rep = node_to_dict(ast_rep)
    return  json.dumps(dictionary_rep, sort_keys=True, indent=4)


'''Returns the ast representation of some json string'''
'''NOTE: Error handling not included!!'''
def from_json_to_ast(json_str):
    dict_representation = json.loads(json_str)
    return from_dict_to_ast(dict_representation)

'''Returns an AST representation of a C source file'''
def file_to_ast(file_name):
    return pycparser.parse_file(file_name)

'''Returns a dictionary representation of the AST
   Needed because json library can directly turn a dict to json format'''
def node_to_dict(node_in_ast):
    #Initialize a new dict for the ast
    dict_representation = {}

    #Record metadata of the node
    dict_representation["_nodetype"] = node_in_ast.__class__.__name__

    #Record Local node attribs
    local_attribs = node_in_ast.attr_names

    for attr in local_attribs:
        dict_representation[attr] = getattr(node_in_ast, attr)

    #Record Coord object (serialize first)
    if node_in_ast.coord is not None:
        coord_string = node_in_ast.coord.file + ":" + str(node_in_ast.coord.line) + ":"+ str(node_in_ast.coord.column)
        dict_representation["coord"] = coord_string
    else:
        dict_representation["coord"] = None


    # Record child attribs (might come in the form of a dict, or array of dicts)
    # Keep in mind that the children are either a dictionary {}, or a LIST [] of dictionaries {}
    # This should appear like [{d1},{d2},d3}]
    # This is not currently the case
    number_of_children = len(node_in_ast.children())

    if number_of_children > 1:
        children = []
        child_name_original = node_in_ast.children()[0][0].split("[")[0]
        for i in range(0, number_of_children):
            child_name = node_in_ast.children()[i][0]
            child_name = child_name.split("[")[0]
            if child_name_original != child_name:
                if (len(children) == 1):
                    dict_representation[child_name_original] = children[0]
                else:
                    dict_representation[child_name_original] = children
                children = []

            child_dict = node_to_dict(node_in_ast.children()[i][1])
            children.append(child_dict)
        if (len(children) == 1):
            dict_representation[child_name] = children[0]
        else:
            dict_representation[child_name] = children

    elif number_of_children == 1:
        for i in range(0, number_of_children):
            child_name = node_in_ast.children()[i][0]
            child_name = child_name.split("[")[0]

            child_dict = node_to_dict(node_in_ast.children()[i][1])

            if child_name == 'ext' or child_name == 'block_items':
                child_as_array = []
                child_as_array.append(child_dict)
                dict_representation[child_name] = child_as_array
            else:
                dict_representation[child_name] = child_dict

    #Record missing attributes of the node as null in the JSON instead of omitting them
    for child_attr in get_child_attr(node_in_ast):
        if child_attr not in dict_representation:
            dict_representation[child_attr] = None
    return dict_representation


'''Part of the deserialization from a python dict back to ast representation'''
def from_dict_to_ast(dict_representation):
    if dict_representation.__class__.__name__ == 'str' or dict_representation.__class__.__name__ == 'int':
        obj_type = dict_representation.__class__
        return obj_type(dict_representation)
    class_name = dict_representation.pop("_nodetype")
    node_class = getattr(c_ast, class_name)

    objs = {}
    for key, value in dict_representation.items():
        if key == 'coord':
            if (value is not None):
                components = value.split(":")
                coord_obj = Coord(components[0], int(components[1]), int(components[2]))
                objs[key] = coord_obj
            else:
                objs[key] = None
        else:
            value_type = type(value)
            if value_type is dict:
                objs[key] = from_dict_to_ast(value)
            elif value_type is list:
                items = []
                for item in value:
                    items.append(from_dict_to_ast(item))
                objs[key] = items
            else:
                objs[key] = value

    return node_class(**objs)

if __name__ == "__main__":
    #This segment is for testing the serialization aspect only
    #   c -> ast -> dict -> json
    # ast = pycparser.parse_file('dummy.c')
    # dictionary = node_to_dict(ast)
    # print(json.dumps(dictionary, sort_keys=True, indent=4))

    #This segment is for testing the de/reserialization aspect
    #   c -> ast -> dict -> ast -> json
    # ast_prelim = file_to_ast("dummy.c")
    # ast_dict = node_to_dict(ast_prelim)
    # ast = from_dict_to_ast(ast_dict)
    # print(json.dumps(node_to_dict(ast), sort_keys=True, indent=4))

    #This segment is just producing a json representation of the input C file (serialization)
    print(file_to_json('dummy.c'))

    #Testing the capabilities of returning the correct AST from a json string
    # print("REFACTORED VERSION TO OBTAIN AST")
    # json_representation = file_to_json("dummy.c")
    # ast = from_json_to_ast(json_representation)
    # ast.show()
    #
    # print("\n\n\nORIGINAL AST GENERATED FROM PYCPARSER")
    # ast_example = pycparser.parse_file("dummy.c")
    # ast_example.show()

