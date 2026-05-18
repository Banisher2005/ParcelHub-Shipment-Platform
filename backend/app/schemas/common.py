"""
Common schemas: pagination, error responses, base models.
"""

from pydantic import BaseModel, Field


class PaginationParams(BaseModel):
    """Query parameters for paginated endpoints."""
    page: int = Field(default=1, ge=1)
    page_size: int = Field(default=20, ge=1, le=100)

    @property
    def offset(self) -> int:
        return (self.page - 1) * self.page_size


class PaginatedResponse(BaseModel):
    """Wrapper for paginated responses."""
    items: list = []
    total: int = 0
    page: int = 1
    page_size: int = 20
    total_pages: int = 0


class ErrorResponse(BaseModel):
    """Standard error response."""
    detail: str
    code: str | None = None


class SuccessResponse(BaseModel):
    """Standard success response for mutations."""
    success: bool = True
    message: str = "OK"
