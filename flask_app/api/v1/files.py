"""File download and management API endpoints."""

import logging
import uuid
import shutil
from pathlib import Path

from flask import Blueprint, send_file, Response
from flask import current_app as app

from ...auth_utils import auth
from ...utils.api_utils import APIResponse, handle_api_error
from assasdb import AssasDatabaseManager, AssasDatabaseHandler

logger = logging.getLogger("assas_app")

files_bp = Blueprint("files", __name__)


class FileService:
    """Service class for file operations."""

    @staticmethod
    def get_database_manager() -> AssasDatabaseManager:
        """Get database manager instance."""
        return AssasDatabaseManager(
            database_handler=AssasDatabaseHandler(
                database_name=app.config["MONGO_DB_NAME"],
            )
        )


@files_bp.route("/datacite/<uuid:system_uuid>", methods=["GET"])
@auth.login_required
def get_datacite_json(system_uuid: uuid.UUID) -> Response:
    """GET /files/datacite/{system_uuid} - Retrieve DataCite JSON for a dataset.

    The JSON files are stored on LSDF, one per system_uuid.
    """
    try:
        datacite_folder = Path(
            app.config.get("DATACITE_FOLDER", "/mnt/ASSAS/datacite_json")
        )
        json_path = datacite_folder / f"{system_uuid}_datacite.json"
        logger.info(f"Looking for DataCite JSON at: {json_path}")

        if not json_path.exists():
            return APIResponse.not_found("DataCite JSON not found for this system_uuid")

        with open(json_path, "r", encoding="utf-8") as f:
            datacite_json = f.read()

        logger.info(f"Serving DataCite JSON: {json_path}")

        return Response(
            datacite_json,
            mimetype="application/json",
        )

    except Exception as e:
        return handle_api_error(
            e, f"Failed to retrieve DataCite JSON for {system_uuid}"
        )


@files_bp.route("/download/<uuid:dataset_id>", methods=["GET"])
@auth.login_required
def download_dataset_file(dataset_id: uuid.UUID) -> Response:
    """GET /files/download/{dataset_id} - Download HDF5 file for dataset."""
    try:
        manager = FileService.get_database_manager()
        document = manager.get_database_entry_by_uuid(dataset_id)

        if not document:
            return APIResponse.not_found("Dataset not found")

        filepath = document.get("system_result")
        if not filepath:
            return APIResponse.not_found("File path not found for dataset")

        file_path = Path(filepath)
        if not file_path.exists():
            return APIResponse.not_found("File does not exist on disk")

        logger.info(f"Serving file download: {filepath}")

        return send_file(
            filepath,
            download_name=f"dataset_{dataset_id}.h5",
            as_attachment=True,
            mimetype="application/octet-stream",
        )

    except Exception as e:
        return handle_api_error(e, f"Failed to download file for dataset {dataset_id}")


@files_bp.route("/archive/<uuid:dataset_id>", methods=["GET"])
@auth.login_required
def download_dataset_archive(dataset_id: uuid.UUID) -> Response:
    """GET /files/archive/{dataset_id} - Download archive for dataset."""
    try:
        dataset_id_str = str(dataset_id)
        tmp_folder = app.config.get("TMP_FOLDER", "/tmp")
        tmp_download_folder = Path(tmp_folder) / f"download_{dataset_id_str}"
        archive_path = tmp_download_folder / f"download_{dataset_id_str}.zip"

        if not archive_path.exists():
            return APIResponse.not_found("Archive not found or expired")

        logger.info(f"Serving archive download: {archive_path}")

        def remove_after_send() -> None:
            """Remove temporary files after sending."""
            try:
                shutil.rmtree(tmp_download_folder)
                logger.info(f"Cleaned up temporary folder: {tmp_download_folder}")
            except Exception as e:
                logger.error(f"Error cleaning up {tmp_download_folder}: {e}")

        response = send_file(
            archive_path,
            download_name=f"dataset_{dataset_id_str}.zip",
            as_attachment=True,
            mimetype="application/zip",
        )

        # Schedule cleanup (you might want to use a background task for this)
        # remove_after_send()  # Comment out if causing issues

        return response

    except Exception as e:
        return handle_api_error(
            e, f"Failed to download archive for dataset {dataset_id}"
        )


@files_bp.route("/info/<uuid:dataset_id>", methods=["GET"])
@auth.login_required
def get_file_info(dataset_id: uuid.UUID) -> Response:
    """GET /files/info/{dataset_id} - Get file information for dataset."""
    try:
        manager = FileService.get_database_manager()
        document = manager.get_database_entry_by_uuid(dataset_id)

        if not document:
            return APIResponse.not_found("Dataset not found")

        filepath = document.get("system_result")
        file_info = {
            "dataset_id": str(dataset_id),
            "filepath": filepath,
            "exists": Path(filepath).exists() if filepath else False,
            "size": document.get("system_size"),
            "size_hdf5": document.get("system_size_hdf5"),
        }

        if filepath and Path(filepath).exists():
            file_path = Path(filepath)
            file_info.update(
                {
                    "file_size_bytes": file_path.stat().st_size,
                    "last_modified": file_path.stat().st_mtime,
                }
            )

        return APIResponse.success({"file_info": file_info})

    except Exception as e:
        return handle_api_error(e, f"Failed to get file info for dataset {dataset_id}")
