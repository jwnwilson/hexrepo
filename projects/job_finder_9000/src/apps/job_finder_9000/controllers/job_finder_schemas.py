"""
API Schemas for Job Finder 9000

This module defines the API schemas used by Django Ninja for the job finder application.
These schemas handle request/response serialization and validation.
"""

from datetime import datetime
from typing import Any, Dict, List, Optional

from ninja import Schema
from pydantic import Field, validator

# =============================================================================
# Request Schemas
# =============================================================================


class SkillSchema(Schema):
    """Schema for candidate skills."""

    name: str = Field(..., description="Name of the skill")
    proficiency: str = Field(
        ..., description="Proficiency level: beginner, intermediate, expert"
    )
    years_experience: Optional[int] = Field(
        None, description="Years of experience with this skill"
    )

    @validator("proficiency")
    def validate_proficiency(cls, v):
        valid_levels = ["beginner", "intermediate", "expert"]
        if v.lower() not in valid_levels:
            raise ValueError(f"Proficiency must be one of: {', '.join(valid_levels)}")
        return v.lower()


class LocationSchema(Schema):
    """Schema for location preferences."""

    city: str = Field(..., description="City name")
    state: Optional[str] = Field(None, description="State or province")
    country: str = Field("USA", description="Country")
    remote_preference: str = Field(
        "hybrid", description="Remote preference: on-site, hybrid, remote"
    )

    @validator("remote_preference")
    def validate_remote_preference(cls, v):
        valid_preferences = ["on-site", "hybrid", "remote"]
        if v.lower() not in valid_preferences:
            raise ValueError(
                f"Remote preference must be one of: {', '.join(valid_preferences)}"
            )
        return v.lower()


class JobSearchRequestSchema(Schema):
    """Schema for job search requests."""

    name: str = Field(..., description="Candidate name")
    email: str = Field(..., description="Candidate email")
    skills: List[SkillSchema] = Field(..., description="Candidate skills")
    experience_years: int = Field(..., ge=0, description="Total years of experience")
    preferred_locations: List[LocationSchema] = Field(
        ..., description="Preferred job locations"
    )
    salary_expectation: Optional[int] = Field(
        None, ge=0, description="Expected salary in USD"
    )
    job_preferences: Optional[Dict[str, Any]] = Field(
        default_factory=dict, description="Additional job preferences"
    )
    max_results: int = Field(
        5, ge=1, le=100, description="Maximum number of jobs to return"
    )
    include_remote: bool = Field(True, description="Include remote jobs")
    salary_threshold: Optional[int] = Field(
        None, ge=0, description="Minimum salary threshold"
    )
    use_cache: bool = Field(True, description="Use cached results if available")


class JobRecommendationsRequestSchema(Schema):
    """Schema for job recommendations requests."""

    name: str = Field(..., description="Candidate name")
    email: str = Field(..., description="Candidate email")
    skills: List[SkillSchema] = Field(..., description="Candidate skills")
    experience_years: int = Field(..., ge=0, description="Total years of experience")
    preferred_locations: List[LocationSchema] = Field(
        ..., description="Preferred job locations"
    )
    salary_expectation: Optional[int] = Field(
        None, ge=0, description="Expected salary in USD"
    )
    max_results: int = Field(
        5, ge=1, le=50, description="Maximum number of recommendations"
    )


class MarketAnalysisRequestSchema(Schema):
    """Schema for market analysis requests."""

    name: str = Field(..., description="Candidate name")
    email: str = Field(..., description="Candidate email")
    skills: List[SkillSchema] = Field(..., description="Candidate skills")
    experience_years: int = Field(..., ge=0, description="Total years of experience")
    preferred_locations: List[LocationSchema] = Field(
        ..., description="Preferred job locations"
    )
    salary_expectation: Optional[int] = Field(
        None, ge=0, description="Expected salary in USD"
    )


# =============================================================================
# Response Schemas
# =============================================================================


class JobRequirementSchema(Schema):
    """Schema for job requirements."""

    skill: str = Field(..., description="Required skill")
    level: str = Field(..., description="Required level: entry, mid, senior, lead")
    is_mandatory: bool = Field(
        True, description="Whether this is a mandatory requirement"
    )


class JobPostingSchema(Schema):
    """Schema for job postings."""

    title: str = Field(..., description="Job title")
    location: str = Field(default="", description="Job location")
    job_url: str = Field(..., description="URL to the job posting")
    match_score: Optional[float] = Field(None, description="Match score (0-100)")


class JobSearchResultSchema(Schema):
    """Schema for job search results."""

    jobs: List[JobPostingSchema] = Field(..., description="Found job postings")
    total_found: int = Field(..., description="Total number of jobs found")
    search_duration: float = Field(..., description="Search duration in seconds")
    sources_searched: List[str] = Field(
        ..., description="Job sources that were searched"
    )
    summary: str = Field(..., description="Summary of the search results")


class MarketAnalysisSchema(Schema):
    """Schema for market analysis results."""

    market_demand: str = Field(
        ..., description="Market demand level: low, medium, high"
    )
    average_salary: int = Field(..., description="Average salary for similar positions")
    salary_percentile: int = Field(..., description="Salary percentile (0-100)")
    average_match_score: float = Field(..., description="Average match score")
    skill_gaps: List[str] = Field(..., description="Identified skill gaps")
    total_jobs_analyzed: int = Field(..., description="Total number of jobs analyzed")
    recommendations: List[str] = Field(..., description="Market recommendations")


class JobRecommendationsSchema(Schema):
    """Schema for job recommendations."""

    recommendations: List[JobPostingSchema] = Field(
        ..., description="Recommended job postings"
    )
    total_recommendations: int = Field(
        ..., description="Total number of recommendations"
    )
    average_match_score: float = Field(
        ..., description="Average match score of recommendations"
    )
    summary: str = Field(..., description="Summary of recommendations")


# =============================================================================
# Error Schemas
# =============================================================================


class ErrorSchema(Schema):
    """Schema for error responses."""

    error: str = Field(..., description="Error message")
    detail: Optional[str] = Field(None, description="Detailed error information")
    code: Optional[str] = Field(None, description="Error code")


class ValidationErrorSchema(Schema):
    """Schema for validation error responses."""

    error: str = Field("Validation Error", description="Error type")
    detail: str = Field(..., description="Validation error details")
    field_errors: Dict[str, List[str]] = Field(
        ..., description="Field-specific validation errors"
    )


# =============================================================================
# Success Response Schemas
# =============================================================================


class SuccessSchema(Schema):
    """Schema for success responses."""

    success: bool = Field(True, description="Success indicator")
    message: str = Field(..., description="Success message")
    data: Optional[Dict[str, Any]] = Field(None, description="Response data")


class JobSearchSuccessSchema(Schema):
    """Schema for successful job search responses."""

    success: bool = Field(True, description="Success indicator")
    message: str = Field(
        "Job search completed successfully", description="Success message"
    )
    data: JobSearchResultSchema = Field(..., description="Job search results")


class RecommendationsSuccessSchema(Schema):
    """Schema for successful recommendations responses."""

    success: bool = Field(True, description="Success indicator")
    message: str = Field(
        "Job recommendations generated successfully", description="Success message"
    )
    data: JobRecommendationsSchema = Field(..., description="Job recommendations")


class MarketAnalysisSuccessSchema(Schema):
    """Schema for successful market analysis responses."""

    success: bool = Field(True, description="Success indicator")
    message: str = Field(
        "Market analysis completed successfully", description="Success message"
    )
    data: MarketAnalysisSchema = Field(..., description="Market analysis results")


# =============================================================================
# Utility Schemas
# =============================================================================


class HealthCheckSchema(Schema):
    """Schema for health check responses."""

    status: str = Field(..., description="Service status")
    timestamp: datetime = Field(..., description="Current timestamp")
    version: str = Field(..., description="API version")
    agent_status: str = Field(..., description="Job finder agent status")


class CacheClearSchema(Schema):
    """Schema for cache clearing responses."""

    success: bool = Field(..., description="Success indicator")
    message: str = Field(..., description="Cache clearing message")
    cleared_entries: Optional[int] = Field(
        None, description="Number of cache entries cleared"
    )
