import json
import os
from typing import Any, Dict, List

import requests

# class HeadHunter:
#     def __init__(self):
#         self.url = "https://api.hh.ru/employers"
#         self.headers = {'User-Agent': 'Course_work'}  # нужно по условию
#
#     def get_employers(self, keyword):
#         params = {
#             'text': keyword,
#             'per_page': 10
#         }
#         response = requests.get(self.url, params=params, headers=self.headers)
#         data = response.json()
#         print(data)
#         return data



class HeadHunterAPI:
    def __init__(self):
        base_dir = os.path.dirname(os.path.dirname(__file__))
        self.data_file = os.path.join(base_dir, "data", "data.json")

    def get_employers(self) -> List[Dict[str, Any]]:
        """Возвращает список всех работодателей из JSON"""
        with open(self.data_file, "r", encoding="utf-8") as f:
            data = json.load(f)

        employers_map = {}
        for item in data.get("items", []):
            emp = item.get("employer", {})
            emp_id = emp.get("id")
            if emp_id and emp_id not in employers_map:
                employers_map[emp_id] = {"id": int(emp_id), "name": emp.get("name", "Unknown")}
        return list(employers_map.values())

    def get_vacancies(self, employer_id: int) -> List[Dict[str, Any]]:
        """Возвращает вакансии конкретного работодателя"""
        with open(self.data_file, "r", encoding="utf-8") as f:
            data = json.load(f)

        vacancies = []
        for item in data.get("items", []):
            emp = item.get("employer", {})
            if int(emp.get("id", 0)) == employer_id:
                salary = item.get("salary") or {}
                vacancies.append(
                    {
                        "name": item.get("name", ""),
                        "salary_from": salary.get("from"),
                        "salary_to": salary.get("to"),
                        "url": item.get("alternate_url", ""),
                    }
                )
        return vacancies
