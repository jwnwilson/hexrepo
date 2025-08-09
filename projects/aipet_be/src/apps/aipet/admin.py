from django.contrib import admin

from .models.aipet import Aipet


# Register your models here.
class AipetAdmin(admin.ModelAdmin):
    pass


admin.site.register(Aipet, AipetAdmin)
