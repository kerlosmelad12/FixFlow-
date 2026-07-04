from fastapi import APIRouter,Depends
from helper import get_settings,Settings


base_app=APIRouter(
    prefix="/Fixflow-V1",
          tags=['Base','V1'])

@base_app.get('/')
async def welcome(app_setting=Depends(get_settings)):
    app_name=app_setting.APP_NAME
    app_version=app_setting.APP_VERSION
    return {
        "message":"Welcome to your errors solver app",
            "App_name":app_name,
            "App_version":app_version
            }

