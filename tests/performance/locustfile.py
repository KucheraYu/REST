from locust import HttpUser, between, task


class LabAPIUser(HttpUser):
    wait_time = between(1, 2)
    token = None
    user_email = None
    post_id = None

    def on_start(self):
        import random

        suffix = random.randint(10000, 99999)
        self.user_email = f"perf{suffix}@test.com"

        resp = self.client.post(
            "/auth/register",
            json={"name": "PerfUser", "email": self.user_email, "password": "123"},
        )
        self.token = resp.json()["access_token"]

        resp = self.client.post(
            "/posts",
            json={"title": "Perf Post", "content": "Load test"},
            headers={"Authorization": f"Bearer {self.token}"},
        )
        self.post_id = resp.json()["id"]

    @task(3)
    def get_users(self):
        self.client.get(
            "/users?page=1&limit=20",
            headers={"Authorization": f"Bearer {self.token}"},
        )

    @task(3)
    def get_posts(self):
        self.client.get(
            "/posts?page=1&limit=20",
            headers={"Authorization": f"Bearer {self.token}"},
        )

    @task(2)
    def get_single_user(self):
        self.client.get(
            "/auth/me",
            headers={"Authorization": f"Bearer {self.token}"},
        )

    @task(1)
    def complex_chain(self):
        post = self.client.post(
            "/posts",
            json={"title": "Chain", "content": "From load test"},
            headers={"Authorization": f"Bearer {self.token}"},
        )
        if post.status_code == 201:
            new_post_id = post.json()["id"]
            self.client.post(
                "/comments",
                json={"text": "Chained", "post_id": new_post_id},
                headers={"Authorization": f"Bearer {self.token}"},
            )
            self.client.delete(
                f"/posts/{new_post_id}",
                headers={"Authorization": f"Bearer {self.token}"},
            )
