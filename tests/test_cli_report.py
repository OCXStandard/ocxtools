#  Copyright (c) 2023. OCX Consortium https://3docx.org. See the LICENSE

#  Copyright (c) 2023. OCX Consortium https://3docx.org. See the LICENSE
""" CLI script tests."""
from click.testing import CliRunner
from ocxtools.cli import cli


def test_report_content(shared_datadir):
    runner = CliRunner()
    model = shared_datadir / 'm1.3docx'
    result = runner.invoke(cli, ['report', 'content', str(model.resolve()), '--report-folder',
                                 shared_datadir.resolve()])
    assert result.exit_code == 0


def test_report_count(shared_datadir):
    runner = CliRunner()
    model = shared_datadir / 'm1.3docx'
    result = runner.invoke(cli, ['report', 'count', str(model.resolve())])
    # print(result.stdout)
    assert result.exit_code == 0


def test_report_count_plate(shared_datadir):
    runner = CliRunner()
    model = shared_datadir / 'm1.3docx'
    result = runner.invoke(cli, ['report', 'count', str(model.resolve())])
    result = runner.invoke(cli, ['report', 'details', '--report', 'ElementCount', '--member', 'Plate'])
    # print(result.stdout)
    assert result.exit_code == 0


def test_report_content_plate(shared_datadir):
    runner = CliRunner()
    model = shared_datadir / 'm1.3docx'
    result = runner.invoke(cli, ['report', 'content', str(model.resolve()), '--report-folder',
                                 shared_datadir.resolve()])
    result = runner.invoke(cli, ['report', 'details', '--report', 'Plate'])
    assert result.exit_code == 0
