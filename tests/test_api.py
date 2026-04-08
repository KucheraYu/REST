import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import Session
from sqlalchemy.pool import StaticPool

from main import Base, CommentModel, PostModel, UserModel, app, get_db

engine = create_engine(
    "sqlite:///:memory:",
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)


def override_get_db():
    db = Session(engine)
    try:
        yield db
    finally:
        db.close()


app.dependency_overrides[get_db] = override_get_db

client = TestClient(app)


@pytest.fixture(autouse=True)
def setup_db():
    Base.metadata.create_all(bind=engine)
    yield
    Base.metadata.drop_all(bind=engine)


class TestAuth:
    def test_register_success(self):
        resp = client.post(
            "/auth/register",
            json={"name": "Test User", "email": "test@test.com", "password": "123456"},
        )
        assert resp.status_code == 201
        data = resp.json()
        assert "access_token" in data
        assert data["user"]["email"] == "test@test.com"

    def test_register_duplicate_email(self):
        client.post(
            "/auth/register",
            json={"name": "A", "email": "dup@test.com", "password": "123456"},
        )
        resp = client.post(
            "/auth/register",
            json={"name": "B", "email": "dup@test.com", "password": "123456"},
        )
        assert resp.status_code == 400

    def test_login_success(self):
        client.post(
            "/auth/register",
            json={"name": "Login", "email": "login@test.com", "password": "pass"},
        )
        resp = client.post(
            "/auth/login",
            json={"email": "login@test.com", "password": "pass"},
        )
        assert resp.status_code == 200
        assert "access_token" in resp.json()

    def test_login_wrong_password(self):
        client.post(
            "/auth/register",
            json={"name": "X", "email": "x@test.com", "password": "correct"},
        )
        resp = client.post(
            "/auth/login",
            json={"email": "x@test.com", "password": "wrong"},
        )
        assert resp.status_code == 401

    def test_me_authenticated(self):
        token = _register_and_get_token(client, email="me@test.com")
        resp = client.get("/auth/me", headers={"Authorization": f"Bearer {token}"})
        assert resp.status_code == 200
        assert resp.json()["email"] == "me@test.com"

    def test_me_unauthenticated(self):
        resp = client.get("/auth/me")
        assert resp.status_code in (401, 403)


class TestUsersCRUD:
    def test_create_user(self):
        token = _register_and_get_token(client)
        resp = client.post(
            "/users",
            json={"name": "Alice", "email": "alice@test.com", "password": "123"},
            headers={"Authorization": f"Bearer {token}"},
        )
        assert resp.status_code == 201
        assert resp.json()["name"] == "Alice"

    def test_list_users_pagination(self):
        token = _register_and_get_token(client)
        for i in range(5):
            client.post(
                "/users",
                json={"name": f"U{i}", "email": f"u{i}@test.com", "password": "123"},
                headers={"Authorization": f"Bearer {token}"},
            )
        resp = client.get(
            "/users?page=1&limit=3",
            headers={"Authorization": f"Bearer {token}"},
        )
        assert resp.status_code == 200
        data = resp.json()
        assert len(data["data"]) == 3
        assert data["total"] >= 5
        assert data["page"] == 1
        assert data["limit"] == 3

    def test_list_users_sorting(self):
        token = _register_and_get_token(client)
        client.post(
            "/users",
            json={"name": "Zebra", "email": "z@test.com", "password": "123"},
            headers={"Authorization": f"Bearer {token}"},
        )
        client.post(
            "/users",
            json={"name": "Apple", "email": "a2@test.com", "password": "123"},
            headers={"Authorization": f"Bearer {token}"},
        )
        resp = client.get(
            "/users?sort=name",
            headers={"Authorization": f"Bearer {token}"},
        )
        names = [u["name"] for u in resp.json()["data"]]
        assert names == sorted(names, key=str.lower)

    def test_list_users_filtering(self):
        token = _register_and_get_token(client)
        client.post(
            "/users",
            json={"name": "Ivan", "email": "ivan@test.com", "password": "123"},
            headers={"Authorization": f"Bearer {token}"},
        )
        client.post(
            "/users",
            json={"name": "Petro", "email": "petro@test.com", "password": "123"},
            headers={"Authorization": f"Bearer {token}"},
        )
        resp = client.get(
            "/users?name=Ivan",
            headers={"Authorization": f"Bearer {token}"},
        )
        assert resp.status_code == 200
        assert len(resp.json()["data"]) == 1
        assert resp.json()["data"][0]["name"] == "Ivan"

    def test_get_user_nested(self):
        token = _register_and_get_token(client, email="nested@test.com")
        me = client.get("/auth/me", headers={"Authorization": f"Bearer {token}"})
        user_id = me.json()["id"]

        client.post(
            "/posts",
            json={"title": "P1", "content": "Hello"},
            headers={"Authorization": f"Bearer {token}"},
        )

        resp = client.get(
            f"/users/{user_id}",
            headers={"Authorization": f"Bearer {token}"},
        )
        assert resp.status_code == 200
        assert len(resp.json()["posts"]) == 1
        assert resp.json()["posts"][0]["title"] == "P1"

    def test_update_user(self):
        token = _register_and_get_token(client)
        me = client.get("/auth/me", headers={"Authorization": f"Bearer {token}"})
        user_id = me.json()["id"]

        resp = client.put(
            f"/users/{user_id}",
            json={"name": "UpdatedName"},
            headers={"Authorization": f"Bearer {token}"},
        )
        assert resp.status_code == 200
        assert resp.json()["name"] == "UpdatedName"

    def test_delete_user(self):
        token = _register_and_get_token(client, email="del@test.com")
        me = client.get("/auth/me", headers={"Authorization": f"Bearer {token}"})
        user_id = me.json()["id"]

        resp = client.delete(
            f"/users/{user_id}",
            headers={"Authorization": f"Bearer {token}"},
        )
        assert resp.status_code == 204

        resp = client.get(
            f"/users/{user_id}",
            headers={"Authorization": f"Bearer {token}"},
        )
        assert resp.status_code == 401


class TestPostsCRUD:
    def test_create_post(self):
        token = _register_and_get_token(client)
        resp = client.post(
            "/posts",
            json={"title": "My Post", "content": "Body"},
            headers={"Authorization": f"Bearer {token}"},
        )
        assert resp.status_code == 201
        assert resp.json()["title"] == "My Post"

    def test_list_posts_with_comments(self):
        token = _register_and_get_token(client, email="pc@test.com")
        p = client.post(
            "/posts",
            json={"title": "Post with comments"},
            headers={"Authorization": f"Bearer {token}"},
        )
        post_id = p.json()["id"]

        client.post(
            "/comments",
            json={"text": "Nice!", "post_id": post_id},
            headers={"Authorization": f"Bearer {token}"},
        )

        resp = client.get(f"/posts/{post_id}", headers={"Authorization": f"Bearer {token}"})
        assert resp.status_code == 200
        assert len(resp.json()["comments"]) == 1

    def test_update_post(self):
        token = _register_and_get_token(client)
        p = client.post(
            "/posts",
            json={"title": "Old"},
            headers={"Authorization": f"Bearer {token}"},
        )
        post_id = p.json()["id"]

        resp = client.put(
            f"/posts/{post_id}",
            json={"title": "New"},
            headers={"Authorization": f"Bearer {token}"},
        )
        assert resp.status_code == 200
        assert resp.json()["title"] == "New"

    def test_delete_post(self):
        token = _register_and_get_token(client)
        p = client.post(
            "/posts",
            json={"title": "To delete"},
            headers={"Authorization": f"Bearer {token}"},
        )
        post_id = p.json()["id"]

        resp = client.delete(
            f"/posts/{post_id}",
            headers={"Authorization": f"Bearer {token}"},
        )
        assert resp.status_code == 204


class TestCommentsCRUD:
    def test_create_comment(self):
        token = _register_and_get_token(client)
        p = client.post(
            "/posts",
            json={"title": "For comment"},
            headers={"Authorization": f"Bearer {token}"},
        )
        post_id = p.json()["id"]

        resp = client.post(
            "/comments",
            json={"text": "Great post", "post_id": post_id},
            headers={"Authorization": f"Bearer {token}"},
        )
        assert resp.status_code == 201
        assert resp.json()["text"] == "Great post"

    def test_create_comment_post_not_found(self):
        token = _register_and_get_token(client)
        resp = client.post(
            "/comments",
            json={"text": "Nope", "post_id": 9999},
            headers={"Authorization": f"Bearer {token}"},
        )
        assert resp.status_code == 400

    def test_list_comments_filtering(self):
        token = _register_and_get_token(client, email="cf@test.com")
        p1 = client.post(
            "/posts",
            json={"title": "P1"},
            headers={"Authorization": f"Bearer {token}"},
        )
        p2 = client.post(
            "/posts",
            json={"title": "P2"},
            headers={"Authorization": f"Bearer {token}"},
        )
        client.post(
            "/comments",
            json={"text": "C1", "post_id": p1.json()["id"]},
            headers={"Authorization": f"Bearer {token}"},
        )
        client.post(
            "/comments",
            json={"text": "C2", "post_id": p2.json()["id"]},
            headers={"Authorization": f"Bearer {token}"},
        )

        resp = client.get(
            f"/comments?post_id={p1.json()['id']}",
            headers={"Authorization": f"Bearer {token}"},
        )
        assert resp.status_code == 200
        assert len(resp.json()["data"]) == 1

    def test_delete_comment(self):
        token = _register_and_get_token(client)
        p = client.post(
            "/posts",
            json={"title": "X"},
            headers={"Authorization": f"Bearer {token}"},
        )
        c = client.post(
            "/comments",
            json={"text": "Del", "post_id": p.json()["id"]},
            headers={"Authorization": f"Bearer {token}"},
        )
        resp = client.delete(
            f"/comments/{c.json()['id']}",
            headers={"Authorization": f"Bearer {token}"},
        )
        assert resp.status_code == 204


class TestComplexScenario:
    """Integration test: complex scenario — result of one call
    is used as input for another."""

    def test_full_workflow(self):
        token = _register_and_get_token(client, email="flow@test.com")

        me = client.get("/auth/me", headers={"Authorization": f"Bearer {token}"})
        user_id = me.json()["id"]

        post = client.post(
            "/posts",
            json={"title": "Chain", "content": "Step 1"},
            headers={"Authorization": f"Bearer {token}"},
        )
        post_id = post.json()["id"]

        comment = client.post(
            "/comments",
            json={"text": "Chained comment", "post_id": post_id},
            headers={"Authorization": f"Bearer {token}"},
        )
        comment_id = comment.json()["id"]

        user = client.get(
            f"/users/{user_id}",
            headers={"Authorization": f"Bearer {token}"},
        )
        assert user.status_code == 200
        assert len(user.json()["posts"]) == 1
        assert len(user.json()["posts"][0]["comments"]) == 1
        assert user.json()["posts"][0]["comments"][0]["id"] == comment_id


def _register_and_get_token(
    client, name="Test", email="test@example.com", password="123456"
):
    resp = client.post(
        "/auth/register",
        json={"name": name, "email": email, "password": password},
    )
    return resp.json()["access_token"]
