from django.contrib import admin
from django.contrib.auth.hashers import make_password
from .models import User

@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    list_display = ('username', 'email', 'phone_number', 'created_date')
    search_fields = ('username', 'email', 'phone_number')
    readonly_fields = ('created_date',)

    def save_model(self, request, obj, form, change):
        if change:  # If the object already exists
            original = User.objects.get(pk=obj.pk)
            if original.password != obj.password:  # If password was changed
                obj.password = make_password(obj.password)
        super().save_model(request, obj, form, change)

admin.site.site_header = "PromptPay Admin"
admin.site.site_title = "PromptPay Admin Panel"
admin.site.index_title = "Welcome to PromptPay Admin"
