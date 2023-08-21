import base64
from datetime import datetime
import hmac
import hashlib
import json
import os
import pprint
import requests
from requests import Request, Session

ces_api_url_base = 'https://ecsvapor.autodesk.com:8080/api/2.0/'

#from ecsvapor user profile, thes keys are for PDG SCM CICD account
#to run this script locally these env variables are needed, keys are available from keeper
ecs_access_key = "Ypd3yU6inRlAIel23EZH5p6C1QS2W5utkCb8GMxsLDwfJfxetzYOV9FrayktuhIAvBFBPQRmG7RTqggpqGhTUQ" # "PDG SCM CICD" account
ecs_secret_key = "f32EqlGTY9FYujYVJmQ8pMwSgRT1HDBzT2ZyJ0FnUe-MXqG9R_Dyc16fqK2CYQWZRuU1tWtLBAdG0__Da5nqKg" # "PDG SCM CICD" account

timeout_period =100 #rest API timeout after 10 sec

def get_utc_8601_now_time_str():
    return datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%SZ")


def generate_ecs_signature(ecs_api_url, ecs_secret_key):
    utc_signed_time = get_utc_8601_now_time_str()
    key = ecs_secret_key + utc_signed_time
    data = ecs_api_url.lower()
    new_hash = hmac.new(key.encode("ascii"), data.encode("ascii"), hashlib.sha1).digest()
    signature = base64.b64encode(new_hash).decode("ascii").rstrip("\n")
    return utc_signed_time, signature


def print_response(response):
    d = response.content
    data = json.loads(d.decode("utf-8"))
    pprint.pprint(data)
    return data["RequestId"]



# get_ecs_instance_by_path("3da8b4f2-e70e-49c9-b3e9-fcec962f804d")
def get_ecs_instance_by_path( instanceId ):
    ecs_api_url = f"{ces_api_url_base}{'GetInstances/'}{instanceId}"

    utc_signed_time, ecs_signature = generate_ecs_signature(ecs_api_url, ecs_secret_key)
    headers =  {
    "AccessKey": ecs_access_key,
    "Signature": ecs_signature,
    "TimeStamp": utc_signed_time,
    "Accept": "application/json"
    }

    p = Request('Get',ecs_api_url, headers=headers).prepare()
    print( 'Rest API headers:', p.headers)
    print( 'Rest API url:', p.url)
    response = Session().send(p)
    
    return print_response( response)



def get_signalR_event( requestId ):
    ecs_api_url = f"{ces_api_url_base}{'GetSignalrEvents?requestId='}{requestId}{'&admin-call=true'}"

    #headers = generate_headers( ecs_api_url)
    utc_signed_time, ecs_signature = generate_ecs_signature(ecs_api_url, ecs_secret_key)
    headers =  {
    "AccessKey": ecs_access_key,
    "Signature": ecs_signature,
    "TimeStamp": utc_signed_time,
    "Accept": "application/json"
    }

    p = Request('Get',ecs_api_url, headers=headers).prepare()
    print( 'Rest API headers:', p.headers)
    print( 'Rest API url:', p.url)
    response = Session().send(p)
    print_response( response)


def main():
    #test if API works
    request_id = get_ecs_instance_by_path("3da8b4f2-e70e-49c9-b3e9-fcec962f804d")
    print("requestID = ", request_id)
    get_signalR_event( request_id )


if __name__=="__main__":
    main()
