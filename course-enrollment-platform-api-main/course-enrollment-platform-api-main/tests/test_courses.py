def _create_course(client, admin_token, auth_header, code="CS101", capacity=10):
    response = client.post(
        "/courses",
        headers=auth_header(admin_token),
        json={"title": "Intro CS", "code": code, "capacity": capacity},
    )
    assert response.status_code == 201, response.text
    return response.json()


def test_list_active_courses_public(client, admin_token, auth_header):
    _create_course(client, admin_token, auth_header, code="A1")
    response = client.get("/courses")
    assert response.status_code == 200
    assert len(response.json()) == 1


def test_list_excludes_inactive_courses(client, admin_token, auth_header):
    course = _create_course(client, admin_token, auth_header, code="A1")
    client.patch(
        f"/courses/{course['id']}/deactivate",
        headers=auth_header(admin_token),
    )
    response = client.get("/courses")
    assert response.status_code == 200
    assert response.json() == []


def test_get_course_by_id_public(client, admin_token, auth_header):
    course = _create_course(client, admin_token, auth_header, code="A1")
    response = client.get(f"/courses/{course['id']}")
    assert response.status_code == 200
    assert response.json()["code"] == "A1"


def test_get_course_not_found(client):
    assert client.get("/courses/999").status_code == 404


def test_create_course_as_admin(client, admin_token, auth_header):
    response = client.post(
        "/courses",
        headers=auth_header(admin_token),
        json={"title": "T", "code": "X1", "capacity": 5},
    )
    assert response.status_code == 201


def test_create_course_as_student_forbidden(client, student_token, auth_header):
    response = client.post(
        "/courses",
        headers=auth_header(student_token),
        json={"title": "T", "code": "X1", "capacity": 5},
    )
    assert response.status_code == 403


def test_create_course_unauthenticated(client):
    response = client.post(
        "/courses", json={"title": "T", "code": "X1", "capacity": 5}
    )
    assert response.status_code == 401


def test_create_course_duplicate_code(client, admin_token, auth_header):
    _create_course(client, admin_token, auth_header, code="DUP")
    response = client.post(
        "/courses",
        headers=auth_header(admin_token),
        json={"title": "Other", "code": "DUP", "capacity": 5},
    )
    assert response.status_code == 409


def test_create_course_capacity_must_be_positive(client, admin_token, auth_header):
    response = client.post(
        "/courses",
        headers=auth_header(admin_token),
        json={"title": "T", "code": "Z1", "capacity": 0},
    )
    assert response.status_code == 422


def test_update_course_as_admin(client, admin_token, auth_header):
    course = _create_course(client, admin_token, auth_header, code="U1")
    response = client.put(
        f"/courses/{course['id']}",
        headers=auth_header(admin_token),
        json={"title": "New Title"},
    )
    assert response.status_code == 200
    assert response.json()["title"] == "New Title"


def test_update_course_as_student_forbidden(
    client, admin_token, student_token, auth_header
):
    course = _create_course(client, admin_token, auth_header, code="U2")
    response = client.put(
        f"/courses/{course['id']}",
        headers=auth_header(student_token),
        json={"title": "Hack"},
    )
    assert response.status_code == 403


def test_activate_and_deactivate_course(client, admin_token, auth_header):
    course = _create_course(client, admin_token, auth_header, code="A2")
    deactivated = client.patch(
        f"/courses/{course['id']}/deactivate",
        headers=auth_header(admin_token),
    )
    assert deactivated.status_code == 200
    assert deactivated.json()["is_active"] is False

    activated = client.patch(
        f"/courses/{course['id']}/activate",
        headers=auth_header(admin_token),
    )
    assert activated.status_code == 200
    assert activated.json()["is_active"] is True
