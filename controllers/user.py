from models.User import UserModel


class UserController():
    def get_all(self):
        all_users = UserModel.find_all()

        return all_users