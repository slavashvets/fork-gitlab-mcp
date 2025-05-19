"""Pydantic models for GitLab pipeline operations."""

from pydantic import BaseModel, HttpUrl

from src.schemas.base import BaseResponseList, GitLabResponseBase


class GitLabPipeline(GitLabResponseBase):
    """Response model for a GitLab pipeline."""

    id: int
    sha: str | None = None
    ref: str | None = None
    status: str | None = None
    web_url: HttpUrl | None = None


class ListProjectPipelinesInput(BaseModel):
    """Input model for listing pipelines in a GitLab project."""

    project_path: str
    page: int = 1
    per_page: int = 20


class GitLabPipelineList(BaseResponseList[GitLabPipeline]):
    """Response model for listing project pipelines."""

    pass


class GetSinglePipelineInput(BaseModel):
    """Input model for retrieving a single pipeline."""

    project_path: str
    pipeline_id: int


class GetLatestPipelineInput(BaseModel):
    """Input model for retrieving the latest pipeline for a ref."""

    project_path: str
    ref: str
