from bank_ddd_es_cqrs.shared.model import UniqueID


def test_str_function_on_unique_id():
    g_id = UniqueID('asd')
    assert str(g_id) == 'asd'

