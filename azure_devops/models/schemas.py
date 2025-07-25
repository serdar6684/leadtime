"""Pydantic models for validating Azure DevOps service connection payloads."""

from typing import Optional
from pydantic import BaseModel, Field, model_validator
import config

class GetDefinitionId(BaseModel):
    """Model for retrieving a definition ID."""
    project_id: str = Field(..., description="The id of the Azure DevOps project.")
    stage_name: str = Field(..., description="The name of the pipeline stage.")

    @model_validator(mode='before')
    def validate_project(cls, values):
        """Ensure the project name is not empty."""
        if not values.get('project'):
            raise ValueError("Project name must be provided.")
        return values