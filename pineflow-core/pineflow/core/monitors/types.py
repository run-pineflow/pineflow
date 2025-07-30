from pydantic import BaseModel


class PayloadRecord(BaseModel):
    """Payload record."""

    input_text: str
    generated_text: str
    generated_token_count: int
    input_token_count: int
    response_time: int
