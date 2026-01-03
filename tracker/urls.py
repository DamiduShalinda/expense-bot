from django.urls import path

from .views import demo_ui, whatsapp_webhook

urlpatterns = [
    path("webhook/whatsapp/", whatsapp_webhook, name="whatsapp-webhook"),
    path("demo/", demo_ui, name="demo-ui"),
]
