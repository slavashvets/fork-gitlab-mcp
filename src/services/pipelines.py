"""Service functions for interacting with GitLab pipelines."""

from src.api.custom_exceptions import GitLabAPIError, GitLabErrorType
from src.api.rest_client import gitlab_rest_client
from src.schemas.pipelines import (
    GetLatestPipelineInput,
    GetSinglePipelineInput,
    GitLabPipeline,
    GitLabPipelineList,
    ListProjectPipelinesInput,
)


async def list_project_pipelines(
    input_model: ListProjectPipelinesInput,
) -> GitLabPipelineList:
    """List pipelines for a project."""
    try:
        project_path = gitlab_rest_client._encode_path_parameter(
            input_model.project_path
        )
        params = {
            "page": input_model.page,
            "per_page": input_model.per_page,
        }
        response = await gitlab_rest_client.get_async(
            f"/projects/{project_path}/pipelines",
            params=params,
        )
        items = [GitLabPipeline.model_validate(p) for p in response]
        return GitLabPipelineList(items=items)
    except GitLabAPIError as exc:
        raise GitLabAPIError(
            GitLabErrorType.REQUEST_FAILED,
            {
                "message": f"Failed to list pipelines for {input_model.project_path}",
                "operation": "list_project_pipelines",
            },
        ) from exc
    except Exception as exc:
        raise GitLabAPIError(
            GitLabErrorType.SERVER_ERROR,
            {
                "message": "Internal error listing pipelines",
                "operation": "list_project_pipelines",
            },
        ) from exc


async def get_single_pipeline(
    input_model: GetSinglePipelineInput,
) -> GitLabPipeline:
    """Get a single pipeline by ID."""
    try:
        project_path = gitlab_rest_client._encode_path_parameter(
            input_model.project_path
        )
        response = await gitlab_rest_client.get_async(
            f"/projects/{project_path}/pipelines/{input_model.pipeline_id}"
        )
        return GitLabPipeline.model_validate(response)
    except GitLabAPIError as exc:
        if "not found" in str(exc).lower():
            raise GitLabAPIError(
                GitLabErrorType.NOT_FOUND,
                {"message": f"Pipeline {input_model.pipeline_id} not found"},
            ) from exc
        raise GitLabAPIError(
            GitLabErrorType.REQUEST_FAILED,
            {
                "message": f"Failed to get pipeline {input_model.pipeline_id}",
                "operation": "get_single_pipeline",
            },
        ) from exc
    except Exception as exc:
        raise GitLabAPIError(
            GitLabErrorType.SERVER_ERROR,
            {"message": "Internal error getting pipeline", "operation": "get_single_pipeline"},
        ) from exc


async def get_latest_pipeline(
    input_model: GetLatestPipelineInput,
) -> GitLabPipeline:
    """Get the latest pipeline for a ref."""
    try:
        project_path = gitlab_rest_client._encode_path_parameter(
            input_model.project_path
        )
        params = {"ref": input_model.ref, "per_page": 1}
        response = await gitlab_rest_client.get_async(
            f"/projects/{project_path}/pipelines",
            params=params,
        )
        if not response:
            raise GitLabAPIError(
                GitLabErrorType.NOT_FOUND,
                {"message": "No pipelines found"},
            )
        latest = response[0]
        return GitLabPipeline.model_validate(latest)
    except GitLabAPIError:
        raise
    except Exception as exc:
        raise GitLabAPIError(
            GitLabErrorType.SERVER_ERROR,
            {"message": "Internal error getting latest pipeline", "operation": "get_latest_pipeline"},
        ) from exc
