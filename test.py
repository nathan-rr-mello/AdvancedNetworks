import sys
import datetime
import socket
import os
import json

oids2objects = {
    ".1.3.6.1.3.1234.1.1.0": "tModelName",
    ".1.3.6.1.3.1234.1.2.0": "tManDate",
    ".1.3.6.1.3.1234.1.3.0": "tACTemp",
    ".1.3.6.1.3.1234.1.4.0": "tBatteryPercentage",
    ".1.3.6.1.3.1234.1.5.0": "tHP",
    ".1.3.6.1.3.1234.1.6.0": "tMaxSpeed",
    ".1.3.6.1.3.1234.1.7.0": "tInterLigths",
    ".1.3.6.1.3.1234.1.8.1.1.1": "tDoorIndex1",
    ".1.3.6.1.3.1234.1.8.1.1.2": "tDoorIndex2",
    ".1.3.6.1.3.1234.1.8.1.1.3": "tDoorIndex3",
    ".1.3.6.1.3.1234.1.8.1.1.4": "tDoorIndex4",
    ".1.3.6.1.3.1234.1.8.1.2.1": "tDoorStatus1",
    ".1.3.6.1.3.1234.1.8.1.2.2": "tDoorStatus2",
    ".1.3.6.1.3.1234.1.8.1.2.3": "tDoorStatus3",
    ".1.3.6.1.3.1234.1.8.1.2.4": "tDoorStatus4",
    ".1.3.6.1.3.1234.1.8.1.3.1": "tDoorWindow1",
    ".1.3.6.1.3.1234.1.8.1.3.2": "tDoorWindow2",
    ".1.3.6.1.3.1234.1.8.1.3.3": "tDoorWindow3",
    ".1.3.6.1.3.1234.1.8.1.3.4": "tDoorWindow4"
}

settable_objects =  {   
    ".1.3.6.1.3.1234.1.3.0": "tACTemp",
    ".1.3.6.1.3.1234.1.7.0": "tInterLigths",
    ".1.3.6.1.3.1234.1.8.1.2.1": "tDoorStatus1",
    ".1.3.6.1.3.1234.1.8.1.2.2": "tDoorStatus2",
    ".1.3.6.1.3.1234.1.8.1.2.3": "tDoorStatus3",
    ".1.3.6.1.3.1234.1.8.1.2.4": "tDoorStatus4",
}

def get_snmp_type(var) -> str:
    if type(var) == str:
        return "string"
    elif type(var) == int:
        return "integer"
    else:
        return "<unknown>"
    
def load_objects(file_path):
    if os.path.exists(file_path):
        with open(file_path, 'r') as file:
            return json.load(file)
    else:
        raise FileNotFoundError(f"Arquivo {file_path} não encontrado.")

def save_objects(file_path, objects):
    with open(file_path, 'w') as file:
        json.dump(objects, file)

def get_object(objects, oid):
    field = oids2objects[oid]
    value = objects[field]
    return value

def set_object(objects, oid, value):
    with open("/tmp/objects.json", "w") as file:
        field = settable_objects[oid]
        objects[field] = value
        json.dump(objects, file)

def main():


    file_path = "/tmp/objects.json"
    try:
        objects = load_objects(file_path)
    except FileNotFoundError as e:
        print(str(e))
        return

    #print(objects)

    with open("/tmp/agent.log", 'a') as file:
        file.write(' '.join(sys.argv) + '\n')

    if len(sys.argv) < 3:
        print("Usage: agent.py <request-type> <MIB-oid> [type] [<new-value>]")
        return

    request_type = sys.argv[1]
    oid = sys.argv[2]

    #print(oid)

    if request_type == "-g":  # GET request
        if oid in oids2objects:
            obj = get_object(objects, oid)
            print(oid)
            print(get_snmp_type(obj))
            print(obj)
        else:
            print("NONE")
            
    elif request_type == "-s":  # SET request
        if oid in settable_objects and len(sys.argv) == 5:
            content_type = sys.argv[3]
            new_content = sys.argv[4]
            if content_type == "i":
                new_content = int(new_content)
            elif content_type == "s":
                new_content = str(new_content)
            set_object(objects, oid, new_content)
            print(oid)
            print(get_snmp_type(new_content))
            print(new_content)
        elif oid in oids2objects:
            obj = get_object(objects, oid)
            print(oid)
            print(get_snmp_type(obj))
            print(obj)
        else:
            print("NONE")

    elif request_type == "-n": #GETNEXT request
        keys = list(oids2objects.keys())
        if oid in oids2objects:
            idx = keys.index(oid) + 1
            if idx < len(keys):
                next_oid = keys[idx]
                obj = get_object(objects, next_oid)
                print(next_oid)
                print(get_snmp_type(obj))
                print(obj)
            else:
                print("NONE")
        else:
            found = False
            for key in keys:
                if oid in key:
                    found = True
                    obj = get_object(objects, key)
                    print(key)
                    print(get_snmp_type(obj))
                    print(obj)
                    break
            if not found:
                print("NONE")
        

if __name__ == "__main__":
    main()