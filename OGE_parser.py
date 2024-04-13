import psycopg2
import hashlib
from typing import List, Dict
from bs4 import BeautifulSoup
import requests

# ======================================

class LoginError(Exception):
    def __init__(self):
        self.message = "Неопознанная ошибка регистрации"
        super().__init__(self.message)


class EmailPasswordError(Exception):
    def __init__(self):
        self.message = "Неверный email или пароль"
        super().__init__(self.message)


class GettingTestError(Exception):
    def __init__(self):
        self.message = "Ошибка в получении теста"
        super().__init__(self.message)


class SignError(Exception):
    def __init__(self):
        self.message = "Ошибка генерации запроса регистрации"
        super().__init__(self.message)


class TeacherError(Exception):
    def __init__(self):
        self.message = "Пользователь не является учителем"
        super().__init__(self.message)

class Task:

    def __init__(self, task_dict: Dict[str, str]):
        self.id: str = task_dict['id']
        self.question: str = task_dict['task_text']
        self.difficult: int = self.__convert_dif(task_dict['difficult'])
        self.answer: float = float(task_dict['answer'].replace(',','.'))
        if str(task_dict['pic_ids']) != 'None':
            response = requests.get('https://teacher.examer.ru/i/math_oge/' + str(task_dict['pic_ids']))
            if not response.ok:
                print(response)
            path = 'resources/image/' + str(task_dict['pic_ids']).split('/')[-1]
            with open(path, 'wb') as file:
                file.write(response.content)
            self.image: str = path
        else:
            self.image = None
        if task_dict['add_text'] != 'None':
            self.add_text: str = task_dict['add_text']
        else:
            self.add_text = None

    @staticmethod
    def __convert_dif(grade: str) -> int:
        if grade == 'easy':
            return 1
        elif grade == 'normal':
            return 2
        else:
            return 3


class ExamerTest:

    def __init__(self, test_dict: Dict):
        self.theme: str = test_dict['title']
        self.tasks: Dict[str, Task] = {}
        for task in test_dict['tasks']:
            t = Task(task)
            self.tasks[t.id] = t

    def get_tasks(self) -> List[Task]:
        return list(self.tasks.values())


class Examer(object):
    def __init__(self, email: str, password: str, is_async=True):
        self.MAX_REQUESTS = 20
        self.BASE_URL = "https://examer.ru/"
        self.SIGN_POSTFIX = 'Ic8_31'
        self.session = requests.session()
        self.is_async = is_async
        if email and password:
            self.auth(email, password)

    def auth(self, email: str, password: str):
        response = self.session.get(self.BASE_URL)
        soup = BeautifulSoup(response.content, 'html.parser')
        token = soup.find(id='login-form').find('input', attrs={"name": "_token"})["value"]
        params = self.prepare_auth_request_params(email, password, token)

        headers = {"Referer": self.BASE_URL, "Cookie": response.headers['Set-Cookie']}
        response = self.session.post(self.BASE_URL + 'api/v2/login', headers=headers, data=params)
        if not response.json()['success']:
            if response.json()['error'] == 3:
                raise EmailPasswordError()
            elif response.json()['error'] == 101:
                raise SignError()
            else:
                raise LoginError()
        response = self.session.get(self.BASE_URL + 'api/v2/user').json()
        if not response['profile']['is_teacher']:
            raise TeacherError()

    def get_test(self, link: str) -> ExamerTest:
        test_id = link.split('/')[-1]
        test = self.get_questions(test_id)
        return test

    def prepare_auth_request_params(self, email: str, password: str, token: str) -> Dict[str, str]:
        data = {
            '_mail': email,
            '_pass': password,
            "_token": token,
            "source_reg": 'login_popup'
        }
        string = ''.join(sorted(data.values())) + self.SIGN_POSTFIX
        data['s'] = hashlib.md5(string.encode('utf-8')).hexdigest()
        return data

    def get_questions(self, link: str) -> ExamerTest:
        tasks = self.session.get(self.BASE_URL + 'api/v2/teacher/test/student/' + link).json()
        #print(tasks)
        if 'error' in tasks:
            raise GettingTestError()
        return ExamerTest(tasks['test'])


EMAIL = 'baboshinikki90@gmail.com'
PASSWORD = 'qazxsw1234'

# =======================================

if __name__ == '__main__':
    ex = Examer(EMAIL, PASSWORD)

    all_links = [["https://t.examer.ru/47f5e", "https://t.examer.ru/eaf5c", "https://t.examer.ru/b38c9"],
                 ["https://t.examer.ru/b813e", "https://t.examer.ru/9e934", "https://t.examer.ru/1de72"],
                 ["https://t.examer.ru/057d3", "https://t.examer.ru/94a1b", "https://t.examer.ru/0125a"],
                 ["https://t.examer.ru/fc9fb", "https://t.examer.ru/7ad44", "https://t.examer.ru/1b0f3"],
                 ["https://t.examer.ru/e520e", "https://t.examer.ru/1a0fe", "https://t.examer.ru/4190e"],
                 ["https://t.examer.ru/1bb59", "https://t.examer.ru/f4fa1", "https://t.examer.ru/f9202"],
                 ["https://t.examer.ru/493f0", "https://t.examer.ru/a5d37", "https://t.examer.ru/71a32"],
                 ["https://t.examer.ru/e02ce", "https://t.examer.ru/8ffdb", "https://t.examer.ru/0b510"],
                 ["https://t.examer.ru/d6d6d", "https://t.examer.ru/1bdf7", "https://t.examer.ru/f2d81"],
                 ["https://t.examer.ru/81d76", "https://t.examer.ru/f43d8", "https://t.examer.ru/aa459"],
                 ["https://t.examer.ru/6d074", "https://t.examer.ru/e04d0", "https://t.examer.ru/f292a"],
                 ["https://t.examer.ru/be414", "https://t.examer.ru/5df8d", "https://t.examer.ru/2a8e4"],
                 ["https://t.examer.ru/f9602", "https://t.examer.ru/f040d", "https://t.examer.ru/c87c6"],
                 ["https://t.examer.ru/857e6", "https://t.examer.ru/02658", "https://t.examer.ru/2c422"],
                 ["https://t.examer.ru/eeb9a", "https://t.examer.ru/17c43", "https://t.examer.ru/65c86"],
                 ["https://t.examer.ru/4b66a", "https://t.examer.ru/6f9eb", "https://t.examer.ru/b698d"],
                 ["https://t.examer.ru/fb619", "https://t.examer.ru/0e1f2", "https://t.examer.ru/0e1f2"],
                 ["https://t.examer.ru/8ed28", "https://t.examer.ru/b8845", "https://t.examer.ru/c17ee"]]

    conn = psycopg2.connect(user="postgres",
                            password="qazx",
                            host="127.0.0.1",
                            database="test_db",
                            port="5432")

    cursor = conn.cursor()

    for index, links in enumerate(all_links):
        id_topic = index + 1
        for i, link in enumerate(links):
            test = ex.get_test(link)
            if i == 0:
                cursor.execute("INSERT INTO topic (name_topic) VALUES (%s)", (test.theme,))
                conn.commit()
            for task in test.get_tasks():
                t = (id_topic, task.question, task.answer, task.difficult, task.add_text, task.image)
                cursor.execute("INSERT INTO task (topic, question, answer, exp, add_text, image) VALUES (%s, %s, %s, %s, %s, %s)", t)
                conn.commit()
    cursor.close()
    conn.close()