"""Serve project files from whitelisted directories."""

import os
from flask import Blueprint, abort, send_from_directory

static_files_bp = Blueprint("static_files", __name__)

ALLOWED_DIRS = {"old files", "old sheets", "docs", "debug_output"}
BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


@static_files_bp.route("/files/<path:filepath>")
def serve_file(filepath):
    if ".." in filepath:
        abort(403, "Path traversal not allowed")

    parts = filepath.split("/", 1)
    if len(parts) < 2:
        abort(404, "File path must include directory and filename")

    top_dir = parts[0]

    # Handle "old files" and "old sheets" (two-word dirs)
    if top_dir == "old" and len(filepath.split("/", 2)) >= 3:
        second = filepath.split("/", 2)[1]
        if f"old {second}" in ALLOWED_DIRS:
            top_dir = f"old {second}"
            parts = [top_dir, filepath.split("/", 2)[2]]

    if top_dir not in ALLOWED_DIRS:
        abort(403, f"Directory '{top_dir}' is not accessible")

    file_path = os.path.join(BASE_DIR, parts[0], parts[1])
    directory = os.path.dirname(file_path)
    filename = os.path.basename(file_path)

    if not os.path.isfile(file_path):
        abort(404, f"File not found: {filepath}")

    return send_from_directory(directory, filename)
