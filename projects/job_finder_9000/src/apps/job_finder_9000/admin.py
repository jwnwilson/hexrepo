from django.contrib import admin

from .models.job_finder_9000 import Job_finder_9000


# Register your models here.
class Job_finder_9000Admin(admin.ModelAdmin):
    pass


admin.site.register(Job_finder_9000, Job_finder_9000Admin)
