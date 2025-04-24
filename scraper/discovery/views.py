from django.http import JsonResponse
from django.views.decorators.http import require_GET
from .helpers.career_site_search import getCareerLinks, selectCorrectSite

@require_GET
def discoverView(request):
    company = request.GET.get("q", "").strip()
    print(f"Company: {company}")
    if not company:
        return JsonResponse({"error": "Missing query ?q=..."}, status=400)
    
    try:
        results = getCareerLinks(company, limit=5)
        print(f"Results for {company}: {results}")
        final_site = selectCorrectSite(results)
        print(f"Final site for {company}: {final_site}")
        return JsonResponse({
            "company": company,
            "results": results,
            "final": final_site
        })
    except Exception as e:
        return JsonResponse({"error": str(e)}, status=500)
