"""Full-text search service for documents."""

from uuid import UUID

from sqlalchemy import and_, func, literal_column, select, text
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.models.document import Document
from app.schemas.search import SearchFilters, SearchMode


class SearchService:
    """Service for full-text search operations."""

    def __init__(self, db: AsyncSession):
        self.db = db

    async def search(
        self,
        query: str,
        mode: SearchMode = SearchMode.SIMPLE,
        filters: SearchFilters | None = None,
        page: int = 1,
        page_size: int = 20,
    ) -> tuple[list[dict], int]:
        """
        Search documents with various modes.

        Args:
            query: Search query string
            mode: Search mode (simple, phrase, fuzzy, boolean)
            filters: Optional search filters
            page: Page number (1-indexed)
            page_size: Number of results per page

        Returns:
            Tuple of (search results with rank and highlights, total count)
        """
        if mode == SearchMode.SIMPLE:
            return await self._search_simple(query, filters, page, page_size)
        elif mode == SearchMode.PHRASE:
            return await self._search_phrase(query, filters, page, page_size)
        elif mode == SearchMode.FUZZY:
            return await self._search_fuzzy(query, filters, page, page_size)
        elif mode == SearchMode.BOOLEAN:
            return await self._search_boolean(query, filters, page, page_size)
        else:
            return await self._search_simple(query, filters, page, page_size)

    def _build_filter_conditions(self, filters: SearchFilters | None) -> list:
        """Build SQLAlchemy filter conditions from SearchFilters."""
        conditions = []
        
        if filters is None:
            return conditions
        
        if filters.owner_id is not None:
            conditions.append(Document.owner_id == filters.owner_id)
        
        if filters.date_from is not None:
            conditions.append(Document.created_at >= filters.date_from)
        
        if filters.date_to is not None:
            conditions.append(Document.created_at <= filters.date_to)
        
        if filters.meta_filters is not None:
            # JSONB contains operator
            conditions.append(Document.meta.contains(filters.meta_filters))
        
        return conditions

    async def _search_simple(
        self,
        query: str,
        filters: SearchFilters | None,
        page: int,
        page_size: int,
    ) -> tuple[list[dict], int]:
        """
        Simple search using plainto_tsquery.
        Converts query to tsquery automatically, handling spaces as AND.
        """
        tsquery = func.plainto_tsquery("english", query)
        
        return await self._execute_fts_search(
            tsquery, query, filters, page, page_size
        )

    async def _search_phrase(
        self,
        query: str,
        filters: SearchFilters | None,
        page: int,
        page_size: int,
    ) -> tuple[list[dict], int]:
        """
        Phrase search using phraseto_tsquery.
        Matches exact phrase order.
        """
        tsquery = func.phraseto_tsquery("english", query)
        
        return await self._execute_fts_search(
            tsquery, query, filters, page, page_size
        )

    async def _search_boolean(
        self,
        query: str,
        filters: SearchFilters | None,
        page: int,
        page_size: int,
    ) -> tuple[list[dict], int]:
        """
        Boolean search using to_tsquery.
        Supports AND (&), OR (|), NOT (!), and grouping.
        """
        # Sanitize query for to_tsquery (basic sanitization)
        # User should use proper boolean syntax: word1 & word2 | word3
        tsquery = func.to_tsquery("english", query)
        
        return await self._execute_fts_search(
            tsquery, query, filters, page, page_size
        )

    async def _execute_fts_search(
        self,
        tsquery,
        original_query: str,
        filters: SearchFilters | None,
        page: int,
        page_size: int,
    ) -> tuple[list[dict], int]:
        """Execute full-text search with ranking and highlighting."""
        # Build filter conditions
        filter_conditions = self._build_filter_conditions(filters)
        
        # Rank calculation
        rank = func.ts_rank(Document.search_vector, tsquery).label("rank")
        
        # Title highlight
        title_headline = func.ts_headline(
            "english",
            Document.title,
            tsquery,
            "StartSel=<b>, StopSel=</b>, MaxWords=50, MinWords=10"
        ).label("title_highlight")
        
        # Content highlight
        content_headline = func.ts_headline(
            "english",
            func.coalesce(Document.content, ""),
            tsquery,
            "StartSel=<b>, StopSel=</b>, MaxWords=50, MinWords=10, MaxFragments=3"
        ).label("content_highlight")
        
        # Main search query
        search_condition = Document.search_vector.op("@@")(tsquery)
        
        # Count query
        count_query = (
            select(func.count(Document.id))
            .where(search_condition)
        )
        if filter_conditions:
            count_query = count_query.where(and_(*filter_conditions))
        
        total_result = await self.db.execute(count_query)
        total = total_result.scalar() or 0
        
        # Main query with pagination
        offset = (page - 1) * page_size
        
        main_query = (
            select(
                Document,
                rank,
                title_headline,
                content_headline,
            )
            .options(selectinload(Document.owner))
            .where(search_condition)
        )
        
        if filter_conditions:
            main_query = main_query.where(and_(*filter_conditions))
        
        main_query = (
            main_query
            .order_by(rank.desc())
            .offset(offset)
            .limit(page_size)
        )
        
        result = await self.db.execute(main_query)
        rows = result.all()
        
        # Build results with highlights
        results = []
        for row in rows:
            document = row[0]
            rank_value = row[1]
            title_hl = row[2]
            content_hl = row[3]
            
            highlights = []
            if title_hl and "<b>" in title_hl:
                highlights.append({
                    "field": "title",
                    "fragment": title_hl,
                })
            if content_hl and "<b>" in content_hl:
                highlights.append({
                    "field": "content",
                    "fragment": content_hl,
                })
            
            results.append({
                "document": document,
                "rank": float(rank_value) if rank_value else 0.0,
                "highlights": highlights,
            })
        
        return results, total

    async def _search_fuzzy(
        self,
        query: str,
        filters: SearchFilters | None,
        page: int,
        page_size: int,
    ) -> tuple[list[dict], int]:
        """
        Fuzzy search using pg_trgm similarity.
        Good for typo tolerance and OCR errors.
        """
        # Similarity threshold
        similarity_threshold = 0.3
        
        # Build filter conditions
        filter_conditions = self._build_filter_conditions(filters)
        
        # Similarity scores
        title_similarity = func.similarity(Document.title, query).label("title_sim")
        content_similarity = func.similarity(
            func.coalesce(Document.content, ""), query
        ).label("content_sim")
        
        # Combined similarity (weighted: title more important)
        combined_similarity = (
            title_similarity * 2 + content_similarity
        ).label("combined_sim")
        
        # Search condition: either title or content has similarity above threshold
        search_condition = (
            (func.similarity(Document.title, query) > similarity_threshold) |
            (func.similarity(func.coalesce(Document.content, ""), query) > similarity_threshold)
        )
        
        # Count query
        count_query = select(func.count(Document.id)).where(search_condition)
        if filter_conditions:
            count_query = count_query.where(and_(*filter_conditions))
        
        total_result = await self.db.execute(count_query)
        total = total_result.scalar() or 0
        
        # Main query
        offset = (page - 1) * page_size
        
        main_query = (
            select(
                Document,
                combined_similarity,
                title_similarity,
                content_similarity,
            )
            .options(selectinload(Document.owner))
            .where(search_condition)
        )
        
        if filter_conditions:
            main_query = main_query.where(and_(*filter_conditions))
        
        main_query = (
            main_query
            .order_by(combined_similarity.desc())
            .offset(offset)
            .limit(page_size)
        )
        
        result = await self.db.execute(main_query)
        rows = result.all()
        
        # Build results
        results = []
        for row in rows:
            document = row[0]
            combined_sim = row[1]
            title_sim = row[2]
            content_sim = row[3]
            
            highlights = []
            if title_sim and title_sim > similarity_threshold:
                highlights.append({
                    "field": "title",
                    "fragment": document.title,
                })
            if content_sim and content_sim > similarity_threshold and document.content:
                # Get first 200 chars of content as fragment
                fragment = document.content[:200] + "..." if len(document.content) > 200 else document.content
                highlights.append({
                    "field": "content",
                    "fragment": fragment,
                })
            
            results.append({
                "document": document,
                "rank": float(combined_sim) if combined_sim else 0.0,
                "highlights": highlights,
            })
        
        return results, total

    async def get_suggestions(
        self,
        query: str,
        limit: int = 10,
        owner_id: UUID | None = None,
    ) -> list[dict]:
        """
        Get search suggestions/autocomplete based on query prefix.

        Args:
            query: Query prefix
            limit: Maximum number of suggestions
            owner_id: Optional owner filter

        Returns:
            List of suggestions with text, document_id, and field
        """
        suggestions = []
        
        # Search in titles using LIKE with prefix
        title_query = (
            select(Document.id, Document.title)
            .where(Document.title.ilike(f"%{query}%"))
        )
        
        if owner_id is not None:
            title_query = title_query.where(Document.owner_id == owner_id)
        
        title_query = title_query.limit(limit)
        
        result = await self.db.execute(title_query)
        rows = result.all()
        
        for row in rows:
            suggestions.append({
                "text": row[1],
                "document_id": row[0],
                "field": "title",
            })
        
        return suggestions[:limit]
