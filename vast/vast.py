# -*- coding: utf-8 -*-

"""Main module."""

from canvasapi import Canvas
from langcodes import Language
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
        self.course_name = None
        self.to_check = []
        self.no_check = []

    def get_canvas_client(self):
        """
        Given a VastConfig object, fetch a Canvas client
        """
        return Canvas(self.config.api_url, self.config.api_key)

    def resource_runner(self):
        """
        Run through each resource searching for media and parse media for captions
        """

        parser = Parser()

        for subclass in ResourceProvider.__subclasses__():
            if subclass.name in self.config.exclude:
                continue
            print('Checking ' + subclass.name)
            self.course_name = subclass(vast=self).get_course_name()
            retrieved_data = subclass(vast=self).fetch()
            data = retrieved_data['info']
            flat = retrieved_data['is_flat']

            for content_pair in data:
                # Each content pair represents a page, or a discussion, etc. (Whole pages) if flat
                # If not flat then each pair is simply a link and a location
                self.to_check, self.no_check = parser.parse_content(content_pair, flat)

        # Validate that the media links contain captions
        for link in self.to_check:
            if link['type'] == 'youtube':
                match = re.search(youtube_pattern, link['media_loc'])
                video_id = match.group(1)
                r = requests.get(
                    'https://www.googleapis.com/youtube/v3/captions?part=snippet&videoId={}&key={}'
                    .format(video_id, self.config.youtube_api_key)
                )

                if r.status_code == 404:
                    link['captions'].append('N/A')
                    link['meta_data'].append('Broken video link')
                    continue

                response = r.json()

                try:
                    for item in response['items']:
                        caption_lang_code = item['snippet']['language']
                        lang_name = Language.make(language=caption_lang_code).language_name()
                        if item['snippet']['trackKind']== 'ASR':
                            link['captions'].append('Automatic Speech Recognition: ' + lang_name)
                        elif caption_lang_code:
                            link['captions'].append(lang_name)
                except:
                    pass

            if link['type'] == 'vimeo':
                match = re.search(vimeo_pattern, link['media_loc'])
                video_id = match.group(4)
                r = requests.get(
                    'https://api.vimeo.com/videos/{}/texttracks'.format(video_id),
                    headers={'Authorization': 'bearer {}'.format(self.config.vimeo_access_token)}
                )

                if r.status_code == 404:
                    link['captions'].append('N/A')
                    link['meta_data'].append('Broken video link')
                    continue

                response = r.json()

                try:
                    for item in response['data']:
                        if item['language']:
                            caption_lang_code = item['language']
                            lang_name = Language.make(language=caption_lang_code).language_name()
                            link['captions'].append(lang_name)
                except:
                    pass

            if len(link['captions']) == 0:
                link['captions'].append('No captions')
