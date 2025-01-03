from django.http import JsonResponse
from .utils import fetch_sec_fillings
from django.shortcuts import render

def fetch_sec_filings_view(request):
    """
    View ג'נרי שמאפשר לקבל טיקר, סוג דיווח, ותאריכים כפרמטרים ב-Query String.
    דוגמא לכתובת:
    /fetch-sec-filings/?ticker=TSLA&report_type=10-Q&after_date=2023-01-01&before_date=2023-12-31
    """
    
    # קריאת פרמטרים מה-Query (אם לא נשלח פרמטר, נשתמש בערכי ברירת מחדל)
    ticker = request.GET.get('ticker', 'AAPL')
    report_type = request.GET.get('report_type', '10-K')
    after_date = request.GET.get('after_date', '2020-01-01')
    before_date = request.GET.get('before_date', '2021-01-01')
    
    try:
        # קריאה לפונקציה מ-utils
        result = fetch_sec_fillings(ticker, report_type, after_date, before_date)
        return JsonResponse({
            "status": "success",
            "data": result
        })
    except Exception as e:
        return JsonResponse({
            "status": "error",
            "message": str(e)
        }, status=500)




# application/views.py

from django.shortcuts import render
# הסר את השורה הבאה אם קיימת
# from django.contrib.auth.decorators import login_required

# הסר את הדקורטור אם קיים (אם אינך זקוק להגבלת גישה)
# @login_required
def dashboard_view(request):
    return render(request, 'index.html')  # השתמש ב-index.html
