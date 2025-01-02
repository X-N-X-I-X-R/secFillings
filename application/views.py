from django.http import JsonResponse
from .utils import fetch_sec_fillings

def fetch_sec_filings_view(request):
    # קבלת פרמטרים מה-URL
    ticker = request.GET.get('ticker', 'AAPL')
    report_type = request.GET.get('report_type', '10-K')
    after_date = request.GET.get('after_date', '2020-01-01')
    before_date = request.GET.get('before_date', '2021-01-01')
    
    try:
        # קריאה לפונקציה מ-utils
        result = fetch_sec_fillings(ticker, report_type, after_date, before_date)
        return JsonResponse({"status": "success", "data": result})
    except Exception as e:
        return JsonResponse({"status": "error", "message": str(e)}, status=500)
