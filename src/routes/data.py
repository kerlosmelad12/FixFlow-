from fastapi import APIRouter,Depends,status,Request
from fastapi.responses import JSONResponse
from helper import get_settings,Settings
from controllers.DataController import DataController
from controllers.ProcessController import ProcessController
from controllers.ProcessController import ProcessController
from .schema.ErrorRequest import UserQueryRequest
from models.DB_Schema.ProcessingJob import ProcessingJob
from models.DB_Schema.ErrorMessage import ErrorMessage
from models.ErrorQueryModel import ErrorQueryModel
from models.JobProcessingModel import JobProcessingModel
from models.Enums.ErrorEnums import ErrorEnums

data_app=APIRouter(
    prefix="/Fixflow-V1/data",
          tags=['data','V1'])


# upload user query

@data_app.post("/upload/")
async def upload_error_data(res:Request, error: UserQueryRequest,app_setting=Depends(get_settings)):
    query=error.query
    data_controller = DataController()
    process_controller=ProcessController()
    error_model=ErrorQueryModel(res.app.db_client)
    job_model=JobProcessingModel(res.app.db_client)

    is_valid, signal = data_controller.validate_error(query)

    if not is_valid:
        return JSONResponse(
            status_code=status.HTTP_400_BAD_REQUEST,
            content={
                "result": signal
            }
        )
    
    clean_text=process_controller.clean_text(query)
    extracted_error=process_controller.extract_error_data(clean_text,res.app.llm)
    extracted_data = extracted_error.get('error')

    if not extracted_error or not extracted_error.get('success'):
        return JSONResponse(
        status_code=status.HTTP_400_BAD_REQUEST,
        content={
            "result": ErrorEnums.NO_EXTRAXTED_ERROR.value
        }
    )

    extracted_data = extracted_error.get('data')

    if not extracted_data:
        return JSONResponse(
        status_code=status.HTTP_400_BAD_REQUEST,
        content={
            "result": ErrorEnums.NO_EXTRAXTED_ERROR.value,
            "debug": extracted_error  # remove/log instead of returning this in production
        }
    )

    extracted_tags = extracted_data.get('tags')
    error_type = extracted_data.get('error_type')
    error_title = extracted_data.get('error_title')
    error_signature = extracted_data.get('error_signature')

    if not all([extracted_tags, error_type, error_title, error_signature]):
        return JSONResponse(
        status_code=status.HTTP_400_BAD_REQUEST,
        content={
            "result": ErrorEnums.NO_EXTRAXTED_ERROR.value
        }
    )
    error_id=DataController.generate_error_id(error_title=error_title,cleaned_text=clean_text )

    

    error=ErrorMessage(error_id=error_id,
                raw_extracted_tags=extracted_tags,
                error_type=error_type,
                error_title=error_title,
                 error_text=query,
                  error_signature= error_signature)
    
    inserted_error=await error_model.insert_error(error)


    job = ProcessingJob(
        error_message_id=inserted_error.id,
        error=query
        )
    job=await job_model.create_job(job)

    return JSONResponse(
        content={
            "result": signal,
            "error": extracted_error,
            "job_id":str(job.id)
        }
    )
@data_app.post("/process/")
def process_error_data(user_request: UserQueryRequest):
    process_controller=ProcessController()
    return  process_controller.process_new_error(user_request)
    


    