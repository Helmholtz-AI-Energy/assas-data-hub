"""Routes for parent Flask app."""

import logging
import uuid
import shutil

from flask import session, redirect, send_file, request, jsonify
from flask import current_app as app
from pathlib import Path

from .auth_utils import (
    auth,
    users,
)  # Assuming users is a dictionary defined in auth_utils.py

from assasdb import AssasDatabaseManager, AssasDatabaseHandler

logger = logging.getLogger("assas_app")


@app.route("/login")
@auth.login_required
def check_user():
    """Route to verify user authentication and display user information."""
    current_user = auth.current_user()
    user_info = users.get(current_user)

    if user_info:
        logger.info(f"User {current_user} has been authenticated.")
        return jsonify(
            message=f"Hello, {current_user}!",
            email=user_info["email"],
            institute=user_info["institute"],
            role=user_info["role"],
        )
    else:
        return jsonify(error="User information not found"), 404


@app.route("/logout", methods=["GET"])
@auth.login_required
def logout():
    """Log out the current user by clearing the session."""
    current_user = auth.current_user()
    logger.info(f"Logging out user: {current_user}")

    # Clear the session
    session.clear()

    response = jsonify(message="You have been logged out.")
    response.status_code = 401

    return response


@app.route("/")
@auth.login_required
def from_root_to_home():
    """Redirect from the root URL to the home page of the application."""
    logger.info("Redirecting from root to home page.")
    return redirect("/assas_app/home")


@app.route("/assas_app")
@auth.login_required
def from_app_to_home():
    """Redirect from the /assas_app URL to the home page of the application."""
    logger.info("Redirecting from /assas_app to home page.")
    return redirect("/assas_app/home")


@app.route("/assas_app/")
@auth.login_required
def from_app_with_slash_to_home():
    """Redirect from the /assas_app/ URL to the home page of the application."""
    logger.info("Redirecting from /assas_app/ to home page.")
    return redirect("/assas_app/home")


@app.route("/assas_app/hdf5_file", methods=["GET"])
@auth.login_required
def get_data_file():
    """Handle the request to retrieve a data file based on the provided UUID."""
    logger.info("Received request for data file.")

    args = request.args
    system_uuid = uuid.UUID(args.get("uuid", type=str))

    manager = AssasDatabaseManager(
        database_handler=AssasDatabaseHandler(
            database_name=app.config["MONGO_DB_NAME"],
        )
    )
    document = manager.get_database_entry_by_uuid(system_uuid)

    if document is None:
        logger.error(f"No document found for UUID {system_uuid}.")
        return jsonify(error="Document not found"), 404

    logger.info(f"Retrieving data file for UUID {system_uuid}.")
    filepath = document["system_result"]
    file = Path(filepath)

    if file.exists():
        logger.info(f"Handle request of {str(file)}.")

        return send_file(
            path_or_file=filepath,
            download_name=f"dataset_{system_uuid}.h5",
            as_attachment=True,
        )


@app.route("/assas_app/hdf5_download", methods=["GET"])
@auth.login_required
def get_download_archive():
    """Handle the request to download an archive based on the provided UUID."""
    logger.info("Received request for download archive.")

    args = request.args
    system_uuid = args.get("uuid", type=str)

    tmp_folder = app.config["TMP_FOLDER"]
    tmp_download_folder = f"{tmp_folder}/download_{system_uuid}"

    filepath = f"{tmp_download_folder}/download_{system_uuid}.zip"
    file = Path(filepath)

    if file.exists():
        logger.info(f"Handle request of {str(file)}.")

        response = send_file(
            path_or_file=filepath,
            download_name=f"download_{system_uuid}.zip",
            as_attachment=True,
        )

        try:
            shutil.rmtree(tmp_download_folder)
            logger.info(f"Temporary folder {tmp_download_folder} has been deleted.")

        except Exception as e:
            logger.error(f"Error deleting file {filepath}: {e}")

        return response

    else:
        logger.error(f"File not found: {filepath}.")
        return jsonify(error="Document not found"), 404


@app.route("/assas_app/query_meta_data", methods=["GET"])
@auth.login_required
def query_data():
    """Handle the request to retrieve meta data variables based on provided UUID."""
    args = request.args
    logger.info(f"Received request with arguments: {args}")

    system_uuid = uuid.UUID(args.get("uuid", type=str))

    manager = AssasDatabaseManager(
        database_handler=AssasDatabaseHandler(
            database_name=app.config["MONGO_DB_NAME"],
        )
    )
    document = manager.get_database_entry_by_uuid(system_uuid)
    if document is None:
        logger.error(f"No document found for UUID {system_uuid}.")
        return jsonify(error="Document not found"), 404

    logger.info(f"Retrieving meta data for UUID {system_uuid}.")
    filepath = document["system_result"]
    meta_data_variables = document["meta_data_variables"]
    logger.info(f"Filepath: {filepath}")
    logger.info(f"Meta data variables: {meta_data_variables}")

    return jsonify(
        {
            "meta_data_variables": meta_data_variables,
        }
    )
