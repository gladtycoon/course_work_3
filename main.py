from src.db_manager import DBManager
from src.hh_api import HeadHunterAPI


def main():
    DBManager.recreate_database()

    api = HeadHunterAPI()
    db = DBManager()

    print("Создание таблиц...")
    db.create_tables()

    print("Заполнение базы данных...")
    db.fill_from_api(api)

    print("\n=== Компании и количество вакансий ===")
    for name, count in db.get_companies_and_vacancies_count():
        print(f"{name}: {count}")

    print("\n=== Средняя зарплата ===")
    avg = db.get_avg_salary()
    print(f"{avg:.2f}" if avg else "Нет данных")

    print("\n=== Вакансии с зарплатой выше средней ===")
    for vac in db.get_vacancies_with_higher_salary():
        print(vac[2])  # название вакансии

    print("\n=== Вакансии с ключевым словом 'Python' ===")
    for vac in db.get_vacancies_with_keyword("Python"):
        print(vac[2])

    db.close()


if __name__ == "__main__":
    main()
