import importlib
import json
import keyword
import sys


class ObjSpecification:
    AS_OBJECT   = '__is-obj'
    OBJ_NAME     = 'obj-name'
    CALL_OR_INIT = 'init/call'
    OBJ_ARGS     = 'args'
    OBJ_KWARGS   = 'kwargs'
    PACKAGE      = 'package'


def create_object(obj_desc):
    """ Create objects from dict in appropriate format
    obj_desc: object description
    Given dict in format:
        {
            AS_OBJECT:    true
            OBJ_NAME:     Name of object.
            CALL_OR_INIT: true if object should be called during processing.
            OBJ_ARGS:     args passed to object call or init.       (Optional)
            OBJ_KWARGS:   kwargs passed to object call or init.     (Optional)
            PACKAGE:      Package for object to be imported from
                          this key should be omitted if object is builtin (Optional for builtins)
        }
    Keys format is presented in ObjSpecification.
    """

    obj_name = obj_desc[ObjSpecification.OBJ_NAME]
    args = obj_desc.get(ObjSpecification.OBJ_ARGS, list())
    kwargs = obj_desc.get(ObjSpecification.OBJ_KWARGS, dict())

    if ObjSpecification.PACKAGE in obj_desc:
        obj = getattr(importlib.import_module(obj_desc[ObjSpecification.PACKAGE]), obj_name)
    else:
        obj = getattr(sys.modules['builtins'], obj_name)
    
    if obj_desc[ObjSpecification.CALL_OR_INIT]:
        return obj(*args, **kwargs)
    else:
        return obj


def process_object(obj):
    """ Recursively process object loaded from json
    When the dict in appropriate(*) format is found,
    make object from it.
    (*) appropriate is defined in create_object function docstring.
    """

    if isinstance(obj, list):
        result_obj = []
        for elem in obj:
            result_obj.append(process_object(elem))
        return result_obj
    elif isinstance(obj, dict):
        processed_obj = {}
        for key in obj.keys():
            processed_obj[key] = process_object(obj[key])
        
        as_obj = obj.get(ObjSpecification.AS_OBJECT, False)
        if as_obj:
            result_obj = create_object(processed_obj)
        else:
            result_obj = processed_obj
        return result_obj
    else:
        return obj


def import_config_from_json(filename: str):
    with open(filename, 'r') as f:
        o = json.load(f)
    return process_object(o)


if __name__ == '__main__':
    print(import_config_from_json('config.json'))

