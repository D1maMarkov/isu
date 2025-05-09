from django.db import models

from entities.user import UserRole
from utils.security.password_hasher import PasswordHasher
from django.utils import timezone


class Batch(models.Model):
    class Meta:
        verbose_name = "Партия"
        verbose_name_plural = "Партия"

    def __str__(self):
        return f"Партия: {self.id}"


class Materials(models.Model):
    name = models.CharField(max_length=100, verbose_name="Название материала")
    quantity = models.IntegerField(verbose_name="Количество на складе")
    features = models.CharField(max_length=255, verbose_name="Характеристики материала")
    price = models.FloatField(verbose_name="Цена за единицу")
    supplier = models.CharField(max_length=100, verbose_name="Название поставщика")

    class Meta:
        verbose_name = "Материалы"
        verbose_name_plural = "Материалы"

    def __str__(self):
        return self.name


WorkerStatuses = (
    ("", ""),
    ("", "")
)

class User(models.Model):
    fullname = models.CharField(max_length=100, verbose_name="ФИО")
    batch = models.ForeignKey(Batch, on_delete=models.CASCADE)
    date_begin = models.DateField(verbose_name="Дата начала работы")
    date_end = models.DateField(verbose_name="Дата окончания работы")

    status = models.CharField(max_length=50, verbose_name="Статус")

    login = models.CharField(unique=True, max_length=50)
    hash_password = models.CharField(max_length=50)
    role = models.CharField(choices=UserRole.values_list, max_length=50)

    password_hasher = PasswordHasher()

    #def save(self, *args, **kwargs):
    #    if not self.pk:
    #        self.hash_password = self.password_hasher.hash_password(self.hash_password)
    #    super().save(*args, **kwargs)

    class Meta:
        verbose_name = "Пользователи"
        verbose_name_plural = "Пользователи"

    def __str__(self):
        return f"{self.fullname} - {self.role}"


DocumentStatuses = (
    ("", ""),
    ("", "")
)

CategoryRequests = (
    ("закупка", ""),
    ("согласование", "")
)	
    

class DocumentManagement(models.Model):
    batch = models.ForeignKey(Batch, on_delete=models.CASCADE)
    status = models.CharField(max_length=50, verbose_name="Статус заявки", choices=DocumentStatuses)
    request = models.TextField(verbose_name="Текст заявки")
    category = models.CharField(max_length=50, verbose_name="Тип", choices=CategoryRequests)
    result = models.TextField(verbose_name="Результат обработки заявки")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="Дата и время последнего изменения")
    created_at = models.DateTimeField(default=timezone.now)

    class Meta:
        verbose_name = "Документооборот"
        verbose_name_plural = "Документооборот"

class FinishedProducts(models.Model):
    batch = models.ForeignKey(Batch, on_delete=models.CASCADE)
    product_name = models.CharField(max_length=100, verbose_name="Название изделия")
    size = models.CharField(max_length=10, verbose_name="Размер изделия")
    quantity_product = models.IntegerField(verbose_name="Количество изделий в партии")

    class Meta:
        verbose_name = "Готовая продукция"
        verbose_name_plural = "Готовая продукция"

    def __str__(self):
        return f"{self.batch}: {self.product_name}"


class DefectiveProducts(models.Model):
    batch = models.ForeignKey(Batch, on_delete=models.CASCADE)
    quantity = models.IntegerField(verbose_name="Количество бракованных изделий")
    description = models.CharField(max_length=255, verbose_name="Описание дефекта")
    report = models.CharField(max_length=255, verbose_name="Ссылка на отчёт (файл/заметка)", null=True)

    class Meta:
        verbose_name = "Брак"
        verbose_name_plural = "Брак"

    def __str__(self):
        return f"{self.batch}: {self.description}"


class OveruseOfMaterials(models.Model):
    batch = models.ForeignKey(Batch, on_delete=models.CASCADE)
    material = models.ForeignKey(Materials, on_delete=models.CASCADE)
    quantity = models.IntegerField(verbose_name="Количество перерасхода")

    class Meta:
        verbose_name = "Перерасход материалов"
        verbose_name_plural = "Перерасход материалов"

    def __str__(self):
        return f"{self.batch}: {self.material}"
