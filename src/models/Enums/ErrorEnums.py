from enum import Enum
class ErrorEnums(Enum):
    ERROR_UPLOAD="your error uploaded"
    ERROR_FAIL="Fail to upload your error"
    NOT_APPROVED_SIZE="The Text size is not approved"
    ERROR_VALIDATED="your error is approved"
    ERROR_CONTANT_NOT_APPROVED="the content not approved"
    ERROR_NOT_FOUND="this errors not found"
    ERROR_FOUND="the errors founded "
    CLUSTER_NOT_FOUNDED="cluster not founded"

    NO_EXTRAXTED_ERROR="no extracted errors"
    NO_MATCHED_ERROR="no matched error found"
    MATCHED_ERROR_FOUND="Matched error found"


class ErrorSource(Enum):
    STACK_OVERFLOW="stackoverflow"