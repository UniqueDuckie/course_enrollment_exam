from app.config import settings
from app.rate_limit import limiter


def _make_course(client, admin_token, auth_header, code="C1", capacity=5):
    response = client.post(
        "/courses",
        headers=auth_header(admin_token),
        json={"title": "T", "code": code, "capacity": capacity},
    )
    assert response.status_code == 201, response.text
    return response.json()


def test_pagination_on_courses(client, admin_token, auth_header):
    for i in range(5):
        _make_course(client, admin_token, auth_header, code=f"P{i}")
    response = client.get("/courses?skip=2&limit=2")
    assert response.status_code == 200
    body = response.json()
    assert len(body) == 2
    assert body[0]["code"] == "P2"


def test_pagination_on_admin_enrollments(
    client, admin_token, student_token, auth_header
):
    courses = [
        _make_course(client, admin_token, auth_header, code=f"E{i}") for i in range(3)
    ]
    for course in courses:
        client.post(
            "/enrollments",
            headers=auth_header(student_token),
            json={"course_id": course["id"]},
        )
    response = client.get(
        "/admin/enrollments?skip=1&limit=1", headers=auth_header(admin_token)
    )
    assert response.status_code == 200
    assert len(response.json()) == 1


def test_soft_delete_course_excluded_from_public_list(
    client, admin_token, auth_header
):
    course = _make_course(client, admin_token, auth_header, code="SD1")
    response = client.delete(
        f"/courses/{course['id']}", headers=auth_header(admin_token)
    )
    assert response.status_code == 204
    response = client.get("/courses")
    assert response.status_code == 200
    assert response.json() == []
    response = client.get(f"/courses/{course['id']}")
    assert response.status_code == 404


def test_soft_delete_course_requires_admin(
    client, admin_token, student_token, auth_header
):
    course = _make_course(client, admin_token, auth_header, code="SD2")
    response = client.delete(
        f"/courses/{course['id']}", headers=auth_header(student_token)
    )
    assert response.status_code == 403


def test_re_enroll_after_dereg_restores_row(
    client, admin_token, student_token, auth_header
):
    course = _make_course(client, admin_token, auth_header)
    enrolled = client.post(
        "/enrollments",
        headers=auth_header(student_token),
        json={"course_id": course["id"]},
    ).json()
    client.delete(
        f"/enrollments/{course['id']}", headers=auth_header(student_token)
    )
    re_enrolled = client.post(
        "/enrollments",
        headers=auth_header(student_token),
        json={"course_id": course["id"]},
    )
    assert re_enrolled.status_code == 201
    assert re_enrolled.json()["id"] == enrolled["id"]


def test_admin_list_excludes_deleted_by_default(
    client, admin_token, student_token, auth_header
):
    course = _make_course(client, admin_token, auth_header)
    client.post(
        "/enrollments",
        headers=auth_header(student_token),
        json={"course_id": course["id"]},
    )
    client.delete(
        f"/enrollments/{course['id']}", headers=auth_header(student_token)
    )
    default_list = client.get(
        "/admin/enrollments", headers=auth_header(admin_token)
    ).json()
    assert default_list == []
    included = client.get(
        "/admin/enrollments?include_deleted=true",
        headers=auth_header(admin_token),
    ).json()
    assert len(included) == 1
    assert included[0]["course_id"] == course["id"]


def test_audit_log_records_enroll_and_deregister(
    client, admin_token, student_token, auth_header
):
    course = _make_course(client, admin_token, auth_header)
    client.post(
        "/enrollments",
        headers=auth_header(student_token),
        json={"course_id": course["id"]},
    )
    client.delete(
        f"/enrollments/{course['id']}", headers=auth_header(student_token)
    )
    response = client.get(
        "/admin/audit-logs", headers=auth_header(admin_token)
    )
    assert response.status_code == 200
    actions = {entry["action"] for entry in response.json()}
    assert "enrolled" in actions
    assert "deregistered" in actions


def test_audit_log_records_admin_removal(
    client, admin_token, student_token, auth_header
):
    course = _make_course(client, admin_token, auth_header)
    enrollment = client.post(
        "/enrollments",
        headers=auth_header(student_token),
        json={"course_id": course["id"]},
    ).json()
    client.delete(
        f"/admin/enrollments/{enrollment['id']}",
        headers=auth_header(admin_token),
    )
    response = client.get(
        "/admin/audit-logs", headers=auth_header(admin_token)
    )
    actions = [entry["action"] for entry in response.json()]
    assert "admin_removed" in actions


def test_audit_log_requires_admin(client, student_token, auth_header):
    response = client.get(
        "/admin/audit-logs", headers=auth_header(student_token)
    )
    assert response.status_code == 403


def test_rate_limit_on_register(client):
    limit_value = int(settings.rate_limit_register.split("/")[0])
    payload = {
        "name": "X",
        "email": "anyone@x.com",
        "password": "password123",
        "role": "student",
    }
    for i in range(limit_value):
        payload["email"] = f"user{i}@x.com"
        response = client.post("/auth/register", json=payload)
        assert response.status_code == 201
    payload["email"] = "overflow@x.com"
    response = client.post("/auth/register", json=payload)
    assert response.status_code == 429
