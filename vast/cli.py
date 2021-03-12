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
def main(ctx, **kwargs):
    """
    Tool for analyzing media content and captions in Instructure Canvas courses.

    You need the api url and key for your Canvas instance as well as YouTube and Vimeo
    API keys.
    """

    ctx.obj = {}

    for key, value in kwargs.items():
        ctx.obj[key] = value

    if kwargs["use_config"]:
        filename = os.path.expanduser(kwargs["config_file"])

        if os.path.exists(filename):
            config = ConfigParser()
            config.read(filename)
            try:
                ctx.obj["canvas_api_url"] = config.get("CANVAS", "canvas_api_url")
                ctx.obj["canvas_api_key"] = config.get("CANVAS", "canvas_api_key")
                ctx.obj["youtube_api_key"] = config.get("MEDIA", "youtube_api_key")
                ctx.obj["vimeo_access_token"] = config.get(
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
def config(ctx):
    """
    Initialize and store config in a file.
    """
    config_file = os.path.expanduser(ctx.obj["config_file"])

    config_object = ConfigParser()

    canvas_api_url = click.prompt(
        "Please enter the API URL for your Canvas instance",
        default=ctx.obj["canvas_api_url"],
    )

    canvas_api_key = click.prompt(
        "Please enter your API key", default=ctx.obj["canvas_api_key"]
    )

    youtube_api_key = click.prompt(
        "Please enter your YouTube API key", default=ctx.obj["youtube_api_key"]
    )

    vimeo_access_token = click.prompt(
        "Please enter your Vimeo access token", default=ctx.obj["vimeo_access_token"]
    )

    config_object["CANVAS"] = {
        "canvas_api_url": canvas_api_url,
        "canvas_api_key": canvas_api_key,
    }

    config_object["MEDIA"] = {
        "youtube_api_key": youtube_api_key,
        "vimeo_access_token": vimeo_access_token,
    }

    with open(config_file, "w") as conf:
        config_object.write(conf)
        click.echo("Config file written.")


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
@click.pass_context
def analyze(ctx, course, exclude):
    """
    Analyze a course for captioned media.
    """

    if not all(ctx.obj.values()):
        raise KeyError("Missing one or more config values.")
    if exclude:
        exclude = exclude.split(",")
    else:
        exclude = []

    ctx.obj["course_id"] = course
    ctx.obj["exclude"] = exclude

    vconfig = VastConfig(**ctx.obj)
    vast = Vast(vconfig=vconfig)

    vast.resource_runner()

    with open(vast.course_name + ".csv", mode="w") as report:
        writer = csv.writer(
            report, delimiter=",", quotechar='"', quoting=csv.QUOTE_MINIMAL
        )

        writer.writerow(
            [
                "Media Type",
                "Media",
                "Caption Status",
                "Media Location in Course",
                "Meta Data",
            ]
        )

        for media in vast.no_check:
            writer.writerow(
                [
                    media["type"],
                    media["media_loc"],
                    "Manual check required",
                    media["link_loc"],
                ]
            )

        for media in vast.to_check:
            caption_list = ", ".join(media["captions"])
            meta_data = ", ".join(media["meta_data"])
            writer.writerow(
                [
                    media["type"],
                    media["media_loc"],
                    caption_list,
                    media["link_loc"],
                    meta_data,
                ]
            )
    click.echo("Analysis complete.")
    return 0


if __name__ == "__main__":
    sys.exit(main())  # pragma: no cover
