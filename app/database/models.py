import uuid

from tortoise import fields
from tortoise.fields.relational import ReverseRelation
from tortoise.models import Model


class LegalEntityType(Model):
    id = fields.CharField(pk=True, max_length=255)
    name = fields.CharField(max_length=255)

    class Meta:
        table = "legal_entity_types"


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
    entity_type = fields.ForeignKeyField(
        "models.LegalEntityType", related_name="entities", null=True
    )
    signer = fields.CharField(max_length=255, null=True)

    entity_company_relations: ReverseRelation["EntityCompanyRelation"]

    class Meta:
        table = "legal_entities"
        unique_together = (("inn", "kpp"),)


class EntityCompanyRelation(Model):
    id = fields.UUIDField(pk=True, default=uuid.uuid4)
    company_id = fields.UUIDField()
    legal_entity = fields.ForeignKeyField(
        "models.LegalEntity",
        related_name="entity_company_relations",
        on_delete=fields.CASCADE,
    )
    relation_type = fields.CharField(max_length=10)
    description = fields.TextField(null=True)
    created_at = fields.DatetimeField(auto_now_add=True)

    class Meta:
        table = "entity_company_relations"


class Storage(Model):
    id = fields.UUIDField(pk=True, default=uuid.uuid4)
    name = fields.CharField(max_length=255)
    description = fields.CharField(max_length=255, null=True)
    company_id = fields.UUIDField()

    created_at = fields.DatetimeField(auto_now_add=True)
    created_by = fields.UUIDField()
    modified_at = fields.DatetimeField(auto_now=True)
    modified_by = fields.UUIDField()

    class Meta:
        table = "storages"


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
