import io

from app.api import routes_documents


def test_health(client):
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "healthy"}


def test_health_db(client):
    response = client.get("/health/db")
    assert response.status_code == 200
    assert response.json() == {"status": "healthy"}


def test_upload_invalid_file_type(client):
    response = client.post(
        "/api/v1/documents/upload",
        files={"file": ("invalid.jpg", io.BytesIO(b"binary-data"), "image/jpeg")},
    )
    assert response.status_code == 400
    assert "PDF, DOCX, and TXT" in response.json()["detail"]


def test_upload_txt_and_reuse_duplicate_checksum(client, monkeypatch):
    monkeypatch.setattr(routes_documents, "run_document_processing", lambda document_id, reset_outputs=True: None)

    first_response = client.post(
        "/api/v1/documents/upload",
        data={"created_by": "tester"},
        files={"file": ("sample.txt", io.BytesIO(b"hello semantic world"), "text/plain")},
    )
    second_response = client.post(
        "/api/v1/documents/upload",
        data={"created_by": "tester"},
        files={"file": ("sample.txt", io.BytesIO(b"hello semantic world"), "text/plain")},
    )

    assert first_response.status_code == 200
    assert second_response.status_code == 200
    assert first_response.json()["id"] == second_response.json()["id"]
