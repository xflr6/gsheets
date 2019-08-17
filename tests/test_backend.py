# test_backend.py

import pytest

from gsheets import backend


def test_build_service(mocker, serviceName='spam', version='v1'):  # noqa: N803
    build = mocker.patch('apiclient.discovery.build', autospec=True)

    result = backend.build_service(serviceName=serviceName, version=version)

    assert result is build.return_value
    build.assert_called_once_with(serviceName=serviceName, version=version)


@pytest.mark.usefixtures('files')
def test_iterfiles(apiclient):
    assert sum(1 for _ in backend.iterfiles(apiclient.drive)) == 1
    list_ = apiclient.drive.files.return_value.list
    list_.assert_called_once_with(
        q="mimeType='application/vnd.google-apps.spreadsheet'",
        orderBy='folder,name,createdTime',
        pageToken=None)
    list_.return_value.execute.assert_called_once_with()


@pytest.mark.usefixtures('files')
def test_iterfiles_nomime(apiclient):
    assert sum(1 for _ in backend.iterfiles(apiclient.drive, mimeType=None)) == 1
    list_ = apiclient.drive.files.return_value.list
    list_.assert_called_once_with(orderBy='folder,name,createdTime',
                                  pageToken=None)
    list_.return_value.execute.assert_called_once_with()
