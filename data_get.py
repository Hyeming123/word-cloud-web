import requests

BASE_URL = 'https://ko.wikipedia.org/w/api.php'

# Wikipedia는 User-Agent 필수
HEADERS = {
    'User-Agent': 'MyWikiBot/1.0 (agrow@example.com)',
}

def search_wikipedia(query: str):
    params = {
        'action': 'query',
        'list': 'search',
        'srsearch': query,
        'format': 'json',
        'utf8': 1,
        'srlimit': 10,
    }
    response = requests.get(BASE_URL, params=params, headers=HEADERS, timeout=10)
    response.raise_for_status()
    data = response.json()

    results = data['query']['search']
    print(f"'{query}' 검색 결과: {len(results)}건\n")

    for i, item in enumerate(results, 1):
        title = item['title']
        snippet = item['snippet'].replace('<span class="searchmatch">', '') \
                                 .replace('</span>', '')
        print(f"{i}. {title}")
        print(f"   {snippet}...")
        print()

    return [item['title'] for item in results]


def get_wikipedia_content(title: str):
    params = {
        'action': 'query',
        'titles': title,
        'prop': 'extracts',
        'exintro': True,
        'explaintext': True,
        'format': 'json',
        'utf8': 1,
    }
    response = requests.get(BASE_URL, params=params, headers=HEADERS, timeout=10)
    response.raise_for_status()
    data = response.json()

    pages = data['query']['pages']
    page = next(iter(pages.values()))

    if 'missing' in page:
        print(f"'{title}' 문서를 찾을 수 없습니다.")
        return ""

    content = page.get('extract', '')
    print(f"=== {page['title']} ===\n")
    print(content[:200] + "...") # Print a snippet for debugging
    return content


def get_wikipedia_url(title: str) -> str:
    encoded = title.replace(' ', '_')
    return f"https://ko.wikipedia.org/wiki/{encoded}"


def get_best_match_content(query: str):
    titles = search_wikipedia(query)
    if not titles:
        return None, ""
    best_title = titles[0]
    content = get_wikipedia_content(best_title)
    return best_title, content


if __name__ == '__main__':
    while True:
        print("\n1. 검색  2. 문서 읽기  3. 종료")
        choice = input("선택: ").strip()

        if choice == '1':
            query = input('검색어: ')
            search_wikipedia(query)

        elif choice == '2':
            title = input('문서 제목 (예: 베이징): ')
            get_wikipedia_content(title)
            print(f"\n🔗 전체 보기: {get_wikipedia_url(title)}")

        elif choice == '3':
            print('종료합니다.')
            break

        else:
            print('1, 2, 3 중에 선택하세요.')