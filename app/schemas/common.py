from typing import Generic, TypeVar

from pydantic import BaseModel

# This is a generic type variable (like <T> in Java/C#)
T = TypeVar("T")


class PaginatedResponse(BaseModel, Generic[T]):  # noqa: UP046
    """
    A standard wrapper for paginated API responses.
    """

    items: list[T]  # The actual data (e.g., list of bookmarks)
    total: int  # Total number of items in the database
    page: int  # Current page number
    size: int  # Items per page
    pages: int  # Total number of pages

    class Config:
        arbitrary_types_allowed = True
