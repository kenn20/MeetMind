import sys
import os

sys.path.insert(0, os.path.dirname(__file__))

from dotenv import load_dotenv

load_dotenv(os.path.join(os.path.dirname(__file__), "..", ".env"))

import railtracks as rt
from agents.transcription import transcribe_meeting
from agents.extraction import get_extraction_agent
from agents.personas import (
    make_persona_agent,
    ENGINEER_PROMPT,
    DESIGNER_PROMPT,
    PM_PROMPT,
)
from tools.senso_tools import ingest_to_senso, search_senso
from tools.git_tools import git_tools


@rt.function_node
async def meetmind_flow(
    file_path: str,
    meeting_title: str,
    engineer_name: str,
    designer_name: str,
    pm_name: str,
    project_name: str,
):
    """Run the full MeetMind pipeline for a meeting recording.

    Args:
        file_path (str): Path to audio/video file
        meeting_title (str): Human-readable meeting title
        engineer_name (str): Name of the software engineer attendee
        designer_name (str): Name of the UX designer attendee
        pm_name (str): Name of the product manager attendee
        project_name (str): Project name as listed in repos.txt
    """
    transcript = await rt.call(transcribe_meeting, file_path)

    await rt.call(
        ingest_to_senso,
        title=meeting_title,
        summary="Auto-ingested meeting transcript",
        text=transcript,
    )

    ExtractionAgent = get_extraction_agent()
    extraction_result = await rt.call(ExtractionAgent, transcript)
    extraction_str = (
        extraction_result.model_dump_json()
        if hasattr(extraction_result, "model_dump_json")
        else str(extraction_result)
    )

    persona_tools = [*git_tools, search_senso]

    eng_agent = make_persona_agent("Engineer", ENGINEER_PROMPT, persona_tools)
    des_agent = make_persona_agent("Designer", DESIGNER_PROMPT, persona_tools)
    pm_agent = make_persona_agent("PM", PM_PROMPT, persona_tools)

    eng_input = f"Raw transcript:\n{transcript}\n\nExtracted data:\n{extraction_str}\n\nUser: {engineer_name} (Software Engineer)\nProject: {project_name}"
    des_input = f"Raw transcript:\n{transcript}\n\nExtracted data:\n{extraction_str}\n\nUser: {designer_name} (UX Designer)\nProject: {project_name}"
    pm_input = f"Raw transcript:\n{transcript}\n\nExtracted data:\n{extraction_str}\n\nUser: {pm_name} (Product Manager)\nProject: {project_name}"

    eng_result = await rt.call(eng_agent, eng_input)
    des_result = await rt.call(des_agent, des_input)
    pm_result = await rt.call(pm_agent, pm_input)

    def extract_content(r):
        if hasattr(r, "content"):
            return r.content
        return str(r)

    return {
        "transcript": transcript,
        "extraction": extraction_str,
        "engineer": extract_content(eng_result),
        "designer": extract_content(des_result),
        "pm": extract_content(pm_result),
    }


flow = rt.Flow("MeetMind", entry_point=meetmind_flow)

if __name__ == "__main__":
    result = flow.invoke(
        file_path=sys.argv[1] if len(sys.argv) > 1 else "test_audio.mp3",
        meeting_title="Test Sprint Planning",
        engineer_name="Marcus",
        designer_name="Priya",
        pm_name="Sarah",
        project_name="meetmind",
    )
    print("=== ENGINEER ===")
    print(result["engineer"])
    print("\n=== DESIGNER ===")
    print(result["designer"])
    print("\n=== PM ===")
    print(result["pm"])
