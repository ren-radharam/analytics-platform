from typing import Any

from pydantic import BaseModel, ConfigDict, Field, UUID4


class WidgetCreate(BaseModel):
    title: str
    widget_type: str
    config: dict[str, Any] = Field(default_factory=dict)
    position: dict[str, Any] = Field(
        default_factory=lambda: {"x": 0, "y": 0, "w": 6, "h": 4},
    )
    query_config: dict[str, Any] = Field(default_factory=dict)


class DashboardCreate(BaseModel):
    name: str
    description: str | None = None
    is_public: bool = False


class DashboardOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID4
    name: str
    description: str | None
    is_public: bool
    org_id: UUID4


class WidgetOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID4
    title: str
    widget_type: str
    config: dict[str, Any]
    position: dict[str, Any]
    query_config: dict[str, Any]
    dashboard_id: UUID4
