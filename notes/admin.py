from django.contrib import admin
from .models import Subject, Note, Comment

@admin.register(Subject)
class SubjectAdmin(admin.ModelAdmin):
    list_display = ['name', 'slug', 'created_at']
    prepopulated_fields = {'slug': ('name',)}
    search_fields = ['name']

@admin.register(Note)
class NoteAdmin(admin.ModelAdmin):
    list_display = ['title', 'author', 'subject', 'view_count', 'download_count', 'created_at']
    list_filter = ['subject', 'created_at', 'author']
    search_fields = ['title', 'description', 'author__username']
    date_hierarchy = 'created_at'

@admin.register(Comment)
class CommentAdmin(admin.ModelAdmin):
    list_display = ['author', 'note', 'created_at']
    list_filter = ['created_at', 'author']
    search_fields = ['content', 'author__username', 'note__title']
