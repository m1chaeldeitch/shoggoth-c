# Serialization refactor
# The idea is to be able to do the following transformations:
#       File (C) ->  AST
#       AST      ->  Dict
#       Dict     ->  JSON
# And the reverse order ( JSON -> Dict -> AST)
from pstats import SortKey

import pycparser
import json




'''Returns a JSON representation of the C source file'''
def file_to_json(file_name):
    return "Coming soon..."



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


    #Record child attribs (might come in the form of a dict, or array of dicts)
    #TODO this child stuff isn't working correctly -- look into that lol

    # for i in range(1, len(node_in_ast.children()) + 1):
    #     child = node_in_ast.children()[0][i]
    #     child_dict = node_to_dict(child)
    #     dict_representation[node_in_ast.children()[0][i-1]] = child_dict


    # approach for finding all child tuples
    #TODO Keep in mind that the children are either a dictionary {}, or a LIST [] of dictionaries {}
    # This should appear like [{d1},{d2},d3}]
    # This is not currently the case
    number_of_children = len(node_in_ast.children())
    siblings = []

    #TODO
    # make a check if there is only one children and approach it differently
    # if there are more than one children, add them to a list then assign it to the dict representation
    # if there is only one children, just translate the node to a dict and then assign regularly in dict_representation

    '''
    #ONE CHILD CASE
    if number_of_children == 1:
        child_name = node_in_ast.children()[0][0]
        child_name = child_name.split("[")[0]
        child_dict = node_to_dict(node_in_ast.children()[0][1])
        dict_representation[child_name] = child_dict

    # >1 CHILD CASE
    elif number_of_children > 1:
        for i in range(0, number_of_children):
            child_name = node_in_ast.children()[i][0]
            child_name = child_name.split("[")[0]
            child_dict = node_to_dict(node_in_ast.children()[i][1])
            siblings.append(child_dict)

        dict_representation[node_in_ast.children()[0][0]] = siblings
    #OLD APPROACH
    '''

    if number_of_children > 0:
        children = []
        child_name_original = node_in_ast.children()[0][0]
        for i in range(0, number_of_children):
            child_name = node_in_ast.children()[i][0]
            child_name = child_name.split("[")[0]

            if child_name_original != child_name:
                dict_representation[child_name_original] = children
                children = []

            child_dict = node_to_dict(node_in_ast.children()[i][1])
            children.append(child_dict)

        dict_representation[child_name] = children

    # for child in node_in_ast.children():
    #     child_dict = node_to_dict(child)
    #     dict_representation[child.name] = child_dict

    return dict_representation


if __name__ == "__main__":
    ast = pycparser.parse_file('easy.c')
    dictionary = node_to_dict(ast)
    print(json.dumps(dictionary, sort_keys=True, indent=4))
    balls = True