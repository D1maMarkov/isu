from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin, UserManager
from django.db import models
from django.utils import timezone

from entities.user import UserRole

DocumentStatuses = (("", ""), ("", ""))

WorkerStatuses = (("", ""), ("", ""))

CategoryRequests = (("закупка", ""), ("согласование", ""))


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
    price = models.IntegerField(verbose_name="Цена за единицу")
    supplier = models.CharField(max_length=100, verbose_name="Название поставщика")

    class Meta:
        verbose_name = "Материалы"
        verbose_name_plural = "Материалы"

    def __str__(self):
        return self.name


class MyUserManager(UserManager):
    use_in_migrations = True

    def _create_user(self, password, **extra_fields):
        user = self.model(**extra_fields)
        user.password = password
        user.save(using=self._db)
        return user

    def create_user(self, password=None, **extra_fields):
        extra_fields.setdefault("is_staff", False)
        extra_fields.setdefault("is_superuser", False)
        return self._create_user(password, **extra_fields)

    def create_superuser(self, password=None, **extra_fields):
        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault("is_superuser", True)

        if extra_fields.get("is_staff") is not True:
            raise ValueError("Superuser must have is_staff=True.")
        if extra_fields.get("is_superuser") is not True:
            raise ValueError("Superuser must have is_superuser=True.")

        return self._create_user(password, **extra_fields)


class User(AbstractBaseUser, PermissionsMixin):
    fullname = models.CharField(max_length=100, verbose_name="ФИО", null=True, blank=True)

    login = models.CharField(unique=True, max_length=50, null=True)
    password = models.CharField(max_length=180)
    role = models.CharField(choices=[(channel.value, channel.value) for channel in UserRole], max_length=50, null=True)

    objects = MyUserManager()

    is_staff = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)

    USERNAME_FIELD = "login"

    class Meta:
        verbose_name = "Пользователи"
        verbose_name_plural = "Пользователи"

    def __str__(self):
        return f"{self.fullname} - {self.role}"

    def check_password(self, raw_password):
        return self.password == raw_password


class Worker(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    batch = models.ForeignKey(Batch, on_delete=models.CASCADE)
    date_begin = models.DateField(verbose_name="Дата начала работы")
    date_end = models.DateField(verbose_name="Дата окончания работы")

    status = models.CharField(max_length=50, verbose_name="Статус")

    class Meta:
        verbose_name = "Работник"
        verbose_name_plural = "Работники"

    def __str__(self):
        return str(self.user)


class DocumentManagement(models.Model):
    batch = models.ForeignKey(Batch, on_delete=models.CASCADE)
    status = models.CharField(max_length=50, verbose_name="Статус заявки", choices=DocumentStatuses)
    request = models.FileField(verbose_name="Текст заявки", upload_to="static/documents/requests/")
    category = models.CharField(max_length=50, verbose_name="Тип", choices=CategoryRequests)
    updated_at = models.DateTimeField(auto_now=True, verbose_name="Дата и время последнего изменения")
    created_at = models.DateTimeField(default=timezone.now)

    class Meta:
        verbose_name = "Документооборот"
        verbose_name_plural = "Документооборот"


class DocumentResult(models.Model):
    document = models.ForeignKey(DocumentManagement, on_delete=models.CASCADE, related_name="results")
    file = models.FileField(verbose_name="Результат обработки заявки", upload_to="static/documents/results/")

    class Meta:
        verbose_name = "Результат заявки"
        verbose_name_plural = "Результаты заявки"


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
    report = models.FileField(
        verbose_name="Ссылка на отчёт (файл/заметка)", null=True, upload_to="static/defects/reports/"
    )

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
