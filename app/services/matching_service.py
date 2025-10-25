import time
import logging
from app.core.models import MatchResult
from app.data.database import db
from app.services.cv_parser import parse_file
from app.services.llm_service import LLMService

logger = logging.getLogger(__name__)


class MatchingService:
    def __init__(self):
        self.llm_service = LLMService()

    async def match_cv_job(
        self,
        cv_file_content: bytes,
        cv_file_type: str,
        job_file_content: bytes,
        job_file_type: str
    ) -> MatchResult:
        """Match CV against job description using LLM"""
        start_time = time.time()

        # Parse files to extract text
        cv_text = parse_file(cv_file_content, cv_file_type)
        job_text = parse_file(job_file_content, job_file_type)

        # Check if match is cached
        cached_match = db.get_match(cv_text, job_text)
        if cached_match:
            logger.info("Returning cached match result")
            cached_match.cached = True
            cached_match.processing_time_ms = int(
                (time.time() - start_time) * 1000)
            return cached_match

        # Use LLM to match CV against job
        logger.info("Using LLM to match CV against job")
        match_result = await self.llm_service.match_cv_job(cv_text, job_text)

        # Add processing time
        match_result.processing_time_ms = int(
            (time.time() - start_time) * 1000)

        # Only cache successful results (not errors)
        if not match_result.error:
            db.cache_match(cv_text, job_text, match_result)
        else:
            logger.warning("Not caching error result")

        return match_result
