from fastapi import APIRouter,Depends
from helper import get_settings,Settings

data_app=APIRouter(
    prefix="/Fixflow-V1/data",
          tags=['data','V1'])


# Validate Question 