from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('core.urls')),  # Core URLs first
    path('accounts/', include('accounts.urls', namespace='accounts')),
]