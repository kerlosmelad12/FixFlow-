from fastapi import APIRouter,Depends,status,Request
from fastapi.responses import JSONResponse
from helper import get_settings,Settings
from controllers.DataController import DataController
from controllers.ProcessController import ProcessController
from controllers.ProcessController import ProcessController
from .schema.ErrorRequest import UserQueryRequest
from models.DB_Schema.ProcessingJob import ProcessingJob
 


data_app=APIRouter(
    prefix="/Fixflow-V1/data",
          tags=['data','V1'])


# upload user query

@data_app.post("/upload/")
async def upload_error_data(res:Request, error: UserQueryRequest,app_setting=Depends(get_settings)):
    query=error.query
    data_controller = DataController()
    process_controller=ProcessController()

    is_valid, signal = data_controller.validate_error(query)

    if not is_valid:
        return JSONResponse(
            status_code=status.HTTP_400_BAD_REQUEST,
            content={
                "result": signal
            }
        )
    clean=process_controller.clean_text(query)
    extracted_error=process_controller.extract_error_data(clean,res.app.llm)



    return JSONResponse(
        content={
            "result": signal,
            "error": extracted_error
        }
    )
@data_app.post("/process/")
def process_error_data(user_request: UserQueryRequest):
    process_controller=ProcessController()
    return  process_controller.process_new_error(user_request)
    


    