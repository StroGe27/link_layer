from channel_level_1 import views
from django.contrib import admin
from rest_framework import permissions
from django.urls import path
from drf_yasg.views import get_schema_view
from drf_yasg import openapi


schema_view = get_schema_view(
   openapi.Info(
      title="Link layer API",
      default_version='v1',
      description="API description",
      terms_of_service="https://www.google.com/policies/terms/",
      contact=openapi.Contact(email="contact@snippets.local"),
      license=openapi.License(name="BSD License"),
   ),
#    properties
   public=True,
   permission_classes=(permissions.AllowAny,),
)
urlpatterns = [
    path(r'api/link_layer/', views.SegmentList.as_view(), name='stocks-list'),
    path(r'api/swagger/', schema_view.with_ui('swagger', cache_timeout=0), name='schema-swagger-ui'),
    path('swagger.yml', schema_view.without_ui(cache_timeout=0), name='schema-swagger'),
]