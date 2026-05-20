import os
from typing import Any, List, Optional, Tuple

import psycopg2
from dotenv import load_dotenv

load_dotenv()


class DBManager:
    """ Класс, который подключается к БД "hh_db" """
    def __init__(self):
        self.conn = psycopg2.connect(
            dbname=os.getenv("DB_NAME", "hh_db"),
            user=os.getenv("DB_USER", "postgres"),
            password=os.getenv("DB_PASSWORD", ""),
            host=os.getenv("DB_HOST", "localhost"),
            port=os.getenv("DB_PORT", "5432"),
        )
        self.cur = self.conn.cursor()

    def create_tables(self) -> None:
        """ Функция создания таблицы """
        self.cur.execute("""
            CREATE TABLE IF NOT EXISTS employers (
                id INTEGER PRIMARY KEY,
                name VARCHAR(255) NOT NULL
            )
        """)
        self.cur.execute("""
            CREATE TABLE IF NOT EXISTS vacancies (
                id SERIAL PRIMARY KEY,
                employer_id INTEGER REFERENCES employers(id),
                name VARCHAR(255) NOT NULL,
                salary_from INTEGER,
                salary_to INTEGER,
                url VARCHAR(255)
            )
        """)
        self.conn.commit()

    def insert_employer(self, employer_id: int, name: str) -> None:
        """ Добавляет работодателя в таблицу """
        self.cur.execute(
            """
            INSERT INTO employers (id, name) VALUES (%s, %s)
            ON CONFLICT (id) DO NOTHING
        """,
            (employer_id, name),
        )
        self.conn.commit()

    def insert_vacancy(
        self, employer_id: int, name: str, salary_from: Optional[int], salary_to: Optional[int], url: str
    ) -> None:
        """ Добавляет вакансию в таблицу """
        self.cur.execute(
            """
            INSERT INTO vacancies (employer_id, name, salary_from, salary_to, url)
            VALUES (%s, %s, %s, %s, %s)
        """,
            (employer_id, name, salary_from, salary_to, url),
        )
        self.conn.commit()

    def get_companies_and_vacancies_count(self) -> List[Tuple[str, int]]:
        """ Получает список всех компаний и количество вакансий у каждой компании """
        self.cur.execute("""
            SELECT e.name, COUNT(v.id) as cnt
            FROM employers e
            LEFT JOIN vacancies v ON e.id = v.employer_id
            GROUP BY e.id, e.name
        """)
        return self.cur.fetchall()

    def get_all_vacancies(self) -> List[Tuple[str, str, Optional[int], Optional[int], str]]:
        """ Получает список всех вакансий с указанием названия компании """
        self.cur.execute("""
            SELECT e.name, v.name, v.salary_from, v.salary_to, v.url
            FROM vacancies v
            JOIN employers e ON v.employer_id = e.id
        """)
        return self.cur.fetchall()

    def get_avg_salary(self) -> Optional[float]:
        """ Получает среднюю зарплату по вакансиям """
        self.cur.execute("""
            SELECT AVG((salary_from + salary_to) / 2.0)
            FROM vacancies
            WHERE salary_from IS NOT NULL AND salary_to IS NOT NULL
        """)
        result = self.cur.fetchone()[0]
        return float(result) if result else None

    def get_vacancies_with_higher_salary(self) -> List[Tuple[Any, ...]]:
        """ Получает список всех вакансий, у которых зарплата выше средней """
        avg = self.get_avg_salary()
        if not avg:
            return []
        self.cur.execute(
            """
            SELECT * FROM vacancies
            WHERE (salary_from + salary_to) / 2.0 > %s
        """,
            (avg,),
        )
        return self.cur.fetchall()

    def get_vacancies_with_keyword(self, keyword: str) -> List[Tuple[Any, ...]]:
        """ Получает список всех вакансий, в названии которых есть введенные пользователем слова """
        self.cur.execute(
            """
            SELECT * FROM vacancies
            WHERE name ILIKE %s
        """,
            (f"%{keyword}%",),
        )
        return self.cur.fetchall()

    def fill_from_api(self, api) -> None:
        employers = api.get_employers()
        for emp in employers:
            self.insert_employer(emp["id"], emp["name"])
            vacancies = api.get_vacancies(emp["id"])
            for vac in vacancies:
                self.insert_vacancy(emp["id"], vac["name"], vac["salary_from"], vac["salary_to"], vac["url"])


    @staticmethod
    def recreate_database():
        """ Удаляет БД hh_db, если она существует, и создаёт заново """
        conn = psycopg2.connect(
            dbname="postgres",
            user=os.getenv("DB_USER", "postgres"),
            password=os.getenv("DB_PASSWORD", ""),
            host=os.getenv("DB_HOST", "localhost"),
            port=os.getenv("DB_PORT", "5432"),
        )
        conn.autocommit = True
        cur = conn.cursor()
        cur.execute("DROP DATABASE IF EXISTS hh_db")
        cur.execute("CREATE DATABASE hh_db")
        cur.close()
        conn.close()


    def close(self) -> None:
        self.cur.close()
        self.conn.close()
