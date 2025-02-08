from locust import HttpUser, constant, task


class GetUsers(HttpUser):
    wait_time = constant(1)

    def on_start(self):
        resp = self.client.post("api/v1/auth/login", json={"username":"test", "password":"TestTest1!"})
        self.client.headers = {"Authorization": f"Bearer {resp.content.decode().replace('\"', '')}"}
    
    @task
    def get_users(self):
        self.client.get("api/v1/user/")
