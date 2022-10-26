from django.conf import settings
from django.contrib import admin
from django.urls import include, path
from rest_framework import permissions
from drf_yasg.views import get_schema_view
from drf_yasg import openapi
admin.site.site_header = 'Park-n-Go'
admin.site.site_title = 'Park-n-Go'
admin.site.index_title = 'Park-n-Go.ng'


schema_view = get_schema_view(
   openapi.Info(
      title="Park-n-Go",
      default_version='v1',
      description="API for hackathon Park-n-Go  project",
      contact=openapi.Contact(email="anthonyolowuxx6@gmail.com"),
   ),
   public=True,
   permission_classes=[permissions.AllowAny],
)

urlpatterns = [
    path('admin/', admin.site.urls),
    path('Pn-G/accounts/', include('Hackathon_users.urls')),
    path('Park-n-Go/', include('Hackathon_app.urls')),
    path('', schema_view.with_ui('swagger', cache_timeout=0), name='schema-swagger-ui'),

]

if settings.DEBUG:
    import debug_toolbar
    urlpatterns = [
        path('__debug__/', include(debug_toolbar.urls)),
    ] + urlpatterns
