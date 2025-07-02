import uuid

from tortoise import fields
from tortoise.models import Model


class LegalEntity(Model):
    id = fields.UUIDField(pk=True, default=uuid.uuid4)
    full_name = fields.CharField(max_length=255, null=True)
    short_name = fields.CharField(max_length=255)
    inn = fields.CharField(max_length=12)
    kpp = fields.CharField(max_length=9, null=True)
    ogrn = fields.CharField(max_length=15, unique=True)
    vat_rate = fields.IntField(default=0)
    address = fields.CharField(max_length=255, null=True)
    opf = fields.CharField(max_length=255, null=True)

    signer = fields.CharField(max_length=255, null=True)

    class Meta:
        table = "legal_entities"
        unique_together = (("inn", "kpp"),)


class Warehouse(Model):
    id = fields.UUIDField(pk=True, default=uuid.uuid4)
    name = fields.CharField(max_length=255)
    description = fields.CharField(max_length=255, null=True)
    company_id = fields.UUIDField()

    created_at = fields.DatetimeField(auto_now_add=True)
    created_by = fields.UUIDField()
    modified_at = fields.DatetimeField(auto_now=True)
    modified_by = fields.UUIDField()

    class Meta:
        table = "warehouses"


class CashRegister(Model):
    id = fields.UUIDField(pk=True, default=uuid.uuid4)
    name = fields.CharField(max_length=255)
    description = fields.CharField(max_length=255, null=True)
    company_id = fields.UUIDField()

    created_at = fields.DatetimeField(auto_now_add=True)
    created_by = fields.UUIDField()
    modified_at = fields.DatetimeField(auto_now=True)
    modified_by = fields.UUIDField()

    class Meta:
        table = "cash_registers"


class City(Model):
    id = fields.UUIDField(pk=True, default=uuid.uuid4)
    name = fields.CharField(max_length=255)
    region = fields.CharField(max_length=255)
    code = fields.CharField(max_length=20)
    external_id = fields.CharField(max_length=40)

    class Meta:
        table = "cities"
