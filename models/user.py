class User:
    def __init__(self, id_user=None, username=None, password=None, security_question=None, security_answer=None, dcompdate=None):
        self.id_user = id_user
        self.username = username
        self.password = password
        self.security_question = security_question
        self.security_answer = security_answer
        self.dcompdate = dcompdate

    def __str__(self):
        return f"User({self.id_user}, {self.username})"

    def to_dict(self):
        return {
            "id_user": self.id_user,
            "username": self.username,
            "password": self.password,
            "security_question": self.security_question
        }
