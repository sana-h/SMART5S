from django.urls import path
from .views import *


urlpatterns =[
path('audits/', AuditList.as_view()),
path('audits/<int:pk>/', AuditDetails.as_view()),
path('audits/<int:pk>/actions/', AuditActionList.as_view()),
path('audits/<int:pk>/zone/',zone),
path('audits/<int:pk>/zone/responsable/',azr),

path('actions/',ActionList.as_view()),
path('actions/<int:pk>/', ActionDetails.as_view()),

path('zones/',ZoneList.as_view()),
path('zones/<int:pk>/',ZoneDetails.as_view()),
path('zones/<int:pk>/responsable/', ZoneResponsableList.as_view()),

path('standards/', StandardList.as_view()),
path('categories/', CategorieList.as_view()),
path('categories/<int:pk>/', CategorieDetails.as_view()),

]
