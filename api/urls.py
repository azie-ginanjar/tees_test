"""api URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/3.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.conf import settings
from django.conf.urls import url
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import path, include, re_path
from django.views.static import serve
from drf_yasg import openapi
from rest_framework import permissions
from rest_framework_simplejwt import views as jwt_views
from drf_yasg.views import get_schema_view

schema_view = get_schema_view(
    openapi.Info(
        title="Tees API",
        default_version='v1',
        description="Tees Backend",
        terms_of_service="https://www.google.com/policies/terms/",
        contact=openapi.Contact(email="contact@snippets.local"),
        license=openapi.License(name="BSD License"),
    ),
    public=True,
    permission_classes=(permissions.AllowAny,),
)

urlpatterns = [
                  path('admin/', admin.site.urls),
                  re_path('api/(?P<version>(v1|v2))/users/', include('user.urls')),
                  re_path('api/(?P<version>(v1|v2))/shirt/', include('shirt.urls')),
                  url(r'^media/(?P<path>.*)$', serve, {'document_root': settings.MEDIA_ROOT, }),
                  path('api/token/', jwt_views.TokenObtainPairView.as_view(), name='token_obtain_pair'),
                  path('api/token/refresh/', jwt_views.TokenRefreshView.as_view(), name='token_refresh'),
                  url(r'^swagger/$', schema_view.with_ui('swagger', cache_timeout=0), name='schema-swagger-ui'),
              ] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
