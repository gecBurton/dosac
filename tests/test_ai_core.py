from langchain_core.messages import AIMessage

from core.ai_core import to_json


def test_to_json():
    messages = {
        "messages": [AIMessage(content="hello")],
        "user_id": "1",
        "another_thing": 2,
    }
    expected = {
        "messages": [
            {
                "additional_kwargs": {},
                "content": "hello",
                "example": False,
                "id": None,
                "invalid_tool_calls": [],
                "name": None,
                "response_metadata": {},
                "tool_calls": [],
                "type": "ai",
                "usage_metadata": None,
            }
        ],
        "another_thing": 2,
    }
    assert to_json(messages) == expected
