from fastapi import APIRouter, UploadFile, File, HTTPException
import logging
from app.services.matching_service import MatchingService

logger = logging.getLogger(__name__)

router = APIRouter()
matching_service = MatchingService()


@router.post("/match")
async def match_cv_job(
    cv: UploadFile = File(...),
    job_description: UploadFile = File(...)
):
    """
    Match a CV against a job description using LLM.
    """
    try:
        # Read file contents
        cv_content = await cv.read()
        job_content = await job_description.read()

        # Validate file types
        if not cv.filename and not cv.content_type:
            raise HTTPException(status_code=400, detail="CV file is required")

        if not job_description.filename and not job_description.content_type:
            raise HTTPException(
                status_code=400, detail="Job description file is required")

        # Perform matching
        result = await matching_service.match_cv_job(
            cv_content,
            cv.content_type or cv.filename,
            job_content,
            job_description.content_type or job_description.filename
        )

        return result.model_dump()

    except ValueError as e:
        logger.error(f"Value error: {e}")
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Error matching CV: {e}")
        raise HTTPException(
            status_code=500, detail=f"Internal server error: {str(e)}")


@router.get("/health")
async def health_check():
    """Health check endpoint"""
    llm_available = await matching_service.llm_service.health_check()

    return {
        "status": "healthy" if llm_available else "degraded",
        "llm_available": llm_available
    }
