#  Copyright (c) 2023. OCX Consortium https://3docx.org. See the LICENSE

#  Copyright (c) 2023. OCX Consortium https://3docx.org. See the LICENSE
""" CLI script tests."""
import pytest
from click.testing import CliRunner

from ocxtools import __version__
from ocxtools.cli import cli
from tests.conftest import TEST_MODEL


def test_cli_version():
    runner = CliRunner()
    result = runner.invoke(cli, ['version'])
    assert result.exit_code == 0
    assert __version__ in result.output


def test_cli_validate_info():
    runner = CliRunner()
    result = runner.invoke(cli, ['validate', 'info'])
    assert result.exit_code == 0


def test_cli_validate_one_model(shared_datadir):
    runner = CliRunner()
    model = shared_datadir / TEST_MODEL
    result = runner.invoke(cli, ['validate', 'one', str(model.resolve())])
    assert result.exit_code == 0


@pytest.mark.skip
def test_cli_validate_one_model_and_save(shared_datadir):
    runner = CliRunner()
    model = shared_datadir / TEST_MODEL
    result = runner.invoke(cli, ['validate', 'one', str(model.resolve()), '--save', '--report-folder',
                                 shared_datadir.resolve()])
    file = shared_datadir / 'm1.csv'
    assert result.exit_code == 0 and file.exists()


def test_cli_validate_many_models_and_save(shared_datadir):
    runner = CliRunner()
    result = runner.invoke(cli, ['validate', 'many', f'{shared_datadir / TEST_MODEL}', '--save', '--report-folder',  shared_datadir.resolve()])
    file = shared_datadir / 'summary_report.csv'
    assert result.exit_code == 0 and file.exists()
