from django.contrib import admin
from main.aa import data
from import_export.admin import ImportExportModelAdmin
# Register your models here.


@admin.register(data)
class DataAdmin(ImportExportModelAdmin):
    pass
