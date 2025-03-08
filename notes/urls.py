from django.urls import path
from . import views

app_name = 'notes'

urlpatterns = [
    path('', views.note_list, name='note_list'),
    path('upload/', views.note_upload, name='note_upload'),
    path('<int:pk>/', views.note_detail, name='note_detail'),
    path('<int:pk>/download/', views.download_note, name='download_note'),
    path('<int:pk>/edit/', views.edit_note, name='edit_note'),
    path('<int:pk>/delete/', views.delete_note, name='delete_note'),
] 