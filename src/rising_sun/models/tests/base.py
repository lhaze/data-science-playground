# -*- coding: utf-8 -*-
import pytest

from ..base import *


class ConfigModelWoSchema(ConfigModel):
    __pks__ = ('attr1', 'attr2')


def test_config_model_pk():
    kwargs = dict(attr1=1, attr2=2)
    instance = ConfigModelWoSchema(**kwargs)
    assert instance.pk == (1, 2)
    assert ConfigModelWoSchema.get_pk(kwargs) == (1, 2)


def test_config_model_get():
    instance = ConfigModelWoSchema(attr1=1, attr2=2)
    assert config_repo.get("ConfigModelWoSchema", (1, 2)) is instance


def test_config_model_single_instance_per_pk():
    instance1 = ConfigModelWoSchema(attr1=1, attr2=2)
    instance2 = ConfigModelWoSchema(attr1=1, attr2=2)
    assert instance1 is instance2


@pytest.fixture
def SerializingSchema():
    class SerializingSchema(v.Schema):
        attr_int = v.SchemaNode(v.Integer(), validator=v.Range(1, 10))
        attr_str = v.SchemaNode(v.String(), validator=v.Length(1, 10))
    return SerializingSchema


@pytest.fixture
def SerializedConfigModel(SerializingSchema):
    class SerializedConfigModel(ConfigModel):
        __pks__ = ('attr1', 'attr2')
        __schema__ = SerializingSchema()
    return SerializedConfigModel


def test_validation_ok(SerializedConfigModel):
    instance = SerializedConfigModel(attr_int=1, attr_str='foo')
    assert instance.__getstate__() == {'attr_int': 1, 'attr_str': 'foo'}
    assert instance.dump() == (
        '!!python/object:rising_sun.models.tests.base.SerializedConfigModel '
        '{attr_int: 1, attr_str: foo}\n'
    )


def test_validation_error(SerializedConfigModel):
    with pytest.raises(v.Invalid) as e:
        SerializedConfigModel(attr_int=0, attr_str='')
    assert e.value.asdict() == {
        'attr_int': '0 is less than minimum value 1',
        'attr_str': 'Required'
    }


def test_attr_not_serialized_preserve(SerializedConfigModel):
    SerializedConfigModel.__schema__.typ.unknown = 'preserve'
    instance = SerializedConfigModel(attr_int=1, attr_str='foo', _not_serialized=2)
    # noinspection PyProtectedMember
    assert instance._not_serialized == 2
    assert '_not_serialized' not in instance.__getstate__()


def test_attr_not_serialized_raises(SerializedConfigModel):
    SerializedConfigModel.__schema__.typ.unknown = 'raise'
    with pytest.raises(v.UnsupportedFields) as e:
        SerializedConfigModel(attr_int=1, attr_str='foo', _not_serialized=2)
    assert e.value.asdict() == {'': 'Unrecognized keys in mapping: "{\'_not_serialized\': 2}"'}
