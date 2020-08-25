from conf.settings import admin_users
from models.User import UserModel
from flask_dance.contrib.google import google


class LoginController():
    @classmethod
    def athenticate_user(cls):
        if google.authorized:
            resp = google.get("/oauth2/v2/userinfo")
            email = resp.json()["email"]
            if email in admin_users:
                return True

            user = UserModel.find_by_username(email)
            if user.dept_id == 9:
                return True

        return False