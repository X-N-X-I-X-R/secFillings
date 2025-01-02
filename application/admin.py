from django.contrib import admin
from .models import SECFiling

@admin.register(SECFiling)
class SECFilingAdmin(admin.ModelAdmin):
    list_display = ('ticker', 'report_type', 'fiscal_year', 'created_at')
    search_fields = ('ticker', 'report_type')
