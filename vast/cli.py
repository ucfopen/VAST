# -*- coding: utf-8 -*-

"""Console script for vast."""

import csv
import os
import sys
from configparser import ConfigParser, NoOptionError, NoSectionError

import click

from vast.vast import Vast, VastConfig


@click.group()
@click.version_option(prog_name="VAST")
@click.option(
    "--canvas_api_url", envvar="CANVAS_API_URL", help="Provide Canvas instance URL."
)
@click.option(
    "--canvas_api_key", envvar="CANVAS_API_KEY", help="Provide Canvas API key."
)
@click.option(
    "--youtube_api_key", envvar="YOUTUBE_API_KEY", help="Provide YouTube API key."
)
@click.option(
    "--vimeo_access_token",
    envvar="VIMEO_ACCESS_TOKEN",
    help="Provide Vimeo access token.",
)
@click.option(
    "--use-config", "-c", is_flag=True, help="Read from a configuration file."
)
@click.option("--config-file", type=click.Path(), default="~/.vast.ini")
@click.pass_context
def main(context, **kwargs):
    """
    Tool for analyzing media content and captions in Instructure Canvas courses.

    You need the api url and key for your Canvas instance as well as YouTube and Vimeo
    API keys.
    """
    context.config = {}

    for key, value in kwargs.items():
        context.config[key] = value

    if kwargs.get("use_config"):
        filename = os.path.expanduser(kwargs["config_file"])

        if os.path.exists(filename):
            config = ConfigParser()
            config.read(filename)
            try:
                context.config["canvas_api_url"] = config.get(
                    "CANVAS", "canvas_api_url"
                )
                context.config["canvas_api_key"] = config.get(
                    "CANVAS", "canvas_api_key"
                )
                context.config["youtube_api_key"] = config.get(
                    "MEDIA", "youtube_api_key"
                )
                context.config["vimeo_access_token"] = config.get(
                    "MEDIA", "vimeo_access_token"
                )
            except NoOptionError as error:
                raise Exception(
                    "Corrupted config file [{}]: {}".format(filename, error)
                )
            except NoSectionError as error:
                raise Exception(
                    "Corrupted config file [{}]: {}".format(filename, error)
                )


@main.command()
@click.pass_context
def config(context):
    """
    Initialize and store config in a file.
    """
    config_file = os.path.expanduser(context.config["config_file"])

    config = ConfigParser()

    canvas_api_url = click.prompt(
        "Please enter the API URL for your Canvas instance",
        default=context.config["canvas_api_url"],
    )
    canvas_api_key = click.prompt(
        "Please enter your API key", default=context.config["canvas_api_key"]
    )

    youtube_api_key = click.prompt(
        "Please enter your YouTube API key", default=context.config["youtube_api_key"]
    )
    vimeo_access_token = click.prompt(
        "Please enter your Vimeo access token",
        default=context.config["vimeo_access_token"],
    )

    config["CANVAS"] = {
        "canvas_api_url": canvas_api_url,
        "canvas_api_key": canvas_api_key,
    }
    config["MEDIA"] = {
        "youtube_api_key": youtube_api_key,
        "vimeo_access_token": vimeo_access_token,
    }

    with open(config_file, "w") as out:
        config.write(out)
        click.echo("Config written to %s", config_file)


@main.command()
@click.option(
    "--course",
    "-c",
    required=True,
    prompt=True,
    help="Provide the course ID that you would like to check.",
)
@click.option(
    "--exclude",
    "-e",
    help="Comma separated list of services you would like to exclude. Options: syllabus, announcements, modules, assignments, discussions, and pages",
)
@click.option(
    "--output-path",
    "-o",
    help="Specify an output path (default: current directory)",
    default=os.getcwd(),
)
@click.pass_context
def report(context, course, exclude, output_path):
    """
    Analyze a course for captioned media.
    """
    if not exclude:
        exclude = ""

    context.config["course_id"] = course
    context.config["exclude"] = exclude.split(",") if exclude else []

    vast = Vast(config=VastConfig(**context.config))

    try:
        vast.write_report(output_path)
        click.echo("Analysis complete.")
        return 0
    except IOError:
        click.echo("Failed to write report")
        return 1


if __name__ == "__main__":
    sys.exit(main())  # pragma: no cover
