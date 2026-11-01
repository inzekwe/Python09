"""Validate nested crew and mission data before launch approval."""

from __future__ import annotations

from datetime import datetime
from enum import Enum

from pydantic import BaseModel, Field, ValidationError, model_validator


class Rank(str, Enum):
    """Ranks recognized by the mission crew system."""

    CADET = "cadet"
    OFFICER = "officer"
    LIEUTENANT = "lieutenant"
    CAPTAIN = "captain"
    COMMANDER = "commander"


class CrewMember(BaseModel):
    """Validated details for one member of a space mission."""

    member_id: str = Field(min_length=3, max_length=10)
    name: str = Field(min_length=2, max_length=50)
    rank: Rank
    age: int = Field(ge=18, le=80)
    specialization: str = Field(min_length=3, max_length=30)
    years_experience: int = Field(ge=0, le=50)
    is_active: bool = True


class SpaceMission(BaseModel):
    """A mission with nested, validated crew and launch requirements."""

    mission_id: str = Field(min_length=5, max_length=15)
    mission_name: str = Field(min_length=3, max_length=100)
    destination: str = Field(min_length=3, max_length=50)
    launch_date: datetime
    duration_days: int = Field(ge=1, le=3650)
    crew: list[CrewMember] = Field(min_length=1, max_length=12)
    mission_status: str = "planned"
    budget_millions: float = Field(ge=1.0, le=10000.0)

    @model_validator(mode="after")
    def validate_mission_rules(self) -> SpaceMission:
        """Apply launch safety rules across the mission and its crew."""
        if not self.mission_id.startswith("M"):
            raise ValueError('Mission ID must start with "M"')

        has_lead = any(
            member.rank in (Rank.COMMANDER, Rank.CAPTAIN)
            for member in self.crew
        )
        if not has_lead:
            raise ValueError(
                "Mission must have at least one Commander or Captain"
            )

        if self.duration_days > 365:
            experienced_count = sum(
                member.years_experience >= 5 for member in self.crew
            )
            minimum_experienced = (len(self.crew) + 1) // 2
            if experienced_count < minimum_experienced:
                raise ValueError(
                    "Long missions require at least 50% experienced crew "
                    "(5+ years)"
                )

        if any(not member.is_active for member in self.crew):
            raise ValueError("All crew members must be active")
        return self


def main() -> None:
    """Show one launch-ready mission and one unsafe crew report."""
    print("Space Mission Crew Validation")
    print("=" * 41)

    mission = SpaceMission.model_validate(
        {
            "mission_id": "M2024_MARS",
            "mission_name": "Mars Colony Establishment",
            "destination": "Mars",
            "launch_date": "2024-06-15T08:00:00",
            "duration_days": 900,
            "crew": [
                {
                    "member_id": "CM001",
                    "name": "Sarah Connor",
                    "rank": "commander",
                    "age": 42,
                    "specialization": "Mission Command",
                    "years_experience": 15,
                },
                {
                    "member_id": "CM002",
                    "name": "John Smith",
                    "rank": "lieutenant",
                    "age": 35,
                    "specialization": "Navigation",
                    "years_experience": 8,
                },
                {
                    "member_id": "CM003",
                    "name": "Alice Johnson",
                    "rank": "officer",
                    "age": 29,
                    "specialization": "Engineering",
                    "years_experience": 4,
                },
            ],
            "budget_millions": 2500.0,
        }
    )
    print("Valid mission created:")
    print(f"Mission: {mission.mission_name}")
    print(f"ID: {mission.mission_id}")
    print(f"Destination: {mission.destination}")
    print(f"Duration: {mission.duration_days} days")
    print(f"Budget: ${mission.budget_millions}M")
    print(f"Crew size: {len(mission.crew)}")
    print("Crew members:")
    for member in mission.crew:
        print(
            f"- {member.name} ({member.rank.value}) - "
            f"{member.specialization}"
        )
    print("=" * 41)

    try:
        SpaceMission.model_validate(
            {
                "mission_id": "M2024_TEST",
                "mission_name": "Unapproved Deep Space Mission",
                "destination": "Deep Space",
                "launch_date": datetime(2024, 6, 15, 8),
                "duration_days": 120,
                "crew": [
                    {
                        "member_id": "CM101",
                        "name": "Jamie Brown",
                        "rank": "lieutenant",
                        "age": 31,
                        "specialization": "Navigation",
                        "years_experience": 7,
                    }
                ],
                "budget_millions": 500.0,
            }
        )
    except ValidationError as error:
        print("Expected validation error:")
        print(error.errors()[0]["msg"])


if __name__ == "__main__":
    main()
