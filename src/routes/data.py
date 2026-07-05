from fastapi import APIRouter,Depends,status
from fastapi.responses import JSONResponse
from helper import get_settings,Settings
from controllers import DataController
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