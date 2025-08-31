"""Companion API for handling file uploads and S3 interactions.

Contains routes for creating upload folders, listing uploads,
checking file existence, and signing S3 upload requests.
"""

import boto3
import logging

from flask import Blueprint, request, jsonify
from ...utils.url_utils import get_base_url

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("assas_app")

companion_bp = Blueprint("companion", __name__)
base_url = get_base_url()
print(f"Companion blueprint loaded {base_url}.")
companion_bp.url_prefix = base_url

MINIO_ENDPOINT = "https://assas.scc.kit.edu:9000"
MINIO_ACCESS_KEY = "assas2025"
MINIO_SECRET_KEY = "assas2025"
MINIO_BUCKET = "uploads"


def get_s3_client() -> boto3.client:
    """Create an S3 client for interacting with MinIO."""
    return boto3.client(
        "s3",
        endpoint_url=MINIO_ENDPOINT,
        aws_access_key_id=MINIO_ACCESS_KEY,
        aws_secret_access_key=MINIO_SECRET_KEY,
        verify=True,
    )


def ensure_folder_exists(uuid: str) -> None:
    """Ensure that the S3 folder for the given UUID exists."""
    s3 = get_s3_client()
    folder_key = f"{uuid}/"
    try:
        s3.put_object(Bucket=MINIO_BUCKET, Key=folder_key)
        logger.info(f"Created folder {folder_key} in bucket {MINIO_BUCKET}")
    except Exception as e:
        logger.warning(f"Could not create folder {folder_key}: {e}")


@companion_bp.route("/create-upload-folder", methods=["POST"])
def create_upload_folder() -> jsonify:
    """Create an upload folder for the given UUID."""
    data = request.get_json()
    uuid = data.get("uuid")
    if not uuid:
        return jsonify({"error": "Missing uuid"}), 400
    ensure_folder_exists(uuid)
    return jsonify({"created": True})


@companion_bp.route("/list-uploads", methods=["GET"])
def list_uploads() -> jsonify:
    """List all upload folders (UUIDs) in the S3 bucket."""
    logger.info("Route /list-uploads called.")
    s3 = get_s3_client()
    bucket = MINIO_BUCKET
    # List all "folders" (prefixes) at the root of the bucket
    resp = s3.list_objects_v2(Bucket=bucket, Delimiter="/")
    prefixes = [p["Prefix"].rstrip("/") for p in resp.get("CommonPrefixes", [])]
    return jsonify({"uuids": prefixes})


@companion_bp.route("/check-files", methods=["POST"])
def check_files() -> jsonify:
    """Check the existence of files in the S3 bucket."""
    logger.info("Route /check-files called.")
    data = request.get_json()
    filenames = data.get("files", [])
    uuid = data.get("uuid", "")
    existing_files = []
    s3 = get_s3_client()
    bucket = "uploads"
    for filename in filenames:
        key = f"{uuid}/{filename}" if uuid else filename
        try:
            s3.head_object(Bucket=bucket, Key=key)
            existing_files.append(filename)
        except s3.exceptions.ClientError:
            pass
    return jsonify({"existingFiles": existing_files})


@companion_bp.route("/companion/s3/params", methods=["GET"])
def sign_single_upload() -> jsonify:
    """Sign a single upload request for S3."""
    logger.info("Route /companion/s3/params called")
    data = request.args
    logger.info(f"Request args: {data}")
    filename = data.get("filename")
    uuid = data.get("uuid", "") or data.get("metadata[uuid]", "")
    key = f"{uuid}/{filename}" if uuid else filename
    if not key:
        logger.warning("Missing filename in request args")
        return jsonify({"error": "Missing filename"}), 400

    content_type = data.get("type", "application/octet-stream")
    logger.info(f"Signing upload for {key} with content type {content_type}")
    s3 = get_s3_client()
    url = s3.generate_presigned_url(
        ClientMethod="put_object",
        Params={
            "Bucket": MINIO_BUCKET,
            "Key": key,
            "ContentType": content_type,
        },
        ExpiresIn=3600,
        HttpMethod="PUT",
    )

    return jsonify(
        {"method": "PUT", "url": url, "headers": {"Content-Type": content_type}}
    )


@companion_bp.route("/companion/s3/multipart", methods=["POST"])
def create_multipart() -> jsonify:
    """Create a multipart upload for S3."""
    logger.info("Route /companion/s3/multipart called")
    try:
        data = request.get_json()
        logger.info(f"Received data: {data}")
        if not data or "filename" not in data or "type" not in data:
            logger.warning("Missing filename or type in data")
            return jsonify({"error": "Missing filename or type"}), 400
        filename = data.get("filename")
        uuid = data.get("metadata", {}).get("uuid")
        if uuid:
            filename = f"{uuid}/{filename}"
        content_type = data.get("type")
        s3 = get_s3_client()
        logger.info(
            f"Initiating multipart upload for {filename} "
            f"with content type {content_type}."
        )
        resp = s3.create_multipart_upload(
            Bucket=MINIO_BUCKET, Key=filename, ContentType=content_type
        )

        logger.info(
            "Multipart upload initiated for %s with upload ID %s",
            filename,
            resp["UploadId"],
        )
        return jsonify({"uploadId": resp["UploadId"], "key": filename})
    except Exception as e:
        logger.error("Error in create_multipart: %s", e)
        import traceback

        traceback.print_exc()
        return jsonify({"error": str(e)}), 500


@companion_bp.route(
    "/companion/s3/multipart/<uploadId>/<int:partNumber>", methods=["GET"]
)
def sign_part(uploadId: str, partNumber: int) -> jsonify:
    """Sign a part upload request for S3."""
    logger.info(f"Signing part {partNumber} for upload ID {uploadId}")
    key = request.args["key"]
    logger.info(f"Request args: {request.args}")
    s3 = get_s3_client()
    params = {
        "Bucket": MINIO_BUCKET,
        "Key": key,
        "UploadId": uploadId,
        "PartNumber": partNumber,
    }
    content_type = request.args.get("type")
    if content_type:
        params["ContentType"] = content_type
        logger.info(f"Signing with ContentType: {content_type}")
    logger.info(f"Params for presigned URL: {params}")
    url = s3.generate_presigned_url(
        ClientMethod="upload_part",
        Params=params,
        ExpiresIn=3600,
        HttpMethod="PUT",
    )

    logger.info(f"Generated presigned URL for part {partNumber}: {url}")
    return jsonify({"url": url})


@companion_bp.route("/companion/s3/multipart/<uploadId>/complete", methods=["POST"])
def complete_multipart(uploadId: str) -> jsonify:
    """Complete a multipart upload for S3."""
    key = request.args["key"]
    parts = request.get_json()["parts"]
    s3 = get_s3_client()
    resp = s3.complete_multipart_upload(
        Bucket=MINIO_BUCKET,
        Key=key,
        UploadId=uploadId,
        MultipartUpload={"Parts": parts},
    )
    return jsonify({"location": resp["Location"]})


@companion_bp.route("/companion/s3/multipart/<uploadId>", methods=["DELETE"])
def abort_multipart(uploadId: str) -> jsonify:
    """Abort a multipart upload for S3."""
    key = request.args["key"]
    s3 = get_s3_client()
    try:
        s3.abort_multipart_upload(Bucket=MINIO_BUCKET, Key=key, UploadId=uploadId)
        return jsonify({"aborted": True})
    except Exception as e:
        print("Error aborting multipart upload:", e)
        return jsonify({"error": str(e)}), 500
