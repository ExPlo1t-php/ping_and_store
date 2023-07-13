import os
import yaml

def ping_store(file, identifier): #takes one parameter "file" which is the source file of the data
    with open(file, "r+") as source:
        # loading content from the yaml file
        content = yaml.safe_load(source)
        # looping through the content of each dictionary entry
        id = 0
        for item in content:
            line = content[item]
            name = line["name"]
            type = line["type"]
            ip_address = line["ip_address"]
            response = os.popen(f"ping -n 2 -w 2000 {ip_address} ").read()
            with open("elements.yaml", "a+") as elements:
                # if the response message includes "request time out" or "unreachable"
                #  we give it a state of 0 otherwise we give it a state of 1
                # if("échec de la transmission" or "Hôte de destination inaccessible" or "TTL expiré" or "Délai d’attente de la demande dépassé.") in response:
                if("perte 100%") in response:
                    # construct payload and inserting it to elements.yaml file
                    payload = {f"{id}{identifier}":{"name":name, "type":type, "ip_address": ip_address, "state":0}}
                    yaml.safe_dump(payload, elements, sort_keys=False)
                    id+=1
                else:
                    payload = {f"{id}{identifier}":{"name":name, "type":type, "ip_address": ip_address, "state":1}}
                    yaml.safe_dump(payload, elements, sort_keys=False)
                    id+=1

def clear_file(file_path):
    with open(file_path, "w") as file:
        file.truncate()