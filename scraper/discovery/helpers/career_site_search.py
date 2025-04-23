from duckduckgo_search import DDGS

def get_career_links(company_name: str, limit: int = 5):
    query = f"{company_name} career site job listings"
    results = []

    with DDGS() as ddgs:
        for r in ddgs.text(keywords=query, max_results=limit):
            results.append({
                "title": r.get("title", ""),
                "url": r.get("href", ""),
                "snippet": r.get("body", "")
            })
    return results


def select_correct_site(results):
    print(results)
    
    pass