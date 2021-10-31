from django.urls import include, path
from rest_framework import routers

from .views import (LoginAPIView, RegistrationAPIView, TicketDeleteAPIView,
                    TicketsContinueCorrespondenceAPIView, TicketsCreateAPIView,
                    TicketsListView, TicketUpdateAPIView, UserDeleteAPIView,
                    UsersListView, UserUpdateAPIView)

app_name = 'support'

router = routers.DefaultRouter()
router.register(r'tickets', TicketsListView)
router.register(r'tickets/<int:pk>', TicketsListView)
router.register(r'users', UsersListView)
router.register(r'users/<int:pk>', UsersListView)

urlpatterns = [
    path('users/signup/', RegistrationAPIView.as_view()),
    path('users/update/<int:pk>/', UserUpdateAPIView.as_view()),
    path('users/login/', LoginAPIView.as_view()),
    path('tickets/new/', TicketsCreateAPIView.as_view()),
    path('tickets/continue-correspondence/', TicketsContinueCorrespondenceAPIView.as_view()),
    path('tickets/update-partial/<int:pk>/', TicketUpdateAPIView.as_view()),
    path('tickets/delete/<int:pk>/', TicketDeleteAPIView.as_view()),
    path('users/delete/<int:pk>/', UserDeleteAPIView.as_view()),

]
urlpatterns += router.urls
