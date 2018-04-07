# test_compat.py

from gsheets import _compat


def test_open_csv(mocker, py2, name='spam.csv', mode='r', encoding='utf-8'):
    open_ = mocker.patch('gsheets._compat.open', new_callable=mocker.Mock)
    assert _compat.open_csv(name, mode=mode, encoding=encoding) is open_.return_value
    if py2:
        open_.assert_called_once_with(name, mode + 'b')
        open_.reset_mock()
        _compat.open_csv(name, mode=mode + 'b', encoding=encoding)
        open_.assert_called_once_with(name, mode + 'b')
    else:
        open_.assert_called_once_with(name, mode, encoding=encoding, newline='')
