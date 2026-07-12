from fastapi import APIRouter,Depends,status
from fastapi.responses import JSONResponse
from helper import get_settings,Settings
from controllers.DataController import DataController
from controllers.ProcessController import ProcessController
from .schema.ErrorRequest import UserQueryRequest


data_app=APIRouter(
    prefix="/Fixflow-V1/data",
          tags=['data','V1'])


# upload user query

@data_app.post("/upload/{error_id}")
def upload_error_data(error_id: str, error: UserQueryRequest):
    query=error.query
    data_controller = DataController()

    is_valid, signal = data_controller.validate_error(query)

    if not is_valid:
        return JSONResponse(
            status_code=status.HTTP_400_BAD_REQUEST,
            content={
                "result": signal
            }
        )

    return JSONResponse(
        content={
            "result": signal,
            "error": query
        }
    )
@data_app.post("/process/")
def process_error_data(user_request: UserQueryRequest):
    process_controller=ProcessController()
    return  process_controller.process_new_error(user_request)
    


    