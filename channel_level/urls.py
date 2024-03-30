from channel_level_1 import views
from django.contrib import admin
from rest_framework import permissions
from django.urls import path
from drf_yasg.views import get_schema_view
from drf_yasg import openapi


schema_view = get_schema_view(
   openapi.Info(
      title="Link layer",
      default_version='v1',
      description="API для кодирования/декодирования сегментов, а также создание/исправление ошибок в сегменте и потеря их",
   ),
#    properties
   public=True,
   permission_classes=(permissions.AllowAny,),
)
urlpatterns = [
    path(r'link_layer/', views.SegmentList.as_view(), name='stocks-list'),
    path(r'swagger/', schema_view.with_ui('swagger', cache_timeout=0), name='schema-swagger-ui'),
    path('swagger.yaml', schema_view.without_ui(cache_timeout=0), name='schema-swagger'),
]