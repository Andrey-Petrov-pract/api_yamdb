from django.conf import settings
from django.contrib.auth.models import AbstractUser
from django.contrib.auth.tokens import default_token_generator
from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models
from django.db.models.signals import post_save
from django.dispatch import receiver


class User(AbstractUser):
    ROLE_CHOISE = [
        ('user', 'User'),
        ('admin', 'Administrator'),
        ('moderator', 'Moderator'),
    ]

    username = models.CharField(
        'Логин',
        max_length=150,
        unique=True,
        blank=False,
    )
    email = models.EmailField(
        'e-mail',
        max_length=254,
        unique=True,
        blank=False,
    )
    bio = models.TextField('Биография', blank=True,)
    role = models.CharField(
        'Роль',
        default='user',
        choices=ROLE_CHOISE,
        max_length=10
    )
    first_name = models.CharField('Имя', max_length=150, blank=True,)
    last_name = models.CharField('Фамилия', max_length=150, blank=True,)
    confirmation_code = models.CharField(max_length=50, default="no code")

    class Meta:
        verbose_name = 'Польователь'
        verbose_name_plural = 'Польователи'
        ordering = ('username',)

    def __str__(self):
        return self.username

    @property
    def is_admin(self):
        return self.role == 'admin'

    @property
    def is_user(self):
        return self.role == 'user'

    @property
    def is_moderator(self):
        return self.role == 'moderator'

    @receiver(post_save, sender=settings.AUTH_USER_MODEL)
    def create_confirmation_code(
        sender,
        instance=None,
        created=False,
        **kwards
    ):
        if created:
            confirmation_code = default_token_generator.make_token(
                instance
            )
            instance.confirmation_code = confirmation_code
            instance.save()


class Category(models.Model):
    name = models.CharField(
        max_length=100,
        verbose_name='Название'
    )
    slug = models.SlugField(
        unique=True,
        verbose_name='Идентификатор'
    )

    class Meta:
        ordering = ('name',)
        verbose_name = 'Категория'
        verbose_name_plural = 'Категории'

    def __str__(self):
        return self.name


class Genre(models.Model):
    name = models.CharField(
        max_length=100,
        verbose_name='Название'
    )
    slug = models.SlugField(
        unique=True,
        verbose_name='Идентификатор'
    )

    class Meta:
        verbose_name = 'Жанр'
        verbose_name_plural = 'Жанры'
        ordering = ('name',)


class Title(models.Model):
    name = models.CharField(
        db_index=True,
        max_length=100,
        verbose_name='Название'
    )
    year = models.IntegerField(
        db_index=True,
        verbose_name='Дата выхода',
    )
    category = models.ForeignKey(
        Category,
        db_index=True,
        on_delete=models.SET_NULL,
        related_name='titles',
        null=True,
        verbose_name='Категория'
    )
    description = models.TextField(
        null=True,
        blank=True,
        verbose_name='Описание',
    )
    genre = models.ManyToManyField(
        Genre,
        verbose_name='Жанр',
        through='GenreTitle',
    )

    class Meta:
        verbose_name = 'Произведение'
        verbose_name_plural = 'Произведения'
        ordering = ('name',)

    def __str__(self):
        return self.name


class GenreTitle(models.Model):
    title = models.ForeignKey(
        Title,
        on_delete=models.CASCADE,
        verbose_name='Произведение'
    )
    genre = models.ForeignKey(
        Genre,
        on_delete=models.CASCADE,
        verbose_name='Жанр'
    )

    class Meta:
        verbose_name = 'Произведение и жанр'
        verbose_name_plural = 'Произведения и жанры'
        constraints = [
            models.UniqueConstraint(
                fields=['title', 'genre'],
                name='unique_genre'
            )
        ]

    def __str__(self):
        return f'{self.title}, {self.genre}'


class Review(models.Model):
    title = models.ForeignKey(
        Title,
        db_index=True,
        on_delete=models.CASCADE,
        related_name='reviews',
        null=True
    )
    text = models.TextField(verbose_name='Текст отзыва')
    author = models.ForeignKey(
        User,
        verbose_name="Автор",
        on_delete=models.CASCADE,
        related_name='reviews'
    )
    score = models.IntegerField(
        'Рейтинг произведения',
        validators=(
            MinValueValidator(1),
            MaxValueValidator(10)
        ),
    )
    pub_date = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = 'Отзыв'
        verbose_name_plural = 'Отзывы'
        constraints = [
            models.UniqueConstraint(
                fields=('title', 'author', ),
                name='unique review'
            )]
        ordering = ('pub_date',)

    def __str__(self):
        return self.text


class Comment(models.Model):
    review = models.ForeignKey(
        Review,
        db_index=True,
        on_delete=models.CASCADE,
        related_name='comments',
    )
    text = models.TextField(
        verbose_name='Текст комментария',
    )
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='comments',
        verbose_name='Автор комментария',
    )
    pub_date = models.DateTimeField(
        verbose_name='Дата публикации',
        auto_now_add=True
    )

    class Meta:
        ordering = ('-pub_date', )

    def __str__(self):
        return self.text
