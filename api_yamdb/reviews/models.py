from django.core.validators import (
    MaxValueValidator,
    MinValueValidator)
from django.db import models

from users.models import User


class Category(models.Model):
    name = models.CharField("Название категории", max_length=100)
    slug = models.SlugField("Slug категории", max_length=100, unique=True)

    class Meta:
        # поля в админке
        verbose_name = "Категория"
        verbose_name_plural = "Категории"

    def __str__(self):
        return self.title[:79]


class Genre(models.Model):
    name = models.CharField("Название жанра", max_length=100)
    slug = models.SlugField("Slug жанра", max_length=100, unique=True)

    class Meta:
        verbose_name = "Жанр"
        verbose_name_plural = "Жанры"

    def __str__(self):
        return self.title[:79]


class Title(models.Model):
    name = models.CharField("Название произведения", max_length=100)
    year = models.IntegerField("Год выпуска",)
    # если поле пустое - NULL; необязательное поле
    description = models.TextField("Описание", null=True, blank=True)
    # related_name - для использования Genre.title а не Genre.title_set
    # для обратного отношения
    genre = models.ManyToManyField(
        Genre,
        verbose_name="Жанр",
        through="TitleGenre",
    )
    category = models.ForeignKey(
        Category,
        # on_delete - обязательное поле, при удалении объекта категории
        # произведение остаётся
        # для genre on_delete е указываем, так как оно необязательно для
        # ManyToManyField
        on_delete=models.SET_NULL,
        null=True,
        related_name="titles",
        verbose_name="Категория",
    )
    rating = models.IntegerField(
        null=True,
        default=None,
        verbose_name='Рейтинг',
    )

    class Meta:
        verbose_name = "Произведение"
        verbose_name_plural = "Произведения"

    def __str__(self):
        return self.title[:79]


class TitleGenre(models.Model):
    """Модель для реализации отношения ManyToMany title_id -- genre_id"""
    title = models.ForeignKey(
        Title,
        on_delete=models.CASCADE,
        verbose_name="Произведение"
    )
    genre = models.ForeignKey(
        Genre,
        on_delete=models.CASCADE,
        verbose_name="Жанр"
    )

    class Meta:
        verbose_name = "Произведение и жанр"
        verbose_name_plural = "Произведения и жанры"

    def __str__(self):
        return f'{self.title} {self.genre}'


class Review(models.Model):
    text = models.TextField()
    pub_date = models.DateTimeField('Дата публикации', auto_now_add=True)
    author = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name='reviews')
    title = models.ForeignKey(
        Title, on_delete=models.SET_NULL,
        related_name='reviews', blank=True, null=True
    )
    score = models.IntegerField(
        validators=[
            MaxValueValidator(10),
            MinValueValidator(1)
        ]
    )

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=['author', 'title'],
                name='unique_review')
        ]

    def __str__(self):
        return f'{self.text}, {self.score}'

    def __repr__(self):
        return self.text[:100]

    class Meta:
        ordering = ['pub_date']


class Comment(models.Model):
    author = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name='comments')
    review = models.ForeignKey(
        Review, on_delete=models.CASCADE, related_name='comments')
    text = models.TextField()
    created = models.DateTimeField(
        'Дата добавления', auto_now_add=True, db_index=True)
