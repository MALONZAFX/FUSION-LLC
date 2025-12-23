from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from main import views

urlpatterns = [
    # TEMPORARY EMERGENCY ROUTE - Comment out when site works
    # path('', views.emergency_home, name='emergency_home'),
    
    # REAL ROUTE - Uncomment when site works
    path('', views.home, name='home'),
    
    
    path('api/contact-submit/', views.contact_submit, name='contact_submit'),
    path('api/newsletter-submit/', views.newsletter_submit, name='newsletter_submit'),
    path('api/formsubmit-webhook/', views.form_submit_webhook, name='formsubmit_webhook'),
   
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)

