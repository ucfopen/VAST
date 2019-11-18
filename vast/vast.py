# -*- coding: utf-8 -*-

"""Main module."""

from canvasapi import Canvas
from pprint import pprint
import re
import requests

from resources import ResourceProvider, SyllabusService, AnnouncementService, ModuleService, AssignmentService, DiscussionService, PageService
from parser import Parser, youtube_pattern, youtube_playlist_pattern, vimeo_pattern


class VastConfig:
    def __init__(self, canvas_api_url, canvas_api_key, course_id, exclude, youtube_api_key, vimeo_access_token):
        self.api_url = canvas_api_url
        self.api_key = canvas_api_key
        self.course_id = course_id
        self.exclude = exclude
        self.youtube_api_key = youtube_api_key
        self.vimeo_access_token = vimeo_access_token


class Vast:
    def __init__(self, config):
        self.config = config

    def get_canvas_client(self):
        """
        Given a VastConfig object, fetch a Canvas client
        """
        return Canvas(self.config.api_url, self.config.api_key)

    def resource_runner(self):
        to_check = []
        no_check = []

        parser = Parser()

        for subclass in ResourceProvider.__subclasses__():
            if subclass.name in self.config.exclude:
                continue
            print(subclass)
            retrieved_data = subclass(vast=self).fetch()
            data = retrieved_data['info']
            flat = retrieved_data['is_flat']

            for content_pair in data:
                # Each content pair represents a page, or a discussion, etc. (Whole pages) if flat
                # If not flat then each pair is simply a link and a location
                to_check, no_check = parser.parse_content(content_pair, flat)

        # Validate that the media links contain captions
        for link in to_check:
            if link['type'] == 'youtube':
                match = re.search(youtube_pattern, link['media_loc'])
                video_id = match.group(1)
                r = requests.get(
                    'https://www.googleapis.com/youtube/v3/captions?part=snippet&videoId={}&key={}'
                    .format(video_id, self.config.youtube_api_key)
                )

                if r.status_code == 404:
                    link['captions'].append('Improper link to video')
                    continue

                response = r.json()

                try:
                    for item in response['items']:
                        if item['snippet']['language'] == 'en':
                            if item['snippet']['trackKind'] == 'ASR':
                                link['captions'].append('automated english')
                            if item['snippet']['trackKind'] == 'standard':
                                link['captions'].append('english')
                        elif item['snippet']['language']:
                            link['captions'].append(item['snippet']['language'])
                except:
                    print('Passing because of no items in response')

            if link['type'] == 'vimeo':
                match = re.search(vimeo_pattern, link['media_loc'])
                video_id = match.group(4)
                r = requests.get(
                    'https://api.vimeo.com/videos/{}/texttracks'.format(video_id),
                    headers={'Authorization': 'bearer {}'.format(self.config.vimeo_access_token)}
                )

                if r.status_code == 404:
                    link['captions'].append('Improper link to video')
                    continue

                response = r.json()

                try:
                    for item in response['data']:
                        if item['language'] == 'en':
                            link['captions'].append('english')
                        elif item['language']:
                            link['captions'].append(item['language'])
                except:
                    pass

        import pdb; pdb.set_trace()
        # Generate a report with that data
