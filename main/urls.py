from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from main import views

urlpatterns = [
    path('', views.home, name='home'),
    path('api/contact-submit/', views.contact_submit, name='contact_submit'),
    path('api/newsletter-submit/', views.newsletter_submit, name='newsletter_submit'),
    path('api/formsubmit-webhook/', views.form_submit_webhook, name='formsubmit_webhook'),
]

# SERVE MEDIA FILES ALWAYS (remove the DEBUG check)
urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)