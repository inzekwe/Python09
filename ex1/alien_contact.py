"""Validate alien contact logs and their business rules."""

from __future__ import annotations

from datetime import datetime
from enum import Enum

from pydantic import BaseModel, Field, ValidationError, model_validator


class ContactType(str, Enum):
    """Supported forms of reported alien contact."""

    RADIO = "radio"
    VISUAL = "visual"
    PHYSICAL = "physical"
    TELEPATHIC = "telepathic"


class AlienContact(BaseModel):
    """An alien contact report with field and cross-field validation."""

    contact_id: str = Field(min_length=5, max_length=15)
    timestamp: datetime
    location: str = Field(min_length=3, max_length=100)
    contact_type: ContactType
    signal_strength: float = Field(ge=0.0, le=10.0)
    duration_minutes: int = Field(ge=1, le=1440)
    witness_count: int = Field(ge=1, le=100)
    message_received: str | None = Field(default=None, max_length=500)
    is_verified: bool = False

    @model_validator(mode="after")
    def validate_contact_rules(self) -> AlienContact:
        """Apply rules that depend on multiple fields in the report."""
        if not self.contact_id.startswith("AC"):
            raise ValueError('Contact ID must start with "AC"')
        if (
            self.contact_type is ContactType.PHYSICAL
            and not self.is_verified
        ):
            raise ValueError("Physical contact reports must be verified")
        if (
            self.contact_type is ContactType.TELEPATHIC
            and self.witness_count < 3
        ):
            raise ValueError(
                "Telepathic contact requires at least 3 witnesses"
            )
        if self.signal_strength > 7.0 and not self.message_received:
            raise ValueError(
                "Strong signals must include a received message"
            )
        return self


def main() -> None:
    """Show a valid report and a cross-field validation failure."""
    print("Alien Contact Log Validation")
    print("=" * 38)

    report = AlienContact.model_validate(
        {
            "contact_id": "AC_2024_001",
            "timestamp": "2024-01-15T14:30:00",
            "location": "Area 51, Nevada",
            "contact_type": "radio",
            "signal_strength": 8.5,
            "duration_minutes": 45,
            "witness_count": 5,
            "message_received": "Greetings from Zeta Reticuli",
        }
    )
    print("Valid contact report:")
    print(f"ID: {report.contact_id}")
    print(f"Type: {report.contact_type.value}")
    print(f"Location: {report.location}")
    print(f"Signal: {report.signal_strength}/10")
    print(f"Duration: {report.duration_minutes} minutes")
    print(f"Witnesses: {report.witness_count}")
    print(f"Message: '{report.message_received}'")
    print("=" * 38)

    try:
        AlienContact.model_validate(
            {
                "contact_id": "AC_2024_002",
                "timestamp": datetime(2024, 1, 16, 9, 15),
                "location": "Roswell, New Mexico",
                "contact_type": ContactType.TELEPATHIC,
                "signal_strength": 6.2,
                "duration_minutes": 30,
                "witness_count": 1,
            }
        )
    except ValidationError as error:
        print("Expected validation error:")
        print(error.errors()[0]["msg"])


if __name__ == "__main__":
    main()
