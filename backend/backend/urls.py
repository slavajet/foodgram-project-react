from django.contrib import admin
from django.urls import include, path
from django.views.generic import TemplateView

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/', include('api.urls')),
    path('api/docs/redoc.html', TemplateView.as_view(template_name='redoc.html'), name='redoc'),  # noqa: E501
]
