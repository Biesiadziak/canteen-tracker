from duckduckgo_search import DDGS

def search_menu_text():
    try:
        with DDGS() as ddgs:
            query = "site:facebook.com/stolowkaPP/ menu"
            results = list(ddgs.text(query, max_results=3))
            for r in results:
                print(f"Result: {r['body']}")
    except Exception as e:
        print(f"Error: {e}")

search_menu_text()
