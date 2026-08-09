from fastapi import APIRouter,Depends,status,Request
from fastapi.responses import JSONResponse

nlp_app=APIRouter(
     prefix="/Fixflow-V1/nlp",
              tags=['nlp','V1']
)

@nlp_app.get("/similar/{error_id}")

async def get_similer_errors(error_id:str,res:Request):
    pass
    


