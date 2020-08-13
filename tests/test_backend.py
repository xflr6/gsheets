# test_backend.py

import pytest

from gsheets import backend


def test_build_service(mocker, serviceName='spam', version='v1'):  # noqa: N803
    build = mocker.patch('apiclient.discovery.build', autospec=True)

    result = backend.build_service(serviceName=serviceName, version=version)

    assert result is build.return_value

    from oauth2client import __version__ as o2c_version

    o2c_v4 = (o2c_version == '4' or o2c_version.startswith('4.'))

    build.assert_called_once_with(serviceName=serviceName, version=version,
                                  cache_discovery=not o2c_v4)


@pytest.mark.usefixtures('files')
def test_iterfiles(services):
    assert sum(1 for _ in backend.iterfiles(services.drive)) == 1

    list_ = services.drive.files.return_value.list
    list_.assert_called_once_with(
        q="mimeType='application/vnd.google-apps.spreadsheet'",
        orderBy='folder,name,createdTime',
        pageToken=None)
    list_.return_value.execute.assert_called_once_with()


@pytest.mark.usefixtures('files')
def test_iterfiles_nomime(services):
    assert sum(1 for _ in backend.iterfiles(services.drive, mimeType=None)) == 1

    list_ = services.drive.files.return_value.list
    list_.assert_called_once_with(orderBy='folder,name,createdTime',
                                  pageToken=None)
    list_.return_value.execute.assert_called_once_with()
