from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import *
# Register your models here.


class UserModel(UserAdmin):
    ordering = ('email',)


admin.site.register(CustomUser, UserModel)
admin.site.register(Provider)
admin.site.register(Merchant)
admin.site.register(Compliance)
admin.site.register(Book)
admin.site.register(IssuedBook)
admin.site.register(Library)
# admin.site.register(Subject)
admin.site.register(Questionnaire)
admin.site.register(Session)
