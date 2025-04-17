from fastapi import APIRouter, HTTPException, status, Depends, UploadFile, File, Form
from pydantic import ValidationError
from typing import List

from project.schemas.resume import *
from project.schemas.profession import *
from project.core.exceptions import ResumeNotFound, ProfessionNotFound
from project.api.depends import database, resume_repo, profession_repo, get_current_user, check_for_admin_access
from project.schemas.user import UserSchema
from project.resource.analyze import Analyzer

import json

resume_router = APIRouter()


@resume_router.get(
    "/all_resumes",
    response_model=list[ResumeSchema],
    status_code=status.HTTP_200_OK,
    dependencies=[Depends(get_current_user)],
)
async def get_all_resumes() -> list[ResumeSchema]:
    async with database.session() as session:
        all_resumes = await resume_repo.get_all_resumes(session=session)

    return all_resumes


@resume_router.get(
    "/resume/{resume_id}",
    response_model=ResumeSchema,
    status_code=status.HTTP_200_OK,
    dependencies=[Depends(get_current_user)],
)
async def get_resume_by_id(
        resume_id: int,
) -> ResumeSchema:
    try:
        async with database.session() as session:
            resume = await resume_repo.get_resume_by_id(session=session, resume_id=resume_id)
    except ResumeNotFound as error:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=error.message)

    return resume


@resume_router.post(
    "/add_resume",
    response_model=ResumeSchema,
    status_code=status.HTTP_201_CREATED,
)
async def add_resume(
        resume_dto: ResumeCreateUpdateSchema,
        current_user: UserSchema = Depends(get_current_user),
) -> ResumeSchema:
    check_for_admin_access(user=current_user)
    try:
        async with database.session() as session:
            new_resume = await resume_repo.create_resume(session=session, resume=resume_dto)
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))

    return new_resume


@resume_router.put(
    "/update_resume/{resume_id}",
    response_model=ResumeSchema,
    status_code=status.HTTP_200_OK,
)
async def update_resume(
        resume_id: int,
        resume_dto: ResumeCreateUpdateSchema,
        current_user: UserSchema = Depends(get_current_user),
) -> ResumeSchema:
    check_for_admin_access(user=current_user)
    try:
        async with database.session() as session:
            updated_resume = await resume_repo.update_resume(
                session=session,
                resume_id=resume_id,
                resume=resume_dto,
            )
    except ResumeNotFound as error:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=error.message)

    return updated_resume


@resume_router.delete(
    "/delete_resume/{resume_id}",
    status_code=status.HTTP_204_NO_CONTENT,
)
async def delete_resume(
        resume_id: int,
        current_user: UserSchema = Depends(get_current_user),
) -> None:
    check_for_admin_access(user=current_user)
    try:
        async with database.session() as session:
            await resume_repo.delete_resume(session=session, resume_id=resume_id)
    except ResumeNotFound as error:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=error.message)


@resume_router.post(
    "/analyze_files/{profession_id}",
    response_model=ProcessedResumeResponse,
    status_code=status.HTTP_200_OK,
)
async def analyze_files(
        profession_id: int,
        files: List[UploadFile] = File(...),
        current_user: UserSchema = Depends(get_current_user),
) -> ProcessedResumeResponse:
    check_for_admin_access(user=current_user)
    try:
        analyzer = Analyzer()

        async with database.session() as session:
            profession = await profession_repo.get_profession_by_id(session=session, profession_id=profession_id)

        files_content = []
        for file in files:
            content = await analyzer.parse_file(file)
            files_content.append(
                FileUploadSchema(
                    filename=file.filename,
                    content=content
                )
            )

        files_data = MultiFileUploadSchema(
            files=files_content,
            profession=profession
        )

        async with database.session() as session:
            result = await resume_repo.process_multiple_files(
                session=session,
                files_data=files_data
            )

        return result

    except ProfessionNotFound as error:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=error.message)

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )


@resume_router.post(
    "/get_analyze_resumes_for_profession/{profession_id}",
    response_model=ProfessionResumeMatchResponse,
    status_code=status.HTTP_200_OK,
    dependencies=[Depends(get_current_user)],
)
async def get_analyze_resumes_for_profession(
        profession_id: int,
        resume_ids: List[int],
) -> ProfessionResumeMatchResponse:
    try:
        async with database.session() as session:
            # Получаем профессию
            profession = await profession_repo.get_profession_by_id(
                session=session,
                profession_id=profession_id
            )

            # Получаем резюме
            resumes = await resume_repo.get_resumes_by_ids(
                session=session,
                resume_ids=resume_ids
            )

            # Проверяем, что все резюме найдены
            found_ids = {resume.id for resume in resumes}
            not_found = [id_ for id_ in resume_ids if id_ not in found_ids]
            if not_found:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail=f"Resumes with IDs {not_found} not found"
                )

            # Анализируем соответствие
            results = []
            required_competencies = profession.competencies.get("competencies", [])

            for resume in resumes:
                resume_competencies = resume.competencies.get("competencies", [])
                resume_comp_dict = {comp["name"]: comp["level"] for comp in resume_competencies}

                total_possible = 0
                total_matched = 0
                mismatches = []

                for req_comp in required_competencies:
                    comp_name = req_comp["name"]
                    required_level = req_comp["level"]
                    total_possible += required_level

                    if comp_name in resume_comp_dict:
                        actual_level = resume_comp_dict[comp_name]
                        if actual_level >= required_level:
                            total_matched += required_level
                        else:
                            total_matched += actual_level
                            mismatches.append(CompetencyMismatch(
                                name=comp_name,
                                required_level=required_level,
                                actual_level=actual_level
                            ))
                    else:
                        mismatches.append(CompetencyMismatch(
                            name=comp_name,
                            required_level=required_level,
                            actual_level=0
                        ))

                match_percentage = (total_matched / total_possible * 100) if total_possible > 0 else 0

                results.append(ResumeMatchResult(
                    resume_id=resume.id,
                    first_name=resume.first_name,
                    last_name=resume.last_name,
                    match_percentage=round(match_percentage, 2),
                    mismatched_competencies=mismatches
                ))

            return ProfessionResumeMatchResponse(results=results)

    except ProfessionNotFound as error:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=error.message)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )


@resume_router.post(
    "/get_resumes_by_ids",
    response_model=ResumeListResponse,
    status_code=status.HTTP_200_OK,
    dependencies=[Depends(get_current_user)],
)
async def get_resumes_by_ids(
        resume_ids: List[int],
) -> ResumeListResponse:
    try:
        async with database.session() as session:
            resumes = await resume_repo.get_resumes_by_ids(
                session=session,
                resume_ids=resume_ids
            )

            # Проверяем, все ли ID были найдены
            found_ids = {resume.id for resume in resumes}
            not_found = [id_ for id_ in resume_ids if id_ not in found_ids]

            if not_found:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail=f"Resumes with IDs {not_found} not found"
                )

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )

    return ResumeListResponse(resumes=resumes)
