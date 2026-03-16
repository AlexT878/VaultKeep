from pathlib import Path
import uuid
from fastapi import UploadFile

UPLOAD_DIR = Path("files")


async def save_file_to_disk(file: UploadFile, user_id: int) -> tuple[Path, int]:
    extension = Path(file.filename).suffix
    unique_name = f"{uuid.uuid4()}{extension}"

    user_dir = UPLOAD_DIR / str(user_id)
    user_dir.mkdir(parents=True, exist_ok=True)
    dest = user_dir / unique_name

    content = await file.read()
    dest.write_bytes(content)

    return dest, len(content)
