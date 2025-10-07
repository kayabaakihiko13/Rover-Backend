from utils import (
    STATUS_CREATED_OR_OK,
    STATUS_OK,
    STATUS_SUCCESS_OR_ACCEPTED,
    STATUS_SUCCESS_OR_ERROR
)

# ========================
# User feature tests
# ========================
def test_register_user(test_client):
    # Hapus dulu user yang sama supaya test bisa dijalankan berulang
    test_client.delete("/users/delete-by-username?username=asep")

    response = test_client.post(
        "/users/register",
        json={
            "firstname": "acep",
            "lastname": "Surocop",
            "username": "asep",
            "email": "asep123@example.com",
            "password": "rahasia123"
        }
    )
    assert response.status_code in STATUS_CREATED_OR_OK, f"Unexpected status: {response.text}"
    data = response.json()
    assert data["username"] == "asep"
    assert data["email"] == "asep123@example.com"

def test_login_user(test_client):
    response = test_client.post(
        "/users/login",
        data={
            "username": "asep",
            "password": "rahasia123"
        }
    )
    assert response.status_code in STATUS_OK, f"Unexpected status: {response.text}"
    data = response.json()
    assert "access_token" in data
    assert data["token_type"] == "bearer"

def test_forget_password(test_client):
    response = test_client.post(
        "/users/forgot-password",
        json={"username": "asep"}
    )
    assert response.status_code in STATUS_SUCCESS_OR_ACCEPTED, f"Unexpected status: {response.text}"

def test_reset_password(test_client):
    fake_token = "fake-reset-token"  # Token dummy
    response = test_client.post(
        "/users/reset-password",
        json={
            "token": fake_token,
            "new_password": "asepganteng",
            "confirm_password": "asepganteng"
        }
    )
    assert response.status_code in STATUS_SUCCESS_OR_ERROR, f"Unexpected status: {response.text}"
