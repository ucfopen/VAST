from __future__ import print_function
import csv
import re

from bs4 import BeautifulSoup
from canvasapi import Canvas
import requests
from six.moves import input

from vast_config import (
    api_key, api_url, courses_url, google_url, google_video, lib_media_urls,
    vimeo_api_key, youtube_key, youtube_pattern
)
from utils import add_entry, process_contents


course_id = input('Enter Canvas ID: ')
canvas = Canvas(api_url, api_key)
course = canvas.get_course(course_id)
print('Checking ' + course.name)
writer = csv.writer(open('{}.csv'.format(course.name), 'wb'))

youtube_link = {}
vimeo_link = {}
media_link = {}
link_media = {}
library_media = {}

# Checks all pages in a canvas course for media links
print('Checking Pages')
pages = course.get_pages()
for page in pages:
    page_body = course.get_page(page.url)
    page_location = page.html_url

    if not page_body.body:
        continue

    contents = page_body.body.encode('utf-8')
    soup = BeautifulSoup(contents, 'html.parser')

    process_contents(
        soup, course, page_location,
        youtube_link, vimeo_link, media_link, link_media, library_media
    )

# Checks all assignments in a canvas course for media links
print('Checking Assignments')
assign = course.get_assignments()
for item in assign:
    if not item.description:
        continue

    assign_location = item.html_url
    contents = item.description.encode('utf-8')
    soup = BeautifulSoup(contents, 'html.parser')

    process_contents(
        soup, course, assign_location,
        youtube_link, vimeo_link, media_link, link_media, library_media
    )

# Checks all discuss in a canvas course for media links
print('Checking Discussions')
discuss = course.get_discussion_topics()
for item in discuss:
    if not item.message:
        continue

    discuss_location = item.html_url
    contents = item.message.encode('utf-8')
    soup = BeautifulSoup(contents, 'html.parser')

    process_contents(
        soup, course, discuss_location,
        youtube_link, vimeo_link, media_link, link_media, library_media
    )

# Checks the syllabus in a canvas course for media links
print('Checking Syllabus')
syllabus = canvas.get_course(course_id, include='syllabus_body')
syllabus_location = '{}/{}/assignments/syllabus'.format(courses_url, course_id)

try:
    contents = syllabus.syllabus_body
    soup = BeautifulSoup(contents, 'html.parser')

    process_contents(
        soup, course, syllabus_location,
        youtube_link, vimeo_link, media_link, link_media, library_media
    )
except Exception:
    pass

# Checks all module external URLs and Files in a canvas course for media links
print('Checking Modules')
modules = course.get_modules()
for module in modules:
    items = module.get_module_items(include='content_details')
    for item in items:
        youtube_embed = []
        vimeo_embed = []
        library_embed = []
        if item.type == 'ExternalUrl':
            module_url = '{}/{}/modules/items/{}'.format(courses_url, course_id, item.id)
            # href = item.external_url.encode('utf8')
            href = item.external_url
            if re.search(youtube_pattern, href):
                youtube_embed.append(href)
            if 'vimeo' in href:
                vimeo_embed.append(href)
            if any(match_str in href for match_str in lib_media_urls):
                library_embed.append(href)

        for y_link in youtube_embed:
            youtube_link.setdefault(y_link, [])
            youtube_link[y_link].append(module_url)
        for v_link in vimeo_embed:
            vimeo_link.setdefault(v_link, [])
            vimeo_link[v_link].append(module_url)
        for link in library_embed:
            add_entry(library_media, link, 'Manually Check for Captions', module_url)
        if item.type == 'File':
            try:
                module_location = item.html_url
                file_id = item.content_id
                get_file = course.get_file(file_id)
                file_location = get_file.url.split('?')[0]

                if 'audio' in get_file.mime_class:
                    link_name = 'Linked Audio File: {}'.format(get_file.display_name)
                    add_entry(
                        link_media, link_name, 'Manually Check for Captions',
                        module_location, file_location=file_location
                    )
                if 'video' in get_file.mime_class:
                    link_name = 'Linked Video File: {}'.format(get_file.display_name)
                    add_entry(
                        link_media, link_name, 'Manually Check for Captions',
                        module_location, file_location=file_location
                    )
                if 'flash' in get_file.mime_class:
                    link_name = 'Linked SWF File: {}'.format(get_file.display_name)
                    add_entry(
                        link_media, link_name, 'Manually Check for Captions',
                        module_location, file_location=file_location
                    )
            except Exception:
                pass

# Checks all announcements in a canvas course for media links
print('Checking Announcements')
announce = course.get_discussion_topics(only_announcements=True)
for item in announce:
    announce_location = item.html_url
    if not item.message:
        continue

    contents = item.message.encode('utf-8')
    soup = BeautifulSoup(contents, 'html.parser')

    process_contents(
        soup, course, announce_location,
        youtube_link, vimeo_link, media_link, link_media, library_media
    )

# Uses YouTube API to check each video for captions
print('Checking YouTube Captions')
for key in youtube_link:
    if 'list' in key:
        youtube_link[key].insert(0, 'this is a playlist, check individual videos')
        youtube_link[key].insert(1, '')
        youtube_link[key].insert(2, '')
        youtube_link[key].insert(3, '')
        continue
    video_id = re.findall(youtube_pattern, key, re.MULTILINE | re.IGNORECASE)
    for item in video_id:
        is_ASR = False
        is_standard = False
        is_english = True
        try:
            r = requests.get('{}?part=snippet&videoId={}&key={}'.format(
                google_url, item, youtube_key
            ))
            data = r.json()
            if data['items']:
                caption_language = []
                for e in data['items']:
                    caption_language.append(e['snippet']['language'])
                    if e['snippet']['language'] == 'en':
                        if e['snippet']['trackKind'] == 'standard':
                            is_standard = True
                        if e['snippet']['trackKind'] == 'ASR':
                            is_ASR = True

                if "en" not in caption_language:
                    is_english = False

                if is_standard is True and is_english is True:
                    youtube_link[key] = ['Captions found in English', '', '', ''] + youtube_link[key]

                if is_standard is False and is_ASR is True and is_english is True:
                    youtube_link[key].insert(0, 'Automatic Captions in English')
                    r = requests.get('{}?part=contentDetails&id={}&key={}'.format(
                        google_video, item, youtube_key
                    ))
                    data = r.json()
                    for d in data['items']:
                        duration = d['contentDetails']['duration']
                        if 'H' in duration:
                            hour, min_org = duration.split('H')
                            minute, sec = min_org.split('M')
                            youtube_link[key].insert(1, hour[2:])
                            youtube_link[key].insert(2, minute)
                            youtube_link[key].insert(3, sec[:-1])
                        elif 'M' in duration:
                            minute, sec = duration.split('M')
                            if minute is None:
                                youtube_link[key].insert(1, '0')
                                youtube_link[key].insert(2, '0')
                                youtube_link[key].insert(3, sec[:-1])
                            else:
                                youtube_link[key].insert(1, '0')
                                youtube_link[key].insert(2, minute[2:])
                                youtube_link[key].insert(3, sec[:-1])
                        else:
                            youtube_link[key].insert(1, '0')
                            youtube_link[key].insert(2, '0')
                            youtube_link[key].insert(3, duration[2:-1])

                if is_english is False:
                    youtube_link[key].insert(0, 'No Captions in English')
                    r = requests.get('{}?part=contentDetails&id={}&key={}'.format(
                        google_video, item, youtube_key
                    ))
                    data = r.json()
                    for d in data['items']:
                        duration = d['contentDetails']['duration']
                        if 'H' in duration:
                            hour, min_org = duration.split('H')
                            minute, sec = min_org.split('M')
                            youtube_link[key].insert(1, hour[2:])
                            youtube_link[key].insert(2, minute)
                            youtube_link[key].insert(3, sec[:-1])
                        elif 'M' in duration:
                            minute, sec = duration.split('M')
                            if minute is None:
                                youtube_link[key].insert(1, '0')
                                youtube_link[key].insert(2, '0')
                                youtube_link[key].insert(3, sec[:-1])
                            else:
                                youtube_link[key].insert(1, '0')
                                youtube_link[key].insert(2, minute[2:])
                                youtube_link[key].insert(3, sec[:-1])
                        else:
                            youtube_link[key].insert(1, '0')
                            youtube_link[key].insert(2, '0')
                            youtube_link[key].insert(3, duration[2:-1])
            else:
                youtube_link[key].insert(0, 'No Captions')
                r = requests.get('{}?part=contentDetails&id={}&key={}'.format(
                    google_video, item, youtube_key
                ))
                data = r.json()
                for d in data['items']:
                    duration = d['contentDetails']['duration']
                    if 'H' in duration:
                        hour, min_org = duration.split('H')
                        min, sec = min_org.split('M')
                        youtube_link[key].insert(1, hour[2:])
                        youtube_link[key].insert(2, min)
                        youtube_link[key].insert(3, sec[:-1])
                    elif 'M' in duration:
                        min, sec = duration.split('M')
                        if min is None:
                            youtube_link[key].insert(1, '0')
                            youtube_link[key].insert(2, '0')
                            youtube_link[key].insert(3, sec[:-1])
                        else:
                            youtube_link[key].insert(1, '0')
                            youtube_link[key].insert(2, min[2:])
                            youtube_link[key].insert(3, sec[:-1])
                    else:
                        youtube_link[key].insert(1, '0')
                        youtube_link[key].insert(2, '0')
                        youtube_link[key].insert(3, duration[2:-1])

        except KeyError:
            youtube_link[key].insert(0, 'Unable to Check Youtube Video')
            youtube_link[key].insert(1, '')
            youtube_link[key].insert(2, '')
            youtube_link[key].insert(3, '')

# Uses Vimeo API to check videos for captions
print('Checking Vimeo Captions')
for link in vimeo_link:
    vimeo_captions = []
    if 'player' in link:
        split_link = link.split('/')
        if '?' in split_link[4]:
            video_link = split_link[4]
            split_link_question = video_link.split('?')
            video_id = split_link_question[0]
        else:
            video_id = split_link[4]
        try:
            r = requests.get(
                'https://api.vimeo.com/videos/{}/texttracks'.format(video_id),
                headers={'Authorization': 'Bearer {}'.format(vimeo_api_key)}
            )
            data = r.json()
            if not data['data']:
                vimeo_link[link].insert(0, 'No Captions')
                r = requests.get(
                    'https://api.vimeo.com/videos/{}'.format(video_id),
                    headers={'Authorization': 'Bearer {}'.format(vimeo_api_key)}
                )
                data = r.json()
                vimeo_duration = data['duration']
                hour, remainder = divmod(vimeo_duration, 3600)
                minute, second = divmod(remainder, 60)
                vimeo_link[link].insert(1, hour)
                vimeo_link[link].insert(2, minute)
                vimeo_link[link].insert(3, second)
            else:
                for d in data['data']:
                    if d['language'] == 'en' or d['language'] == 'en-US':
                        vimeo_captions.append('1')
                    else:
                        vimeo_captions.append('2')
                if '1' in vimeo_captions:
                    vimeo_link[link] = ['Captions in English', '', '', ''] + vimeo_link[link]
                else:
                    r = requests.get(
                        'https://api.vimeo.com/videos/{}'.format(video_id),
                        headers={'Authorization': 'Bearer {}'.format(vimeo_api_key)}
                    )
                    data = r.json()
                    vimeo_duration = data['duration']
                    hour, remainder = divmod(vimeo_duration, 3600)
                    minute, second = divmod(remainder, 60)
                    vimeo_link[link] = ['No English Captions', hour, minute, second] + vimeo_link[link]

        except KeyError:
            vimeo_link[link] = ['Unable to Vimeo Check Video', '', '', ''] + vimeo_link[link]
    else:
        if 'review' in link:
            split_link = link.split('/')
            video_id = split_link[-2]
        else:
            split_link = link.split('/')
            video_id = split_link[-1]
            if not video_id:
                video_id = split_link[-2]
        try:
            r = requests.get(
                'https://api.vimeo.com/videos/{}/texttracks'.format(video_id),
                headers={'Authorization': 'Bearer {}'.format(vimeo_api_key)}
            )
            data = r.json()
            if not data['data']:
                vimeo_link[link].insert(0, 'No Captions')
                r = requests.get(
                    'https://api.vimeo.com/videos/{}'.format(video_id),
                    headers={'Authorization': 'Bearer {}'.format(vimeo_api_key)}
                )
                data = r.json()
                vimeo_duration = data['duration']
                hour, remainder = divmod(vimeo_duration, 3600)
                minute, second = divmod(remainder, 60)
                vimeo_link[link].insert(1, hour)
                vimeo_link[link].insert(2, minute)
                vimeo_link[link].insert(3, second)
            else:
                for d in data['data']:
                    if d['language'] == 'en' or d['language'] == 'en-US':
                        vimeo_captions.append('1')
                    else:
                        vimeo_captions.append('2')
                if '1' in vimeo_captions:
                    vimeo_link[link].insert(0, 'Captions in English')
                    vimeo_link[link].insert(1, '')
                    vimeo_link[link].insert(2, '')
                    vimeo_link[link].insert(3, '')
                else:
                    vimeo_link[link].insert(0, 'No English Captions')
                    r = requests.get(
                        'https://api.vimeo.com/videos/{}'.format(video_id),
                        headers={'Authorization': 'Bearer {}'.format(vimeo_api_key)}
                    )
                    data = r.json()
                    vimeo_duration = data['duration']
                    hour, remainder = divmod(vimeo_duration, 3600)
                    minute, second = divmod(remainder, 60)
                    vimeo_link[link].insert(1, hour)
                    vimeo_link[link].insert(2, minute)
                    vimeo_link[link].insert(3, second)
        except KeyError:
            vimeo_link[link].insert(0, 'Unable to Check Vimeo Video')
            vimeo_link[link].insert(1, '')
            vimeo_link[link].insert(2, '')
            vimeo_link[link].insert(3, '')
writer.writerow([
    'Media', 'Caption Status', 'Hour', 'Minute', 'Second', 'Page Location',
    'File Location'
])
for key, value in youtube_link.items():
    writer.writerow([key] + value)
for key, value in vimeo_link.items():
    writer.writerow([key] + value)
for key, value in media_link.items():
    writer.writerow([key] + value)
for key, value in link_media.items():
    writer.writerow([key] + value)
for key, value in library_media.items():
    writer.writerow([key] + value)
