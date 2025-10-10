from fastapi import APIRouter,status,Depends,HTTPException,UploadFile,File
from sqlalchemy.orm import Session
from pathlib import Path
from datetime import datetime
from collections import Counter,defaultdict


import uuid
import shutil
import cv2


from src.core.db import get_db
from src.core.auth import get_current_user
from src.core.config import settings
from src.posts.schemas import PostResponse
from src.users.models import User
from src.posts.models import Post
from src.yolo_detector.V11 import Yolov11Detector
from src.posts._utils import _read_yaml_file


# for coonstant value 
UPLOAD_DIR = Path("uploads")
UPLOAD_DIR.mkdir(exist_ok=True)

ALLOWED_EXTENSIONS = {"jpg", "jpeg", "png"}

CLASS_NAMES = _read_yaml_file(str(settings.LABEL_PATH))

router = APIRouter(
    prefix="/posts",
    tags=["Posts"]
)

detector = Yolov11Detector(model_path=settings.MODEL_PATH,
                           label_yaml=settings.LABEL_PATH)


# this for create post
@router.post("/",response_model=PostResponse,status_code=status.HTTP_201_CREATED)
async def upload_and_predict(
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
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
    # jalankan model
    img = cv2.imread(str(file_path))
    boxes,scores,class_ids = detector.detect(img)
    # hasil prediction ke dalam json file
    if not boxes:
        result_predict = {"predict": {}, "confidence": {}, "bbox": {}}
    else:
        predict_summary = {}
        predict_confidence = {}
        predict_bbox = {}
        for box,score,cls_id in zip(boxes,scores,class_ids):
            # class name
            cls_name = CLASS_NAMES[cls_id] if cls_id < len(CLASS_NAMES) else f"class_{cls_id}"
            # Tambahkan count
            predict_summary[cls_name] = predict_summary.get(cls_name, 0) + 1

            # Tambahkan confidence
            predict_confidence.setdefault(cls_name, []).append(round(float(score), 4))

            # Tambahkan bbox
            predict_bbox.setdefault(cls_name, []).append([int(x) for x in box])

        result_predict ={
            "predict":predict_summary,
            "confidence":predict_confidence,
            "bbox":predict_bbox
        }

    # Simpan record post di DB
    db_post = Post(
        post_id=str(uuid.uuid4()),
        user_id=current_user.user_id,
        image_url=str(file_path),
        result = result_predict,
        create_at = datetime.now()
    )

    db.add(db_post)
    db.commit()
    db.refresh(db_post)

    return db_post