from unittest import mock

import pytest

import setup


@pytest.mark.parametrize("version_info", [(3, 7, 3), (3, 8)])
def test_assert_python_version(version_info):
    assert setup.assert_python_version(version_info) is None


@pytest.mark.parametrize("version_info", [(2, 7), (3, 6)])
def test_assert_python_version_raise(version_info):
    with pytest.raises(AssertionError) as ex_info:
        setup.assert_python_version(version_info)
    assert ex_info.value.args[0].startswith("Python 3.7 is required")


def test_run_setup():
    with mock.patch("setup.setup") as m_setup:
        setup.run_setup()
    assert m_setup.called is True
