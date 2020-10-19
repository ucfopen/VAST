#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""Tests for `vast` package."""


import unittest
from unittest import mock
from click.testing import CliRunner

from vast.cli import main, config, analyze
from vast.vast import Vast, VastConfig
from vast.provider import ResourceProvider, SyllabusService, AnnouncementService, ModuleService, AssignmentService, DiscussionService, PageService
from vast.parser import Parser


class TestProvider(unittest.TestCase):
    """Test for 'provider' Canvas classes"""

    def setUp(self):
        """Set up test fixtures, if any."""
        self.vconfig = VastConfig(
            canvas_api_url='test1',
            canvas_api_key='test2',
            course_id='123456',
            exclude=[],
            youtube_api_key='test3',
            vimeo_access_token='test4'
        )

    @mock.patch('vast.provider.Canvas')
    def test_resource_provider_config_load(self, mock_canvas):
        provider = ResourceProvider(self.vconfig)
        assert provider.vconfig == self.vconfig

    @mock.patch('vast.provider.Canvas')
    def test_resource_provider_canvas_client(self, mock_canvas):
        provider = ResourceProvider(self.vconfig)
        mock_canvas.assert_called_with(self.vconfig.api_url, self.vconfig.api_key)
        provider.client.get_course.assert_called_with(self.vconfig.course_id)

    @mock.patch('vast.provider.Canvas')
    def test_resource_provider_returns_course_name(self, mock_canvas):
        provider = ResourceProvider(self.vconfig)
        provider.course.name = "ABC1234-00Semester"
        course_name = provider.get_course_name()
        assert course_name == provider.course.name

    @mock.patch('vast.provider.Canvas')
    def test_resource_provider_instantiation(self, mock_canvas):
        provider = ResourceProvider(self.vconfig)
        self.assertRaises(NotImplementedError, provider.fetch)


class TestVast(unittest.TestCase):
    """Tests for `vast` package."""

    def setUp(self):
        """Set up test fixtures, if any."""
        self.vconfig = VastConfig(
            canvas_api_url='test1',
            canvas_api_key='test2',
            course_id='123456',
            exclude=[],
            youtube_api_key='test3',
            vimeo_access_token='test4'
        )

    def tearDown(self):
        """Tear down test fixtures, if any."""

    def test_000_something(self):
        """Test something."""

class TestCli(unittest.TestCase):
    """Tests for 'vast' click CLI."""
    def test_main_cli(self):
        """Test the CLI."""
        help_message = "Usage: main [OPTIONS] COMMAND [ARGS]...\n\n  Tool for analyzing media content and captions in Instructure Canvas courses.\n\n  You need the api url and key for your Canvas instance as well as YouTube and\n  Vimeo API keys.\n\nOptions:\n  --version                  Show the version and exit.\n  --canvas_api_url TEXT      Provide Canvas instance URL.\n  --canvas_api_key TEXT      Provide Canvas API key.\n  --youtube_api_key TEXT     Provide YouTube API key.\n  --vimeo_access_token TEXT  Provide Vimeo access token.\n  -c, --use-config           Read from a configuration file.\n  --config-file PATH\n  --help                     Show this message and exit.\n\nCommands:\n  analyze  Analyze a course for captioned media.\n  config   Initialize and store config in a file.\n"
        runner = CliRunner()
        result = runner.invoke(main)
        assert not result.exception
        assert result.exit_code == 0
        assert help_message in result.output
        help_result = runner.invoke(main, ['--help'])
        assert not result.exception
        assert help_result.exit_code == 0
        assert help_message in help_result.output

    def test_config_cli(self):
        runner = CliRunner()
        result = runner.invoke(main, ['config'], input="test1\ntest2\ntest3\ntest4\n")
        assert not result.exception
        assert result.output.endswith('Config file written.\n')

    def test_analyze_cli_with_no_config(self):
        runner = CliRunner()
        result = runner.invoke(main, ['analyze'], input="123456\n")
        assert result.exception
        assert result.exc_info[0] is KeyError
        assert result.exit_code == 1

