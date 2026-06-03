#!/root/scrapling-env/bin/python3
"""Утренняя подборка заработка — парсинг через Scrapling (no_agent cron script).
В 20x быстрее crawl4ai: 6 сайтов за ~1с вместо 60-90с.
"""
from scrapling.fetchers import Fetcher
from datetime import date
import re, concurrent.futures

SITES = {
    "hh_rkeeper": {
        "url": "https://hh.ru/search/vacancy?text=rkeeper+автоматизация+ресторан&area=113",
        "label": "rkeeper / Автоматизация ресторанов",
    },
    "hh_iiko": {
        "url": "https://hh.ru/search/vacancy?text=iiko+автоматизация+ресторан&area=113",
        "label": "iiko / Автоматизация ресторанов",
    },
    "hh_python": {
        "url": "https://hh.ru/search/vacancy?text=Python+разработчик+удаленная&area=113",
        "label": "Python разработка (удалёнка)",
    },
    "hh_trading_bot": {
        "url": "https://hh.ru/search/vacancy?text=торговый+бот+крипто+трейдинг&area=113",
        "label": "Торговые боты / крипта",
    },
    "hh_devops": {
        "url": "https://hh.ru/search/vacancy?text=DevOps+удаленная+автоматизация&area=113",
        "label": "DevOps / Автоматизация",
    },
    "hh_telegram_bot": {
        "url": "https://hh.ru/search/vacancy?text=Telegram+бот+разработчик&area=113",
        "label": "Telegram-боты",
    },
}


def parse_site(site_info: dict) -> str:
    """Парсит hh.ru через Scrapling HTTP — 0.5-1.5 сек на сайт.
    Использует CSS-селекторы по data-qa атрибутам вместо фильтрации Markdown.
    """
    page = Fetcher.get(site_info["url"], stealthy_headers=True)
    if page.status != 200:
        return f"🔥 {site_info['label']}:\n  — ошибка {page.status}\n\n"

    vacs = page.css('[data-qa="vacancy-serp__vacancy"]')
    if not vacs:
        return f"🔥 {site_info['label']}:\n  — нет результатов\n\n"

    # Зарплаты — единственное поле без data-qa, достаём регуляркой
    raw = page.get_all_text()
    sal_pattern = re.compile(r'(\d[\d\s\u202f]*\d\s*[₽$])')
    salary_lines = sal_pattern.findall(raw)

    output = f"🔥 {site_info['label']} ({len(vacs)} вакансий):\n"
    salaries_used = 0

    for v in vacs[:12]:
        title_el = v.css('[data-qa="serp-item__title-text"]')
        employer_el = v.css('[data-qa="vacancy-serp__vacancy-employer-text"]')
        metro_el = v.css('[data-qa="address-metro-station-name"]')
        addr_el = v.css('[data-qa="vacancy-serp__vacancy-address"]')
        exp1 = v.css('[data-qa="vacancy-serp__vacancy-work-experience-between1And3"]')
        exp2 = v.css('[data-qa="vacancy-serp__vacancy-work-experience-between3And6"]')
        exp3 = v.css('[data-qa="vacancy-serp__vacancy-work-experience-moreThan6"]')
        remote_el = v.css('[data-qa="vacancy-label-work-schedule-remote"]')
        link_el = v.css('a[data-qa="serp-item__title"]')

        title = title_el[0].text.strip() if title_el else '?'
        employer = employer_el[0].text.strip() if employer_el else '?'
        location = metro_el[0].text.strip() if metro_el else (addr_el[0].text.strip() if addr_el else '')
        exp = (exp1[0].text.strip() if exp1 else exp2[0].text.strip() if exp2 else exp3[0].text.strip() if exp3 else '')
        remote = remote_el[0].text.strip() if remote_el else ''
        url = link_el[0].attrib.get('href', '') if link_el else ''

        salary = salary_lines[salaries_used].strip() if salaries_used < len(salary_lines) else ''
        salaries_used += 1

        line = f"  — {title}"
        if employer != '?':
            line += f" | {employer}"
        if location:
            line += f" | {location}"
        if exp:
            line += f" | {exp}"
        if remote:
            line += f" | {remote}"
        if salary:
            line += f" | {salary}"
        if url:
            line += f"\n    {url}"
        output += line + "\n"

    output += "\n"
    return output


def main():
    today = date.today().strftime("%d.%m.%Y")
    output = [f"📅 **Утренняя подборка — {today}**\nПарсинг через Scrapling\n---\n"]

    with concurrent.futures.ThreadPoolExecutor(max_workers=6) as pool:
        results = list(pool.map(parse_site, SITES.values()))

    output.extend(r for r in results if r)

    output.append("---\n💡 **Дополнительно:**\n")
    output.append("  — fl.ru / freelance.ru: требуют авторизации\n")
    output.append("  — kwork.ru: поиск по категориям, а не по строке\n")
    output.append("  — GitHub баунти: метки 'bounty' в релевантных репозиториях\n\n")
    output.append("🎯 **Рекомендация:** откликайся на свежие вакансии сразу — конкуренция высокая\n")

    print('\n'.join(output))


if __name__ == "__main__":
    main()
