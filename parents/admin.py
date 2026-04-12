from django.contrib import admin
from .models import Parent


@admin.register(Parent)
class ParentAdmin(admin.ModelAdmin):
    list_display = ('id', 'first_name', 'last_name', 'email', 'phone', 'student', 'relationship')
    list_filter = ('relationship', 'created_at')
    search_fields = ('first_name', 'last_name', 'email', 'phone')
    readonly_fields = ('created_at', 'updated_at')
