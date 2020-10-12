# -*- coding: utf-8 -*-

"""Console script for vast."""

import click
import csv
import os
import sys

from vast.vast import VastConfig, Vast

@click.command()
@click.version_option(prog_name="VAST")
@click.option('--settings', is_flag=True, help="Specifies there is a module that contains your config in a dictionary. This overwrites any environment variables or passed in.")
@click.option('--canvas_api_url', default=lambda: os.environ.get('CANVAS_API_URL'), help="Provide Canvas instance URL.")
@click.option('--canvas_api_key', default=lambda: os.environ.get('CANVAS_API_KEY'), help="Provide Canvas API key.")
@click.option('--youtube_api_key', default=lambda: os.environ.get('YOUTUBE_API_KEY'), help="Provide YouTube API key.")
@click.option('--vimeo_access_token', default=lambda: os.environ.get('VIMEO_ACCESS_TOKEN'), help="Provide Vimeo access token.")
@click.option('--course', '-c', required=True, prompt=True, help="Provide the course ID that you would like to check.")
@click.option('--exclude', '-e', help="Comma separated list of services you would like to exclude. Options: syllabus, announcements, modules, assignments, discussions, and pages")
def main(settings, canvas_api_url, canvas_api_key, youtube_api_key, vimeo_access_token, course, exclude):
    if settings:
        from settings import config
        try:
            canvas_api_url = config['CANVAS_API_URL']
            canvas_api_key = config['CANVAS_API_KEY']
            youtube_api_key = config['YOUTUBE_API_KEY']
            vimeo_access_token = config['VIMEO_ACCESS_TOKEN']
        except KeyError as error:
            print(f'Missing {error} key in config file')
            return 0
    if exclude:
        exclude = exclude.split(',')
    else:
        exclude = []

    _config = {
        "canvas_api_url": canvas_api_url,
        "canvas_api_key": canvas_api_key,
        "course_id": course,
        "exclude": exclude,
        "youtube_api_key": youtube_api_key,
        "vimeo_access_token": vimeo_access_token
    }

    config = VastConfig(**_config)
    vast = Vast(config=config)

    vast.resource_runner()

    with open(vast.course_name + '.csv', mode='w') as report:
        writer = csv.writer(report, delimiter=',', quotechar='"', quoting=csv.QUOTE_MINIMAL)

        writer.writerow([
            'Media Type',
            'Media',
            'Caption Status',
            'Media Location in Course',
            'Meta Data'
        ])

        for media in vast.no_check:
            writer.writerow([
                media['type'],
                media['media_loc'],
                'Manual check required',
                media['link_loc']
            ])

        for media in vast.to_check:
            caption_list = ", ".join(media['captions'])
            meta_data = ", ".join(media['meta_data'])
            writer.writerow([
                media['type'],
                media['media_loc'],
                caption_list,
                media['link_loc'],
                meta_data
            ])

    return 0

if __name__ == "__main__":
    sys.exit(main())  # pragma: no cover
