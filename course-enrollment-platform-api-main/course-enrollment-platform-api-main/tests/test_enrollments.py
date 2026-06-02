def _make_course(client, admin_token, auth_header, code="C1", capacity=2):
    response = client.post(
        "/courses",
        headers=auth_header(admin_token),
        json={"title": "T", "code": code, "capacity": capacity},
    )
    assert response.status_code == 201
    return response.json()


def test_enroll_student_success(client, admin_token, student_token, auth_header):
    course = _make_course(client, admin_token, auth_header)
    response = client.post(
        "/enrollments",
        headers=auth_header(student_token),
        json={"course_id": course["id"]},
    )
    assert response.status_code == 201
    assert response.json()["course_id"] == course["id"]


def test_enroll_requires_student_role(client, admin_token, auth_header):
    course = _make_course(client, admin_token, auth_header)
    response = client.post(
        "/enrollments",
        headers=auth_header(admin_token),
        json={"course_id": course["id"]},
    )
    assert response.status_code == 403


def test_enroll_requires_authentication(client, admin_token, auth_header):
    course = _make_course(client, admin_token, auth_header)
    response = client.post("/enrollments", json={"course_id": course["id"]})
    assert response.status_code == 401


def test_enroll_duplicate_blocked(
    client, admin_token, student_token, auth_header
):
    course = _make_course(client, admin_token, auth_header)
    client.post(
        "/enrollments",
        headers=auth_header(student_token),
        json={"course_id": course["id"]},
    )
    response = client.post(
        "/enrollments",
        headers=auth_header(student_token),
        json={"course_id": course["id"]},
    )
    assert response.status_code == 409


def test_enroll_full_course_blocked(
    client, admin_token, student_token, auth_header
):
    course = _make_course(client, admin_token, auth_header, code="FULL", capacity=1)
    client.post(
        "/enrollments",
        headers=auth_header(student_token),
        json={"course_id": course["id"]},
    )
    client.post(
        "/auth/register",
        json={
            "name": "Two",
            "email": "stu2@x.com",
            "password": "password123",
            "role": "student",
        },
    )
    other_token = client.post(
        "/auth/login", data={"username": "stu2@x.com", "password": "password123"}
    ).json()["access_token"]
    response = client.post(
        "/enrollments",
        headers=auth_header(other_token),
        json={"course_id": course["id"]},
    )
    assert response.status_code == 400
    assert "full" in response.json()["detail"].lower()


def test_enroll_inactive_course_blocked(
    client, admin_token, student_token, auth_header
):
    course = _make_course(client, admin_token, auth_header)
    client.patch(
        f"/courses/{course['id']}/deactivate",
        headers=auth_header(admin_token),
    )
    response = client.post(
        "/enrollments",
        headers=auth_header(student_token),
        json={"course_id": course["id"]},
    )
    assert response.status_code == 400


def test_enroll_nonexistent_course(client, student_token, auth_header):
    response = client.post(
        "/enrollments",
        headers=auth_header(student_token),
        json={"course_id": 999},
    )
    assert response.status_code == 404


def test_deregister_student_success(
    client, admin_token, student_token, auth_header
):
    course = _make_course(client, admin_token, auth_header)
    client.post(
        "/enrollments",
        headers=auth_header(student_token),
        json={"course_id": course["id"]},
    )
    response = client.delete(
        f"/enrollments/{course['id']}", headers=auth_header(student_token)
    )
    assert response.status_code == 204


def test_deregister_nonexistent_enrollment(
    client, admin_token, student_token, auth_header
):
    course = _make_course(client, admin_token, auth_header)
    response = client.delete(
        f"/enrollments/{course['id']}", headers=auth_header(student_token)
    )
    assert response.status_code == 404


def test_deregister_requires_student_role(client, admin_token, auth_header):
    course = _make_course(client, admin_token, auth_header)
    response = client.delete(
        f"/enrollments/{course['id']}", headers=auth_header(admin_token)
    )
    assert response.status_code == 403
