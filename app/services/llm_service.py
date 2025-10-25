import json
import logging
from pathlib import Path
from openai import AsyncOpenAI
from app.core.config import settings
from app.core.models import MatchResult, CriteriaScores

logger = logging.getLogger(__name__)


def load_prompt(filename: str) -> str:
    """Load prompt from file"""
    prompt_path = Path(__file__).parent.parent / "prompts" / filename
    return prompt_path.read_text()


class LLMService:
    def __init__(self):
        self.client = AsyncOpenAI(api_key=settings.openai_api_key)
        self.model = settings.openai_model

    async def _call_openai(self, prompt: str) -> str:
        """Call OpenAI API"""
        try:
            response = await self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "user", "content": prompt}
                ],
                temperature=0.3,
                max_tokens=2000
            )
            return response.choices[0].message.content
        except Exception as e:
            logger.error(f"Error calling OpenAI: {e}")
            raise

    async def match_cv_job(self, cv_text: str, job_text: str) -> MatchResult:
        """
        Match CV against job description using LLM.
        All scoring and evaluation is done by the LLM via prompts.
        """
        # Load prompt template
        prompt_template = load_prompt("match_prompt.txt")

        # Format prompt with CV and job text
        prompt = prompt_template.format(cv_text=cv_text, job_text=job_text)

        try:
            response = await self._call_openai(prompt)

            # Clean response to extract JSON
            response = response.strip()
            if response.startswith("```json"):
                response = response[7:]
            if response.startswith("```"):
                response = response[3:]
            if response.endswith("```"):
                response = response[:-3]
            response = response.strip()

            data = json.loads(response)

            # Validate and create MatchResult
            criteria_scores = CriteriaScores(**data['criteria_scores'])
            return MatchResult(
                match=data['match'],
                overall_score=data['overall_score'],
                criteria_scores=criteria_scores,
                explanation=data['explanation']
            )

        except Exception as e:
            logger.error(f"Error in LLM matching: {e}")
            # Return error result (will not be cached)
            return MatchResult(
                match=False,
                overall_score=0,
                criteria_scores=CriteriaScores(
                    skills=0,
                    experience=0,
                    location=0,
                    education=0,
                    certifications=0
                ),
                explanation=f"Error processing match: {str(e)}",
                error=True
            )

    async def health_check(self) -> bool:
        """Check if OpenAI is available"""
        try:
            await self.client.models.list()
            return True
        except Exception:
            return False
