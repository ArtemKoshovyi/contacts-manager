from django.urls import path
from . import views

app_name = "contacts"

urlpatterns = [
    path("", views.contact_list, name="list"),
    path("add/", views.contact_create, name="add"),
    path("<int:pk>/edit/", views.contact_update, name="edit"),
    path("<int:pk>/delete/", views.contact_delete, name="delete"),
    path("import/", views.contact_import_csv, name="import"),
    path("api/contacts/", views.ContactListCreateAPI.as_view(), name="api_list_create"),
    path("api/contacts/<int:pk>/", views.ContactDetailAPI.as_view(), name="api_detail_update_delete"),
    path("export/", views.contact_export_csv, name="export"),

]