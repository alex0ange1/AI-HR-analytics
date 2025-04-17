from typing import Type

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, insert, update, delete
from sqlalchemy.exc import IntegrityError

from project.schemas.resume import *
from project.infrastructure.postgres.models import Resume

from project.core.exceptions import ResumeNotFound
from project.resource.analyze import Analyzer


class ResumeRepository:
    _collection: Type[Resume] = Resume

    async def get_resume_by_id(
            self,
            session: AsyncSession,
            resume_id: int,
    ) -> ResumeSchema:
        query = (
            select(self._collection)
            .where(self._collection.id == resume_id)
        )

        resume = await session.scalar(query)

        if not resume:
            raise ResumeNotFound(_id=resume_id)

        return ResumeSchema.model_validate(obj=resume)

    async def get_all_resumes(
            self,
            session: AsyncSession,
    ) -> list[ResumeSchema]:
        query = select(self._collection)

        resumes = await session.scalars(query)

        return [ResumeSchema.model_validate(obj=resume) for resume in resumes.all()]

    async def create_resume(
            self,
            session: AsyncSession,
            resume: ResumeCreateUpdateSchema,
    ) -> ResumeSchema:
        query = (
            insert(self._collection)
            .values(resume.model_dump())
            .returning(self._collection)
        )

        created_resume = await session.scalar(query)
        await session.flush()

        return ResumeSchema.model_validate(obj=created_resume)

    async def update_resume(
            self,
            session: AsyncSession,
            resume_id: int,
            resume: ResumeCreateUpdateSchema,
    ) -> ResumeSchema:
        query = (
            update(self._collection)
            .where(self._collection.id == resume_id)
            .values(resume.model_dump())
            .returning(self._collection)
        )

        updated_resume = await session.scalar(query)

        if not updated_resume:
            raise ResumeNotFound(_id=resume_id)

        return ResumeSchema.model_validate(obj=updated_resume)

    async def delete_resume(
            self,
            session: AsyncSession,
            resume_id: int
    ) -> None:
        query = delete(self._collection).where(self._collection.id == resume_id)

        result = await session.execute(query)

        if not result.rowcount:
            raise ResumeNotFound(_id=resume_id)

    async def process_multiple_files(
            self,
            session: AsyncSession,
            files_data: MultiFileUploadSchema,
    ) -> ProcessedResumeResponse:
        analyzer = Analyzer()

        resume_ids = []
        need_comp = files_data.profession.competencies

        for file_data in files_data.files:
            resume_data = ResumeCreateUpdateSchema(
                first_name=file_data.filename,
                last_name=file_data.filename,
                phone="1234567890",
                competencies=analyzer.analyze(file_data.content, need_comp)
            )

            query = (
                insert(self._collection)
                .values(resume_data.model_dump())
                .returning(self._collection)
            )

            created_resume = await session.scalar(query)
            resume_ids.append(created_resume.id)

        await session.flush()
        return ProcessedResumeResponse(
            resume_ids=resume_ids,
            status=f"Processed {len(files_data.files)} files"
        )

    async def get_resumes_by_ids(
            self,
            session: AsyncSession,
            resume_ids: List[int],
    ) -> List[ResumeSchema]:
        query = (
            select(self._collection)
            .where(self._collection.id.in_(resume_ids))
        )
        resumes = await session.scalars(query)
        return [ResumeSchema.model_validate(obj=resume) for resume in resumes.all()]
