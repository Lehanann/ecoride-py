from pathlib import Path
from uuid import uuid4
from fastapi import UploadFile
import logging

logger = logging.getLogger(__name__)

class FileService:
    """
    Service responsible for handling profile image files.

    Provides utilities for saving and replacing user profile images on disk.
    """
    STORAGE_DIR = Path.cwd() / 'storage/profiles'
    BUFFER_SIZE = 1024 * 1024

    @classmethod
    def save_profile_image(cls, file: UploadFile) -> str:
        """
        Save a new profile image.

        Args:
            file (UploadFile): New uploaded file

        Returns:
            str: The new file path
        """
        cls.STORAGE_DIR.mkdir(parents=True, exist_ok=True)

        extension: str = file.filename.split('.')[-1].lower()
        filename: str = f'{uuid4()}.{extension}'
        file_path = cls.STORAGE_DIR / filename

        with file_path.open('wb') as buffer :
            for chunk in iter(lambda: file.file.read(cls.BUFFER_SIZE), b''):
                buffer.write(chunk)

        return f'storage/profiles/{filename}'

    @classmethod
    def replace_profile_image(cls, file: UploadFile, old_file_path: str | None) -> str:
        """
        Replace an existing profile image.
        - Deletes the old file if it exists
        - Saves the new file

        Args:
            file (UploadFile): New uploaded file
            old_file_path (str | None): Existing file path

        Returns:
            str: New file path
        """

        if old_file_path:
            try:
                old_path = Path.cwd() / old_file_path
                if old_path.exists() and old_path.is_file():
                    old_path.unlink()
            except Exception:
                logger.exception("Unexpected error while removing old file path")

        return cls.save_profile_image(file)