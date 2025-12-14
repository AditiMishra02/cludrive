from flask import Blueprint, request, jsonify
from ..models import db, User, File
from app.utils.jwt_helper import decode_token

# S3 helper imports
from app.utils.s3_helper import (
    upload_file_to_s3,
    generate_presigned_url,
    s3_client,
    AWS_S3_BUCKET
)

files_bp = Blueprint('files', __name__)


# -------------------------
# Upload File
# -------------------------
@files_bp.route('/upload', methods=['POST'])
def upload_file():
    auth_header = request.headers.get('Authorization')
    if not auth_header:
        return jsonify({"msg": "Missing token"}), 401

    token = auth_header.split(" ")[1]
    user_data = decode_token(token)
    if not user_data:
        return jsonify({"msg": "Invalid or expired token"}), 401

    user = User.query.get(user_data["user_id"])
    if not user:
        return jsonify({"msg": "User not found"}), 404

    if 'file' not in request.files:
        return jsonify({"msg": "No file uploaded"}), 400

    file = request.files['file']

    # ---- File Size Validation ----
    file.seek(0, 2)  # Move cursor to end of file to get size
    file_size = file.tell()
    file.seek(0)  # Reset cursor back to start for upload

    MAX_SIZE = 10 * 1024 * 1024  # 10 MB

    if file_size > MAX_SIZE:
       return jsonify({"msg": "File too large. Max allowed size is 10 MB"}), 400

    # ---- File Type Validation ----
    import os
    allowed_extensions = {
    "jpg", "jpeg", "png", "pdf",
    "txt", "doc", "docx",
    "csv", "zip", "mp4"
    }

    file_ext = os.path.splitext(file.filename)[1].lower().replace(".", "")

    if file_ext not in allowed_extensions:
        return jsonify({
        "msg": f"File type not allowed: .{file_ext}",
        "allowed_types": list(allowed_extensions)
    }), 400

    # ---- Magic Byte Validation (Real File Type Check) ----
    import imghdr

    file_bytes = file.read(2048)  # Read first 2 KB to inspect signature
    file.seek(0)  # Reset cursor

    # Detect image type using imghdr
    detected_type = imghdr.what(None, file_bytes)

    if file_ext in ["jpg", "jpeg", "png"]:
     	if detected_type not in ["jpeg", "png"]:
        	return jsonify({"msg": "Invalid image file content"}), 400

    # Additional strong checks for PDF
    if file_ext == "pdf":
        if not file_bytes.startswith(b"%PDF"):
                return jsonify({"msg": "Invalid PDF file"}), 400


    # Upload to S3
    s3_key = upload_file_to_s3(file, file.filename, user.id)
    url = generate_presigned_url(s3_key)

    # Save file metadata in DB
    new_file = File(
        user_id=user.id,
        filename=file.filename,
        s3_key=s3_key
    )
    db.session.add(new_file)
    db.session.commit()

    return jsonify({
        "msg": "File uploaded successfully",
        "filename": file.filename,
        "url": url,
        "id": new_file.id
    }), 201


# -------------------------
# List User Files
# -------------------------
@files_bp.route('/files', methods=['GET'])
def list_files():
    auth_header = request.headers.get('Authorization')
    if not auth_header:
        return jsonify({"msg": "Missing token"}), 401

    token = auth_header.split(" ")[1]
    user_data = decode_token(token)
    if not user_data:
        return jsonify({"msg": "Invalid or expired token"}), 401

    user = User.query.get(user_data["user_id"])
    if not user:
        return jsonify({"msg": "User not found"}), 404

    files = File.query.filter_by(user_id=user.id).all()

    result = []
    for f in files:
        result.append({
            "id": f.id,
            "filename": f.filename,
            "uploaded_at": f.uploaded_at.strftime("%Y-%m-%d %H:%M:%S"),
            "url": generate_presigned_url(f.s3_key)
        })

    return jsonify(result), 200


# -------------------------
# Delete File
# -------------------------
@files_bp.route('/files/<int:file_id>', methods=['DELETE'])
def delete_file(file_id):
    auth_header = request.headers.get('Authorization')
    if not auth_header:
        return jsonify({"msg": "Missing token"}), 401

    token = auth_header.split(" ")[1]
    user_data = decode_token(token)
    if not user_data:
        return jsonify({"msg": "Invalid or expired token"}), 401

    file = File.query.get(file_id)
    if not file:
        return jsonify({"msg": "File not found"}), 404

    # Check owner
    if file.user_id != user_data["user_id"]:
        return jsonify({"msg": "Not allowed"}), 403

    # Delete from S3
    s3_client.delete_object(
        Bucket=AWS_S3_BUCKET,
        Key=file.s3_key
    )

    # Delete from DB
    db.session.delete(file)
    db.session.commit()

    return jsonify({"msg": "File deleted successfully"}), 200

