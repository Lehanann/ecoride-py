from pathlib import Path
from uuid import uuid4
import shutil
from fastapi import UploadFile
from typing import BinaryIO, cast

class FileService:
    STORAGE_DIR = Path.cwd() / 'storage/profiles'
    BUFFER_SIZE = 1024 * 1024

    @classmethod
    def save_profile_image(cls, file: UploadFile) -> str:
        cls.STORAGE_DIR.mkdir(parents=True, exist_ok=True)

        extension: str = file.filename.split('.')[-1]
        filename: str = f'{uuid4()}.{extension}'
        file_path = cls.STORAGE_DIR / filename

        file_path.touch()

        with file_path.open('wb') as buffer :
            for chunk in iter(lambda: file.file.read(cls.BUFFER_SIZE), b''):
                buffer.write(chunk)

        local_filename = cls.STORAGE_DIR / filename

        return local_filename.name

