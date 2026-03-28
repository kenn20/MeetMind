import os
import railtracks as rt
from schemas.models import MeetingExtraction


def get_extraction_agent():
    key = os.getenv("DigitalOceanAPIKey")
    if not key:
        raise RuntimeError("ERROR: DigitalOceanAPIKey env var not set")
    llm = rt.llm.OpenAICompatibleProvider(
        "openai-gpt-oss-120b",
        api_base="https://inference.do-ai.run/v1/",
        api_key=key,
    )
    return rt.agent_node(
        name="Meeting Extraction Agent",
        llm=llm,
        system_message=(
            "You are a meeting analysis expert. Given a raw meeting transcript, "
            "extract structured information precisely. "
            "Map speaker labels (Speaker 1, Speaker 2, etc.) to likely real names if mentioned. "
            "Focus on concrete decisions and actionable items only. "
            "Ignore filler conversation."
        ),
        output_schema=MeetingExtraction,
    )
