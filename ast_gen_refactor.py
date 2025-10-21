# Serialization refactor
# The idea is to be able to do the following transformations:
#       File (C) ->  AST
#       AST      ->  Dict
#       Dict     ->  JSON
# And the reverse order ( JSON -> Dict -> AST)
from pstats import SortKey

import pycparser
import json
import re

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
    return "Coming soon..."



'''Returns an AST representation of a C source file'''
def file_to_ast(file_name):
    return pycparser.parse_file(file_name)

def node_to_dict_retry(node_in_ast):
    # Initialize a new dict for the ast
    dict_representation = {}

    # Record metadata of the node
    node_type = node_in_ast.__class__.__name__
    dict_representation["_nodetype"] = node_in_ast.__class__.__name__

    if node_type == 'FileAST':
        print("STOP")

    # Record Local node attribs
    local_attribs = node_in_ast.attr_names

    for attr in local_attribs:
        dict_representation[attr] = getattr(node_in_ast, attr)

    # Record Coord object (serialize first)
    if node_in_ast.coord is not None:
        coord_string = node_in_ast.coord.file + ":" + str(node_in_ast.coord.line) + ":" + str(node_in_ast.coord.column)
        dict_representation["coord"] = coord_string
    else:
        dict_representation["coord"] = None

    # Record child attribs of the current node (might come in the form of a dict, or array of dicts)
    number_of_children_attribs = len(node_in_ast.children())

    children = []
    curr_attrib_name = None

    # if number_of_children_attribs > 0:
    #     curr_attrib_name = node_in_ast.children()[0][0].split("[")[0]
    for i in range(0, number_of_children_attribs):
        # for each child attribute of the current node
        #   (1) Record the length of the attribute
        curr_attrib_name = node_in_ast.children()[i][0].split("[")[0]
        curr_attrib = node_in_ast.children()[i][1]
        children.append(node_to_dict_retry(curr_attrib))
        '''
        curr_attrib_length = len(curr_attrib.children())
        #   (2) If == 1 -> assign then do a key value pair like normal, where the
        #   key is the name of the attribute, and the value is the corresponding dictionary
        if curr_attrib_length == 1: #todo might have "or == 0"
            dict_representation[curr_attrib_name] = node_to_dict_retry(curr_attrib)

        #   (3) If > 1  -> create a list of the dictionaries, then assign the key value pair, where the key is the
        #   attribute name, and the value is the list of dictionaries.
        elif curr_attrib_length > 1:
            sub_children = []

            for j in range (0, curr_attrib_length):
                # for each child of the  current child attribute...
                sub_child = node_to_dict_retry(curr_attrib.children()[j][1])
                sub_children.append(sub_child)

            dict_representation[curr_attrib_name] = sub_children

        #todo might need else case
        '''

    if len(children) == 1:
        dict_representation[curr_attrib_name] = children[0]

    elif len(children) > 1:
        dict_representation[curr_attrib_name] = children


    return dict_representation







def node_to_dict_alternate(node_in_ast):
    # Initialize a new dict for the ast
    dict_representation = {}

    # Record metadata of the node
    node_type = node_in_ast.__class__.__name__
    dict_representation["_nodetype"] = node_in_ast.__class__.__name__

    if node_type == 'ParamList':
        print("STOP")

    # Record Local node attribs
    local_attribs = node_in_ast.attr_names

    for attr in local_attribs:
        dict_representation[attr] = getattr(node_in_ast, attr)

    # Record Coord object (serialize first)
    if node_in_ast.coord is not None:
        coord_string = node_in_ast.coord.file + ":" + str(node_in_ast.coord.line) + ":" + str(node_in_ast.coord.column)
        dict_representation["coord"] = coord_string
    else:
        dict_representation["coord"] = None

    # Record child attribs (might come in the form of a dict, or array of dicts)
    number_of_children = len(node_in_ast.children())
    siblings = []

    for i in range(0, number_of_children):
        number_of_child_children = len(node_in_ast.children()[i][1].children())

        if number_of_child_children > 1:
            children = []
            child_name_original = node_in_ast.children()[i][0].split("[")[0]
            for j in range(0, number_of_children):
                child_name = node_in_ast.children()[j][0]
                child_name = child_name.split("[")[0]

                if child_name_original != child_name:
                    dict_representation[child_name_original] = children
                    print(f"Found {child_name_original} in section where there should be 1 child (edge case though)")
                    children = []

                child_dict = node_to_dict_alternate(node_in_ast.children()[j][1])
                children.append(child_dict)
                x = 'stop'

            dict_representation[child_name] = children
            print(f"Found {child_name} in section where there should be 1 child")

        elif number_of_child_children == 1:
            for j in range(0, number_of_children):
                child_name = node_in_ast.children()[j][0]
                child_name = child_name.split("[")[0]

                child_dict = node_to_dict_alternate(node_in_ast.children()[j][1])
                dict_representation[child_name] = child_dict
                print(f"Found {child_name} in section where there should be >1 child")
                x = 'stop'
        else:
            child_name = node_in_ast.children()[i][0].split("[")[0]
            child_dict = node_to_dict_alternate(node_in_ast.children()[i][1])
            dict_representation[child_name] = child_dict

    return dict_representation

'''Returns a dictionary representation of the AST
   Needed because json library can directly turn a dict to json format'''
def node_to_dict(node_in_ast):
    #Initialize a new dict for the ast
    dict_representation = {}


    #Record metadata of the node
    node_type = node_in_ast.__class__.__name__
    if (node_type == 'ext'):
        print("STOP")
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
    for i in range(0, number_of_children):
        #for each child of the current node, find its length
        child_name_testing = node_in_ast.children()[i][0]
        child_node_testing = node_in_ast.children()[i][1]
        child_children_count = len(node_in_ast.children())
        x = 'stop'


        number_of_children_children = len(node_in_ast.children()[0][1].children())

    if number_of_children > 1:
        children = []
        child_name_original = node_in_ast.children()[0][0].split("[")[0]
        if child_name_original == 'ext':
            print("STOP HERE MATE")
        for i in range(0, number_of_children):
            child_name = node_in_ast.children()[i][0]
            child_name = child_name.split("[")[0]
            if child_name == 'ext':
                print("STOP HERE MATE")
            if child_name_original != child_name:
                if (len(children) == 1):
                    dict_representation[child_name_original] = children[0]
                else:
                    dict_representation[child_name_original] = children
                print(f"Found {child_name_original} in section where there should be 1 child (edge case though)")
                children = []

            child_dict = node_to_dict(node_in_ast.children()[i][1])
            children.append(child_dict)
            x= 'stop'
        if child_name == 'ext':
            print("STOP HERE MATE")
        if (len(children) == 1):
            dict_representation[child_name] = children[0]
        else:
            dict_representation[child_name] = children


        print(f"Found {child_name} in section where there should be 1 child")

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
                print(f"Found {child_name} in section where there should be >1 child")
                x = 'stop'

    # for child in node_in_ast.children():
    #     child_dict = node_to_dict(child)
    #     dict_representation[child.name] = child_dict

    for child_attr in get_child_attr(node_in_ast):
        if child_attr not in dict_representation:
            dict_representation[child_attr] = None
    return dict_representation


if __name__ == "__main__":
    ast = pycparser.parse_file('dummy.c')
    dictionary = node_to_dict(ast)
    print(json.dumps(dictionary, sort_keys=True, indent=4))
    balls = True