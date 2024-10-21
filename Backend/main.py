import os
from fastapi import FastAPI
import requests
import base64
from dotenv import load_dotenv, dotenv_values 
from fastapi import HTTPException
from fastapi.middleware.cors import CORSMiddleware


load_dotenv() 

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=['*']
)

def authorize_account(applicationKeyId : str,applicationKey : str):
    url = "https://api.backblazeb2.com/b2api/v3/b2_authorize_account"

    payload = ""

    auth_string = f"{applicationKeyId}:{applicationKey}"
    auth_encoded = base64.b64encode(auth_string.encode()).decode()

    headers = {
    'Authorization': f'Basic {auth_encoded}'
    }

    response = requests.request("GET", url, headers=headers, data=payload)

    try:
        response_data = response.json()  # Ensure it's parsed as JSON
    except ValueError:
        print("Failed to parse response as JSON")
        return
    
    result = {
        "apiUrl":  response_data["apiInfo"]["storageApi"]["apiUrl"],
        "bucketId": response_data["apiInfo"]["storageApi"]["bucketId"],
        "authorizationToken": response_data["authorizationToken"]
    }

    return result


@app.get("/get_upload_url")
def get_upload_url():

    application_key_id = os.getenv("applicationKeyId")
    application_key = os.getenv("applicationKey")

    # Check if environment variables are set
    if not application_key_id or not application_key:
        raise HTTPException(status_code=400, detail="Missing applicationKeyId or applicationKey in environment variables")

    try:
        # Call the authorize_account function to get authorization data
        authorize_data = authorize_account(application_key_id, application_key)

        # Validate the expected keys are present in authorize_data
        if "authorizationToken" not in authorize_data or "apiUrl" not in authorize_data:
            raise HTTPException(status_code=500, detail="Authorization data is missing required fields")
        
    except requests.exceptions.RequestException as e:
        raise HTTPException(status_code=502, detail=f"Failed to communicate with the authorization API: {str(e)}")


    url = f"{authorize_data['apiUrl']}/b2api/v3/b2_get_upload_url?bucketId={authorize_data['bucketId']}"
    payload = {}
    headers = {
    'Authorization': f'{authorize_data["authorizationToken"]}'
    }
    upload_response = requests.get(url, headers=headers)

    if upload_response.status_code == 200:
        upload_data = upload_response.json()
        return {"uploadUrl": upload_data["uploadUrl"],
                "authorizationToken" : upload_data["authorizationToken"]}
    else:
        return {"error": "Failed to get upload URL", "details": upload_response.text}
