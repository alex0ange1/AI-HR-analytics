from fastapi import APIRouter, HTTPException, status, Depends, UploadFile, File, Form
from typing import List

from project.schemas.resume import *
from project.core.exceptions import ResumeNotFound
from project.api.depends import database, resume_repo, get_current_user, check_for_admin_access
from project.schemas.user import UserSchema

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
    "/upload-files",
    response_model=ProcessedResumeResponse,
    status_code=status.HTTP_201_CREATED,
)
async def upload_files(
        files: List[UploadFile] = File(...),
        current_user: UserSchema = Depends(get_current_user),
) -> ProcessedResumeResponse:
    check_for_admin_access(user=current_user)

    try:
        # Преобразуем загруженные файлы в схему
        files_data = MultiFileUploadSchema(
            files=[
                FileUploadSchema(
                    filename=file.filename,
                    content=await file.read()  # добавить парсер разных форматов
                )
                for file in files
            ],
            user_id=current_user.id
        )

        async with database.session() as session:
            result = await resume_repo.process_multiple_files(
                session=session,
                files_data=files_data
            )

        return result

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )


@resume_router.post(
    "/get-resumes-by-ids",
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
