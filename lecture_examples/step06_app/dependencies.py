from typing import Annotated

from fastapi import Query


class Pagination:
    """여러 목록 API에서 재사용할 Query Parameter 모음."""

    def __init__(
        self,
        offset: Annotated[int, Query(ge=0)] = 0,
        limit: Annotated[int, Query(ge=1, le=100)] = 10,
    ) -> None:
        self.offset = offset
        self.limit = limit

