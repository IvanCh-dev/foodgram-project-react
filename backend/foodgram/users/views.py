from django.contrib.auth import get_user_model
from django.shortcuts import get_object_or_404

from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response

from .models import Subscription
from users.serializers import (
    ChangePasswordSerializer, CustomUserCreateSerializer, CustomUserSerializer,
    SubscriptionSerializer)

User = get_user_model()


class CustomUserViewSet(viewsets.ModelViewSet):
    """ViewSet для кастомной модели User."""
    permission_classes = (AllowAny,)
    queryset = User.objects.all()

    def get_serializer_class(self):
        if self.request.method in ('POST', 'PATCH'):
            return CustomUserCreateSerializer
        return CustomUserSerializer

    @action(detail=False, permission_classes=[IsAuthenticated])
    def me(self, request, *args, **kwargs):
        self.object = get_object_or_404(User, pk=request.user.id)
        serializer = self.get_serializer(self.object)
        return Response(serializer.data)

    @action(
        detail=False, methods=['post'], permission_classes=[IsAuthenticated])
    def set_password(self, request, *args, **kwargs):
        '''set_password также хэширует новый пароль'''
        self.object = get_object_or_404(User, pk=request.user.id)
        serializer = ChangePasswordSerializer(data=request.data)
        if serializer.is_valid():
            if not self.object.check_password(
                    serializer.data.get('current_password')):
                return Response({'current_password': ['Wrong password.']},
                                status=status.HTTP_400_BAD_REQUEST)
            self.object.set_password(serializer.data.get('new_password'))
            self.object.save()
            return Response({
                'status': 'password set'}, status=status.HTTP_200_OK)

        return Response(serializer.errors,
                        status=status.HTTP_400_BAD_REQUEST)

    @action(detail=False, permission_classes=[IsAuthenticated])
    def subscriptions(self, request, context={}, *args, **kwargs):
        context['request'] = self.request
        queryset = User.objects.filter(subscribers__user=request.user)
        page = self.paginate_queryset(queryset)
        serializer = SubscriptionSerializer(page, context=context, many=True)
        return self.get_paginated_response(serializer.data)

    @action(detail=True, methods=['post', 'delete'],
            permission_classes=[IsAuthenticated])
    def subscribe(self, request, context={}, *args, **kwargs):
        context['request'] = self.request
        author = get_object_or_404(User, id=kwargs['pk'])
        user = request.user

        if author == user:
            return Response({
                'errors': 'Ошибка, нельзя подписываться на самого себя'},
                status=status.HTTP_400_BAD_REQUEST)

        if request.method == 'POST':
            if Subscription.objects.filter(author=author, user=user).exists():
                return Response({
                    'errors': 'Ошибка, данная подписка уже существует'},
                    status=status.HTTP_400_BAD_REQUEST)

            Subscription.objects.create(author=author, user=user)
            serializer = CustomUserSerializer(
                User.objects.get(id=author.id), context=context)
            return Response(serializer.data, status.HTTP_201_CREATED)

        get_object_or_404(Subscription, author=author,
                          user=user).delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
