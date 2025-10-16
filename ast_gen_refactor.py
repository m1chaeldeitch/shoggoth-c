# Serialization refactor
# The idea is to be able to do the following transformations:
#       File (C) ->  AST
#       AST      ->  Dict
#       Dict     ->  JSON
# And the reverse order ( JSON -> Dict -> AST)

import pycparser




'''Returns a JSON representation of the C source file'''
def file_to_json(file_name):
    return "Coming soon..."



'''Returns an AST representation of a C source file'''
def file_to_ast(file_name):
    return pycparser.parse_file(file_name)


'''Returns a dictionary representation of the AST
   Needed because json library can directly turn a dict to json format'''
def node_to_dict(node_in_ast):
    return "Coming soon..."
