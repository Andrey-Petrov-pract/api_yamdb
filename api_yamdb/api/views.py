from django.shortcuts import get_object_or_404
from django.core.mail import send_mail
from django.db.models import Avg

from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework import filters, permissions, status, viewsets, generics
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework.pagination import PageNumberPagination

from django_filters.rest_framework import DjangoFilterBackend

from .filters import TitleFilter
from .serializers import (
    GenreSerializer, CategorySerializer, UserSerializer, ReviewSerializer,
    CommentSerializer, GetTokenSerializer, SignupSerializer,
    TitleReadSerializer, TitleWriteSerializer
)
from reviews.models import Category, Comment, Genre, Review, Title, User
from .mixins import CreateLisDestroytViewSet
from .permissions import (
    IsAdminOrSuperuser,
    IsAdminModeratorAuthorOrReadOnly,
    IsAdminOrSuperuserOrReadOnly,
    IsAdminUserOrReadOnly
)


class UserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    pagination_class = PageNumberPagination
    permission_classes = (IsAdminOrSuperuser,)
    filter_backends = (filters.SearchFilter,)
    search_fields = ('username', )
    lookup_field = 'username'

    @action(
        methods=['get', 'patch'], url_path='me',
        detail=False, permission_classes=(permissions.IsAuthenticated,)
    )
    def current_user(self, request):
        serializer = UserSerializer(request.user)
        if request.method == 'PATCH':
            serializer = UserSerializer(
                request.user, data=request.data, partial=True
            )
            serializer.is_valid(raise_exception=True)
            if request.user.is_user or request.user.is_moderator:
                if serializer.validated_data.get('role') != request.user.role:
                    serializer.save(role=request.user.role)
                    return Response(serializer.data, status=status.HTTP_200_OK)
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)

        return Response(serializer.data, status=status.HTTP_200_OK)


class CategoryViewSet(CreateLisDestroytViewSet):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer
    pagination_class = PageNumberPagination
    permission_classes = (IsAdminOrSuperuserOrReadOnly,)
    filter_backends = (filters.SearchFilter,)
    search_fields = ('name', )
    lookup_field = 'slug'


class GenreViewSet(CreateLisDestroytViewSet):
    queryset = Genre.objects.all()
    serializer_class = GenreSerializer
    pagination_class = PageNumberPagination
    permission_classes = (IsAdminOrSuperuserOrReadOnly,)
    filter_backends = (filters.SearchFilter,)
    search_fields = ('name', )
    lookup_field = 'slug'


class TitleViewSet(viewsets.ModelViewSet):
    queryset = Title.objects.annotate(
        rating=Avg('reviews__score')
    )
    permission_classes = (IsAdminUserOrReadOnly,)
    filter_backends = (DjangoFilterBackend, )
    filterset_class = TitleFilter

    def get_serializer_class(self):
        if self.action in ('list', 'retrieve'):
            return TitleReadSerializer
        return TitleWriteSerializer


class ReviewViewSet(viewsets.ModelViewSet):
    serializer_class = ReviewSerializer
    permission_classes = (
        IsAdminModeratorAuthorOrReadOnly,
    )

    def get_queryset(self):
        title = get_object_or_404(
            Title,
            id=self.kwargs.get('title_id')
        )
        return title.reviews.all()

    def perform_create(self, serializer):
        title = get_object_or_404(
            Title,
            id=self.kwargs.get('title_id')
        )
        serializer.save(author=self.request.user, title=title)


class CommentViewSet(viewsets.ModelViewSet):
    queryset = Comment.objects.all()
    serializer_class = CommentSerializer
    permission_classes = (
        IsAdminModeratorAuthorOrReadOnly,
    )

    def get_queryset(self):
        review = get_object_or_404(
            Review,
            id=self.kwargs.get('review_id')
        )
        return review.comments.all()

    def perform_create(self, serializer):
        review = get_object_or_404(
            Review, pk=self.kwargs.get('review_id')
        )
        serializer.save(author=self.request.user, review=review)


class APIGetToken(generics.CreateAPIView):
    permission_classes = (permissions.AllowAny,)

    def post(self, request):
        serializer = GetTokenSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = get_object_or_404(
            User,
            username=serializer.validated_data['username']
        )

        if (
            serializer.validated_data[
                'confirmation_code'
            ] == user.confirmation_code
        ):
            token = RefreshToken.for_user(user).access_token
            return Response(
                {'Token': str(token)},
                status=status.HTTP_200_OK
            )
        return Response(
            {'error': 'Неправильный confirmation_code'},
            status=status.HTTP_400_BAD_REQUEST
        )


class APISignup(generics.CreateAPIView):
    permission_classes = (permissions.AllowAny,)

    def post(self, request):
        serializer = SignupSerializer(data=request.data)
        if serializer.is_valid() and request.data['username'] != 'me':
            user = serializer.save()
            send_mail(
                'Код подтверждения',
                f'Ваш логин: {user.username} и confirmation_code: '
                f'{user.confirmation_code}',
                'no_reply@yamdb.ru',
                [user.email],
            )
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
