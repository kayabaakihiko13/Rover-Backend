from fastapi import APIRouter,status,Depends,HTTPException,UploadFile,File
from sqlalchemy.orm import Session
from pathlib import Path
# from typing import List
import uuid
import shutil

from src.core.db import get_db
from src.core.auth import get_current_user
from src.posts.schemas import PostResponse
from src.users.models import User
from src.posts.models import Post

router = APIRouter(
    prefix="/posts",
    tags=["Posts"]
)
# for coonstant file 
UPLOAD_DIR = Path("uploads")
UPLOAD_DIR.mkdir(exist_ok=True)

ALLOWED_EXTENSIONS = {"jpg", "jpeg", "png"}
# this for create post
@router.post("/{user_id}",response_model=PostResponse,
             status_code=status.HTTP_201_CREATED)
async def upload_post_image(
    user_id:str,
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    if str(current_user.user_id) != str(user_id):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You are not allowed to create a post for another user."
        )
    
    # Cek ekstensi file
    file_ext = file.filename.split(".")[-1].lower()
    if file_ext not in ALLOWED_EXTENSIONS:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"File type '{file_ext}' not allowed. Allowed types: {', '.join(ALLOWED_EXTENSIONS)}"
        )

    # Simpan file
    file_path = UPLOAD_DIR / f"{uuid.uuid4()}.{file_ext}"
    with file_path.open("wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    # Simpan record post di DB
    db_post = Post(
        post_id=str(uuid.uuid4()),
        user_id=current_user.user_id,
        image_url=str(file_path)
    )
    db.add(db_post)
    db.commit()
    db.refresh(db_post)

    return db_post