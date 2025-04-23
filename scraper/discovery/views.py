from django.http import JsonResponse
from django.views.decorators.http import require_GET
from .helpers.career_site_search import get_career_links, select_correct_site

@require_GET
def discover_view(request):
    company = request.GET.get("q", "").strip()
    if not company:
        return JsonResponse({"error": "Missing query ?q=..."}, status=400)

    try:
        results = get_career_links(company, limit=5)
        print(f"Results for {company}: {results}") 
        final_site = select_correct_site(results)
        print(f"Final site for {company}: {final_site}")
        return JsonResponse({
            "company": company,
            "results": results
        })
    except Exception as e:
        return JsonResponse({"error": str(e)}, status=500)
