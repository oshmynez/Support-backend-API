from rest_framework import generics, mixins, status, viewsets
from rest_framework.generics import GenericAPIView
from rest_framework.mixins import UpdateModelMixin
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from .models import Ticket, User
from .permission import IsAdminUser
from .renderers import TicketJSONRenderer, UserJSONRenderer
from .serializers import (LoginSerializer, RegistrationSerializer,
                          TicketSerializer, UserSerializer)
from .tasks import send_email


class TicketsListView(viewsets.ModelViewSet):
    queryset = Ticket.objects.all().order_by('id')
    permission_classes = (AllowAny,)
    serializer_class = TicketSerializer


class TicketsCreateAPIView(generics.ListCreateAPIView):
    queryset_tickets = Ticket.objects.all().order_by('id')
    queryset_users = User.objects.all().order_by('id')
    permission_classes = (IsAuthenticated,)
    serializer_class = TicketSerializer
    renderer_classes = (TicketJSONRenderer,)

    def create(self, request, *args, **kwargs):
        ticket = request.data.get('ticket', {})
        if 'text' not in ticket.keys() and len(ticket['text']) < 0:
            msg = {'msg': 'enter a field \' text \''}
            return Response(msg, status=status.HTTP_404_NOT_FOUND)

        ticket['sender'] = request.user.id
        if 'recipient' in ticket.keys() and len(ticket['recipient']) > 0:
            try:
                user = self.queryset_users.get(username=ticket['recipient'])
            except User.DoesNotExist:
                msg = {'msg': 'Recipient with this username\'' + str(
                    ticket['recipient']) + '\' matching query does not exist'}
                return Response(msg, status=status.HTTP_404_NOT_FOUND)
            ticket['recipient'] = user.id
        else:
            msg = {'msg': 'enter a field \' recipient \''}
            return Response(msg, status=status.HTTP_404_NOT_FOUND)

        serializer = self.serializer_class(data=ticket)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        try:
            user_sender = self.queryset_users.get(id=request.user.id)

            user_recipient = self.queryset_users.get(id=ticket['recipient'])
        except User.DoesNotExist:
            msg = {'msg': 'user_sender or user_recipient matching query does not exist'}
            return Response(msg, status=status.HTTP_404_NOT_FOUND)
        user_sender.opened_dialogs.append(serializer.data['id'])
        user_recipient.opened_dialogs.append(serializer.data['id'])
        user_sender.save()
        user_recipient.save()
        #send_email.delay(user_recipient.id, ticket['text'])

        return Response(serializer.data, status=status.HTTP_201_CREATED)


class TicketsContinueCorrespondenceAPIView(generics.ListCreateAPIView):
    queryset_tickets = Ticket.objects.all().order_by('id')
    queryset_users = User.objects.all().order_by('id')

    permission_classes = (IsAuthenticated,)
    serializer_class = TicketSerializer
    renderer_classes = (TicketJSONRenderer,)

    def create(self, request, *args, **kwargs):
        ticket = request.data.get('ticket', {})
        if 'text' not in ticket.keys() and len(ticket['text']) < 0:
            msg = {'msg': 'enter a field \' text \''}
            return Response(msg, status=status.HTTP_404_NOT_FOUND)

        if 'recipient' not in ticket.keys() or self.queryset_users.filter(username=ticket['recipient']).count <= 0:
            msg = {'msg': 'enter a field \' recipient \''}
            return Response(msg, status=status.HTTP_404_NOT_FOUND)

        if 'code_correspondence' not in ticket.keys() or self.queryset_tickets.filter(
                code_correspondence=ticket['code_correspondence']).count() <= 0:
            msg = {'msg': 'enter a field \' code_correspondence \''}
            return Response(msg, status=status.HTTP_404_NOT_FOUND)

        ticket['sender'] = request.user.id

        user = User.objects.get(username=ticket['recipient'])
        ticket['recipient'] = user.id

        serializer = self.serializer_class(data=ticket)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)


class TicketUpdateAPIView(GenericAPIView, UpdateModelMixin):
    queryset = Ticket.objects.all().order_by('id')
    permission_classes = (IsAdminUser,)
    serializer_class = TicketSerializer
    renderer_classes = (TicketJSONRenderer,)

    def put(self, request, *args, **kwargs):
        return self.partial_update(request, *args, **kwargs)


class TicketDeleteAPIView(APIView):
    queryset = Ticket.objects.all().order_by('id')
    permission_classes = (IsAdminUser,)
    renderer_classes = (TicketJSONRenderer,)

    def delete(self, request, pk, format=None):
        try:
            ticket = Ticket.objects.get(pk=pk)
            ticket.delete()
            msg = {'msg': 'Ticket with id \'' + str(pk) + '\' deleted'}
        except Ticket.DoesNotExist:
            msg = {'msg': 'Ticket with id \'' + str(pk) + '\' matching query does not exist'}
            return Response(msg, status=status.HTTP_404_NOT_FOUND)
        return Response(msg, status=status.HTTP_204_NO_CONTENT)


class UsersListView(viewsets.ModelViewSet):
    queryset = User.objects.all().order_by('id')
    serializer_class = UserSerializer
    permission_classes = (IsAdminUser,)


class UserDeleteAPIView(APIView):
    queryset = User.objects.all().order_by('id')
    permission_classes = (IsAdminUser,)
    renderer_classes = (UserJSONRenderer,)

    def delete(self, request, pk, format=None):
        try:
            user = User.objects.get(pk=pk)
            user.delete()
            msg = {'msg': 'User with id \'' + str(pk) + '\' deleted'}
        except User.DoesNotExist:
            msg = {'msg': 'user with id \'' + str(pk) + '\' matching query does not exist'}
            return Response(msg, status=status.HTTP_404_NOT_FOUND)
        return Response(msg, status=status.HTTP_204_NO_CONTENT)


class UserUpdateAPIView(GenericAPIView, UpdateModelMixin):
    queryset = User.objects.all().order_by('id')
    permission_classes = (IsAdminUser,)
    serializer_class = UserSerializer
    renderer_classes = (UserJSONRenderer,)

    def put(self, request, *args, **kwargs):
        return self.partial_update(request, *args, **kwargs)


class LoginAPIView(APIView):
    permission_classes = (AllowAny,)
    authentication_classes = ()
    serializer_class = LoginSerializer

    def post(self, request):
        user = request.data.get('user', {})

        serializer = self.serializer_class(data=user)
        if serializer.is_valid():
            response_data = serializer.save()
            response = Response()
            response.set_cookie('Token', response_data['access'], httponly=False)
            response.data = response_data
            response.status_code = status.HTTP_200_OK
            return response
        msg = {'msg': 'User with email ' + user['email'] + 'and password ' + user['password'] + ' does\'t exist'}

        return Response(msg, status=status.HTTP_401_UNAUTHORIZED)


class RegistrationAPIView(APIView):
    permission_classes = (AllowAny,)
    authentication_classes = ()
    serializer_class = RegistrationSerializer
    renderer_classes = (UserJSONRenderer,)

    def post(self, request):
        user = request.data.get('user', {})
        serializer = self.serializer_class(data=user)
        serializer.is_valid(raise_exception=True)
        serializer.save()

        return Response(serializer.data, status=status.HTTP_201_CREATED)
