from django.contrib import admin
from . import models
admin.site.register(models.Users)
admin.site.register(models.Upss)
admin.site.register(models.Address)
admin.site.register(models.Products)
admin.site.register(models.Packages)
admin.site.register(models.Warehouse)
admin.site.register(models.Inventories)
admin.site.register(models.Emails)
admin.site.register(models.Subscriber)

@admin.register(models.Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ('name',)
    list_filter = ('name',)

    list_per_page = 12

# Register your models here.
