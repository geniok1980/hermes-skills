#!/root/scrapling-env/bin/python3
"""Пример парсинга hh.ru через Scrapling для cron-задач.

Поддерживает множественные запросы (несколько категорий).
Использует HTTP Fetcher (без браузера) — быстрый и stealthy.

Запуск: ./hh-vacancies.py
Или в cron: cronjob(action='create', no_agent=True, script='hh-vacancies.py', ...)
"""
from scrapling.fetchers import Fetcher
import re, sys

QUERIES = [
    ("Python-разработчик", "text=python+разработчик&area=113"),
    ("Middle Python", "text=middle+python&area=113"),
]

for category, query in QUERIES:
    url = f"https://hh.ru/search/vacancy?{query}&page=0"
    page = Fetcher.get(url, stealthy_headers=True)

    if page.status != 200:
        print(f"[{category}] Ошибка: статус {page.status}")
        continue

    vacs = page.css('[data-qa="vacancy-serp__vacancy"]')
    if not vacs:
        print(f"[{category}] Нет вакансий")
        continue

    print(f"=== {category} ({len(vacs)} вакансий) ===")
    for v in vacs:
        title = v.css('[data-qa="serp-item__title-text"]::text').get()
        employer = v.css('[data-qa="vacancy-serp__vacancy-employer-text"]::text').get()
        metro = v.css('[data-qa="address-metro-station-name"]::text').get() or \
                v.css('[data-qa="vacancy-serp__vacancy-address"]::text').get() or ''
        exp3 = v.css('[data-qa="vacancy-serp__vacancy-work-experience-between3And6"]::text').get()
        exp1 = v.css('[data-qa="vacancy-serp__vacancy-work-experience-between1And3"]::text').get()
        exp6 = v.css('[data-qa="vacancy-serp__vacancy-work-experience-moreThan6"]::text').get()
        remote = v.css('[data-qa="vacancy-label-work-schedule-remote"]::text').get()
        exp = exp3 or exp1 or exp6 or ''
        
        title_t = title.strip() if title else 'N/A'
        emp_t = employer.strip() if employer else ''
        metro_t = metro.strip() if metro else ''
        exp_t = exp.strip() if exp else ''
        remote_t = remote.strip() if remote else ''

        print(f"  {title_t} | {emp_t} | {metro_t} | {exp_t} | {remote_t}")
    print()
