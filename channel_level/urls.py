from django.contrib import admin
from channel_level_1 import views
from django.urls import include, path
from rest_framework import routers

router = routers.DefaultRouter()

urlpatterns = [
    path('', include(router.urls)),
    path(r'segments1/', views.SegmentList.as_view(), name='stocks-list'),
    # path(r'segments/<int:pk>/', views.StockDetail.as_view(), name='stocks-detail'),
    # path(r'segments/<int:pk>/put/', views.put, name='stocks-put'),
    # path('api-auth/', include('rest_framework.urls', namespace='rest_framework')),
    # path('admin/', admin.site.urls),
]