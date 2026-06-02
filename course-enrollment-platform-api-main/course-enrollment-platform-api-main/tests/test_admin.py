def _make_course(client, admin_token, auth_header, code="C1", capacity=5):
    response = client.post(
        "/courses",
        headers=auth_header(admin_token),
        json={"title": "T", "code": code, "capacity": capacity},
    )
    return response.json()


def test_admin_lists_all_enrollments(
    client, admin_token, student_token, auth_header
):
    course = _make_course(client, admin_token, auth_header)
    client.post(
        "/enrollments",
        headers=auth_header(student_token),
        json={"course_id": course["id"]},
    )
    response = client.get(
        "/admin/enrollments", headers=auth_header(admin_token)
    )
    assert response.status_code == 200
    assert len(response.json()) == 1


def test_admin_lists_course_enrollments(
    client, admin_token, student_token, auth_header
):
    course = _make_course(client, admin_token, auth_header)
    client.post(
        "/enrollments",
        headers=auth_header(student_token),
        json={"course_id": course["id"]},
    )
    response = client.get(
        f"/admin/courses/{course['id']}/enrollments",
        headers=auth_header(admin_token),
    )
    assert response.status_code == 200
    assert len(response.json()) == 1


def test_admin_course_enrollments_404(client, admin_token, auth_header):
    response = client.get(
        "/admin/courses/999/enrollments", headers=auth_header(admin_token)
    )
    assert response.status_code == 404


def test_admin_removes_enrollment(
    client, admin_token, student_token, auth_header
):
    course = _make_course(client, admin_token, auth_header)
    enrollment = client.post(
        "/enrollments",
        headers=auth_header(student_token),
        json={"course_id": course["id"]},
    ).json()
    response = client.delete(
        f"/admin/enrollments/{enrollment['id']}",
        headers=auth_header(admin_token),
    )
    assert response.status_code == 204


def test_admin_remove_nonexistent_enrollment(client, admin_token, auth_header):
    response = client.delete(
        "/admin/enrollments/999", headers=auth_header(admin_token)
    )
    assert response.status_code == 404


def test_student_cannot_access_admin_endpoints(
    client, student_token, auth_header
):
    listing = client.get(
        "/admin/enrollments", headers=auth_header(student_token)
    )
    deleting = client.delete(
        "/admin/enrollments/1", headers=auth_header(student_token)
    )
    assert listing.status_code == 403
    assert deleting.status_code == 403


def test_admin_endpoints_require_authentication(client):
    assert client.get("/admin/enrollments").status_code == 401
    assert client.delete("/admin/enrollments/1").status_code == 401
