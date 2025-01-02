from django.db import models

class SECFiling(models.Model):
    ticker = models.CharField(max_length=10)  # לדוגמה: "AAPL"
    report_type = models.CharField(max_length=10)  # לדוגמה: "10-K"
    fiscal_year = models.DateField()  # לדוגמה: 2024-09-30
    html_content = models.TextField()  # תוכן קובץ ה-HTML
    created_at = models.DateTimeField(auto_now_add=True)  # תאריך יצירת הרשומה
    updated_at = models.DateTimeField(auto_now=True)  # תאריך עדכון הרשומה

    def __str__(self):
        return f"{self.ticker} {self.report_type} {self.fiscal_year}"
