from __future__ import print_function, division
import csv
import re
import time

from bs4 import BeautifulSoup
from canvasapi import Canvas
import requests
from six.moves import input

from vast_config import (
    api_key, api_url, courses_url, google_url, google_video,
    lib_media_urls, vimeo_api_key, youtube_key, youtube_pattern
)
from utils import add_entry


start_time = time.time()
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
pages = course.get_pages()
if pages:
    print('Checking Pages')
    for page in pages:
        page_body = course.get_page(page.url)
        page_location = page.html_url
        if page_body.body:
            contents = page_body.body.encode('utf-8')
            soup = BeautifulSoup(contents, 'html.parser')
            # Process Anchor Tags
            href_href_list = []
            for link in soup.find_all('a'):
                href_href_list.append(link.get('href'))

                location = link.get('data-api-endpoint')
                if location:
                    try:
                        file_id = location.split('/')[-1:]
                        file_id_string = ', '.join(file_id)
                        get_file = course.get_file(file_id_string)
                        file_location = get_file.url.split('?')[0]
                        if 'audio' in get_file.mime_class:
                            add_entry(
                                link_media,
                                'Linked Audio File: {}'.format(get_file.display_name),
                                'Manually Check for Captions',
                                page_location,
                                file_location=file_location
                            )
                        if 'video' in get_file.mime_class:
                            add_entry(
                                link_media,
                                'Linked Video File: {}'.format(get_file.display_name),
                                'Manually Check for Captions',
                                page_location,
                                file_location=file_location
                            )
                        if 'flash' in get_file.mime_class:
                            add_entry(
                                link_media,
                                'Linked SWF File: {}'.format(get_file.display_name),
                                'Manually Check for Captions',
                                page_location,
                                file_location=file_location
                            )
                    except:
                        pass

            href_list_filter = filter(None, href_href_list)

            for link in href_list_filter:
                # Matches library media from lib_media_urls
                if any(match_str in link for match_str in lib_media_urls):
                    add_entry(library_media, link, 'Manually Check for Captions', page_location)
                # Matches YouTube
                elif re.search(youtube_pattern, link):
                    youtube_link.setdefault(link, [])
                    youtube_link[link].append(page_location)
                # Matches Vimeo
                elif 'vimeo.com' in link:
                    vimeo_link.setdefault(link, [])
                    vimeo_link[link].append(page_location)

            # Process IFrames
            iframe_list = []
            for link in soup.find_all('iframe'):
                iframe_list.append(link.get('src'))
            iframe_list_filter = filter(None, iframe_list)

            for link in iframe_list_filter:
                # Matches library media from lib_media_urls
                if any(match_str in link for match_str in lib_media_urls):
                    add_entry(library_media, link, 'Manually Check for Captions', page_location)
                # Matches YouTube
                elif re.search(youtube_pattern, link):
                    youtube_link.setdefault(link, [])
                    youtube_link[link].append(page_location)
                # Matches Vimeo
                elif 'vimeo.com' in link:
                    vimeo_link.setdefault(link, [])
                    vimeo_link[link].append(page_location)

            # Process Videos
            for video in soup.find_all('video'):
                m_link = 'Video Media Comment {}'.format(video.get('data-media_comment_id'))
                for media_comment in video.get('class'):
                    if media_comment == 'instructure_inline_media_comment video_comment':
                        add_entry(media_link, m_link, 'Manually Check for Captions', page_location)

            # Process Audio
            for audio in soup.find_all('audio'):
                m_link = 'Audio Media Comment {}'.format(audio.get('data-media_comment_id'))
                for media_comment in audio.get('class'):
                    if media_comment == 'instructure_inline_media_comment audio_comment':
                        add_entry(media_link, m_link, 'Manually Check for Captions', page_location)

# Checks all assignments in a canvas course for media links
assign = course.get_assignments()
if assign:
    print('Checking Assignments')
    for item in assign:
        if item.description:
            assign_location = item.html_url
            contents = item.description.encode('utf-8')
            soup = BeautifulSoup(contents, 'html.parser')
            href_list = []
            for link in soup.find_all('a'):
                href_list.append(link.get('href'))
            href_list_filter = filter(None, href_list)
            library_embed_fod = [s for s in href_list_filter if 'fod.infobase.com' in s]
            for link in library_embed_fod:
                library_media.setdefault(link, [])
                library_media[link].append('Manually Check for Captions')
                library_media[link].append('')
                library_media[link].append('')
                library_media[link].append('')
                library_media[link].append(assign_location)
            library_embed_alex = [s for s in href_list_filter if 'search.alexanderstreet.com' in s]
            for link in library_embed_alex:
                library_media.setdefault(link, [])
                library_media[link].append('Manually Check for Captions')
                library_media[link].append('')
                library_media[link].append('')
                library_media[link].append('')
                library_media[link].append(assign_location)
            library_embed_kanopy = [s for s in href_list_filter if 'kanopystreaming-com' in s]
            for link in library_embed_kanopy:
                library_media.setdefault(link, [])
                library_media[link].append('Manually Check for Captions')
                library_media[link].append('')
                library_media[link].append('')
                library_media[link].append('')
                library_media[link].append(assign_location)
            youtube_embed = [s for s in href_list_filter if re.search(youtube_pattern, s)]
            vimeo_embed = [s for s in href_list_filter if 'vimeo.com' in s]
            for link in youtube_embed:
                youtube_link.setdefault(link, [])
                youtube_link[link].append(item.html_url)
            for v_link in vimeo_embed:
                vimeo_link.setdefault(v_link, [])
                vimeo_link[v_link].append(item.html_url)
                vimeo_link[v_link].append(item.html_url)
            iframe_list = []
            for link in soup.find_all('iframe'):
                iframe_list.append(link.get('src'))
            iframe_list_filter = filter(None, iframe_list)
            library_iframe_fod = [s for s in iframe_list_filter if 'fod.infobase.com' in s]
            for link in library_iframe_fod:
                library_media.setdefault(link, [])
                library_media[link].append('Manually Check for Captions')
                library_media[link].append('')
                library_media[link].append('')
                library_media[link].append('')
                library_media[link].append(assign_location)
            library_iframe_alex = [s for s in iframe_list_filter if 'search.alexanderstreet.com' in s]
            for link in library_iframe_alex:
                library_media.setdefault(link, [])
                library_media[link].append('Manually Check for Captions')
                library_media[link].append('')
                library_media[link].append('')
                library_media[link].append('')
                library_media[link].append(assign_location)
            library_iframe_kanopy = [s for s in iframe_list_filter if 'kanopystreaming-com' in s]
            for link in library_iframe_kanopy:
                library_media.setdefault(link, [])
                library_media[link].append('Manually Check for Captions')
                library_media[link].append('')
                library_media[link].append('')
                library_media[link].append('')
                library_media[link].append(assign_location)
            youtube_iframe = [s for s in iframe_list_filter if re.search(youtube_pattern, s)]
            vimeo_iframe = [s for s in iframe_list_filter if 'vimeo.com' in s]
            for link in youtube_iframe:
                youtube_link.setdefault(link, [])
                youtube_link[link].append(item.html_url)
            for v_link in vimeo_iframe:
                vimeo_link.setdefault(v_link, [])
                vimeo_link[v_link].append(item.html_url)
            for video in soup.find_all('video'):
                instructure = video.get('class')
                media_id = video.get('data-media_comment_id')
                for media_comment in instructure:
                    if media_comment == 'instructure_inline_media_comment video_comment':
                        m_link = 'Video Media Comment {}'.format(media_id)
                        media_link.setdefault(m_link, [])
                        media_link[m_link].append('Manually Check for Captions')
                        media_link[m_link].append('')
                        media_link[m_link].append('')
                        media_link[m_link].append('')
                        media_link[m_link].append(assign_location)
            for audio in soup.find_all('audio'):
                instructure = audio.get('class')
                media_id = audio.get('data-media_comment_id')
                for media_comment in instructure:
                    if media_comment == 'instructure_inline_media_comment audio_comment':
                        m_link = 'Audio Media Comment {}'.format(media_id)
                        media_link.setdefault(m_link, [])
                        media_link[m_link].append('Manually Check for Captions')
                        media_link[m_link].append('')
                        media_link[m_link].append('')
                        media_link[m_link].append('')
                        media_link[m_link].append(assign_location)
            for file_link in soup.find_all('a'):
                instructure = file_link.get('class')
                location = file_link.get('data-api-endpoint')
                if location:
                    try:
                        file_id = location.split('/')[-1:]
                        file_id_string = ', '.join(file_id)
                        get_file = course.get_file(file_id_string)
                        file_location = get_file.url.split('?')[0]
                        if 'audio' in get_file.mime_class:
                            link_name = 'Linked Audio File: {}'.format(get_file.display_name)
                            link_media.setdefault(link_name, [])
                            link_media[link_name].append('Manually Check for Captions')
                            link_media[link_name].append('')
                            link_media[link_name].append('')
                            link_media[link_name].append('')
                            link_media[link_name].append(assign_location)
                            link_media[link_name].append(file_location)
                        if 'video' in get_file.mime_class:
                            link_name = 'Linked Video File: {}'.format(get_file.display_name)
                            link_media.setdefault(link_name, [])
                            media_link[m_link].append('Manually Check for Captions')
                            link_media[link_name].append('')
                            link_media[link_name].append('')
                            link_media[link_name].append('')
                            link_media[link_name].append(assign_location)
                            link_media[link_name].append(file_location)
                        if 'flash' in get_file.mime_class:
                            link_name = 'Linked SWF File: {}'.format(get_file.display_name)
                            link_media.setdefault(link_name, [])
                            link_media[link_name].append('Manually Check for Captions')
                            link_media[link_name].append('')
                            link_media[link_name].append('')
                            link_media[link_name].append('')
                            link_media[link_name].append(assign_location)
                            link_media[link_name].append(file_location)
                    except:
                        pass

# Checks all discuss in a canvas course for media links
discuss = course.get_discussion_topics()
if discuss:
    print('Checking Discussions')
    for item in discuss:
        if item.message:
            discuss_location = item.html_url
            contents = item.message.encode('utf-8')
            soup = BeautifulSoup(contents, 'html.parser')
            href_list = []
            for link in soup.find_all('a'):
                href_list.append(link.get('href'))
            href_list_filter = filter(None, href_list)
            library_embed_fod = [s for s in href_list_filter if 'fod.infobase.com' in s]
            for link in library_embed_fod:
                library_media.setdefault(link, [])
                library_media[link].append('Manually Check for Captions')
                library_media[link].append('')
                library_media[link].append('')
                library_media[link].append('')
                library_media[link].append(discuss_location)
            library_embed_alex = [s for s in href_list_filter if 'search.alexanderstreet.com' in s]
            for link in library_embed_alex:
                library_media.setdefault(link, [])
                library_media[link].append('Manually Check for Captions')
                library_media[link].append('')
                library_media[link].append('')
                library_media[link].append('')
                library_media[link].append(discuss_location)
            library_embed_kanopy = [s for s in href_list_filter if 'kanopystreaming-com' in s]
            for link in library_embed_kanopy:
                library_media.setdefault(link, [])
                library_media[link].append('Manually Check for Captions')
                library_media[link].append('')
                library_media[link].append('')
                library_media[link].append('')
                library_media[link].append(discuss_location)
            youtube_embed = [s for s in href_list_filter if re.search(youtube_pattern, s)]
            vimeo_embed = [s for s in href_list_filter if 'vimeo.com' in s]
            for link in youtube_embed:
                youtube_link.setdefault(link, [])
                youtube_link[link].append(item.html_url)
            for v_link in vimeo_embed:
                vimeo_link.setdefault(v_link, [])
                vimeo_link[v_link].append(item.html_url)
            iframe_list = []
            for link in soup.find_all('iframe'):
                iframe_list.append(link.get('src'))
            iframe_list_filter = filter(None, iframe_list)
            library_iframe_fod = [s for s in iframe_list_filter if 'fod.infobase.com' in s]
            for link in library_iframe_fod:
                library_media.setdefault(link, [])
                library_media[link].append('Manually Check for Captions')
                library_media[link].append('')
                library_media[link].append('')
                library_media[link].append('')
                library_media[link].append(discuss_location)
            library_iframe_alex = [s for s in iframe_list_filter if 'search.alexanderstreet.com' in s]
            for link in library_iframe_alex:
                library_media.setdefault(link, [])
                library_media[link].append('Manually Check for Captions')
                library_media[link].append('')
                library_media[link].append('')
                library_media[link].append('')
                library_media[link].append(discuss_location)
            library_iframe_kanopy = [s for s in iframe_list_filter if 'kanopystreaming-com' in s]
            for link in library_iframe_kanopy:
                library_media.setdefault(link, [])
                library_media[link].append('Manually Check for Captions')
                library_media[link].append('')
                library_media[link].append('')
                library_media[link].append('')
                library_media[link].append(discuss_location)
            youtube_iframe = [s for s in iframe_list_filter if re.search(youtube_pattern, s)]
            vimeo_iframe = [s for s in iframe_list_filter if 'vimeo.com' in s]
            for v_link in vimeo_iframe:
                vimeo_link.setdefault(v_link, [])
                vimeo_link[v_link].append(item.html_url)
            for video in soup.find_all('video'):
                instructure = video.get('class')
                media_id = video.get('data-media_comment_id')
                for media_comment in instructure:
                    if media_comment == 'instructure_inline_media_comment video_comment':
                        m_link = 'Video Media Comment {}'.format(media_id)
                        media_link.setdefault(m_link, [])
                        media_link[m_link].append('Manually Check for Captions')
                        media_link[m_link].append('')
                        media_link[m_link].append('')
                        media_link[m_link].append('')
                        media_link[m_link].append(discuss_location)
            for audio in soup.find_all('audio'):
                instructure = audio.get('class')
                media_id = audio.get('data-media_comment_id')
                for media_comment in instructure:
                    if media_comment == 'instructure_inline_media_comment audio_comment':
                        m_link = 'Audio Media Comment {}'.format(media_id)
                        media_link.setdefault(m_link, [])
                        media_link[m_link].append('Manually Check for Captions')
                        media_link[m_link].append('')
                        media_link[m_link].append('')
                        media_link[m_link].append('')
                        media_link[m_link].apppend(discuss_location)
            for file_link in soup.find_all('a'):
                instructure = file_link.get('class')
                location = file_link.get('data-api-endpoint')
                if location:
                    try:
                        file_id = location.split('/')[-1:]
                        file_id_string = ', '.join(file_id)
                        get_file = course.get_file(file_id_string)
                        file_location = get_file.url.split('?')[0]
                        if 'audio' in get_file.mime_class:
                            link_name = 'Linked Audio File: {}'.format(get_file.display_name)
                            link_media.setdefault(link_name, [])
                            link_media[link_name].append('Manually Check for Captions')
                            link_media[link_name].append('')
                            link_media[link_name].append('')
                            link_media[link_name].append('')
                            link_media[link_name].append(discuss_location)
                            link_media[link_name].append(file_location)
                        if 'video' in get_file.mime_class:
                            link_name = 'Linked Video File: {}'.format(get_file.display_name)
                            link_media.setdefault(link_name, [])
                            link_media[link_name].append('Manually Check for Captions')
                            link_media[link_name].append('')
                            link_media[link_name].append('')
                            link_media[link_name].append('')
                            link_media[link_name].append(discuss_location)
                            link_media[link_name].append(file_location)
                        if 'flash' in get_file.mime_class:
                            link_name = 'Linked SWF File: {}'.format(get_file.display_name)
                            link_media.setdefault(link_name, [])
                            link_media[link_name].append('Manually Check for Captions')
                            link_media[link_name].append('')
                            link_media[link_name].append('')
                            link_media[link_name].append('')
                            link_media[link_name].append(discuss_location)
                            link_media[link_name].append(file_location)
                    except:
                        pass
# Checks the syllabus in a canvas course for media links
syllabus = canvas.get_course(course_id, include='syllabus_body')
if syllabus.syllabus_body:
    syllabus_location = '{}/{}/assignments/syllabus'.format(courses_url, course_id)
    print('Checking Syllabus')
    try:
        contents = syllabus.syllabus_body
        soup = BeautifulSoup(contents, 'html.parser')
        href_list = []
        for link in soup.find_all('a'):
            href_list.append(link.get('href'))
        href_list_filter = filter(None, href_list)
        library_embed_fod = [s for s in href_list_filter if 'fod.infobase.com' in s]
        for link in library_embed_fod:
            library_media.setdefault(link, [])
            library_media[link].append('Manually Check for Captions')
            library_media[link].append('')
            library_media[link].append('')
            library_media[link].append('')
            library_media[link].append(syllabus_location)
        library_embed_alex = [s for s in href_list_filter if 'search.alexanderstreet.com' in s]
        for link in library_embed_alex:
            library_media.setdefault(link, [])
            library_media[link].append('Manually Check for Captions')
            library_media[link].append('')
            library_media[link].append('')
            library_media[link].append('')
            library_media[link].append(syllabus_location)
        library_embed_kanopy = [s for s in href_list_filter if 'kanopystreaming-com' in s]
        for link in library_embed_kanopy:
            library_media.setdefault(link, [])
            library_media[link].append('Manually Check for Captions')
            library_media[link].append('')
            library_media[link].append('')
            library_media[link].append('')
            library_media[link].append(syllabus_location)
        youtube_embed = [s for s in href_list_filter if re.search(youtube_pattern, s)]
        vimeo_embed = [s for s in href_list_filter if 'vimeo.com' in s]
        for link in youtube_embed:
            youtube_link.setdefault(link, [])
            youtube_link[link].append(syllabus_location)
        for v_link in vimeo_embed:
            vimeo_link.setdefault(v_link, [])
            vimeo_link[v_link].append(syllabus_location)
        iframe_list = []
        for link in soup.find_all('iframe'):
            iframe_list.append(link.get('src'))
        iframe_list_filter = filter(None, iframe_list)
        library_iframe_fod = [s for s in iframe_list_filter if 'fod.infobase.com' in s]
        for link in library_iframe_fod:
            library_media.setdefault(link, [])
            library_media[link].append('Manually Check for Captions')
            library_media[link].append('')
            library_media[link].append('')
            library_media[link].append('')
            library_media[link].append(syllabus_location)
        library_iframe_alex = [s for s in iframe_list_filter if 'search.alexanderstreet.com' in s]
        for link in library_iframe_alex:
            library_media.setdefault(link, [])
            library_media[link].append('Manually Check for Captions')
            library_media[link].append('')
            library_media[link].append('')
            library_media[link].append('')
            library_media[link].append(syllabus_location)
        library_iframe_kanopy = [s for s in iframe_list_filter if 'kanopystreaming-com' in s]
        for link in library_iframe_kanopy:
            library_media.setdefault(link, [])
            library_media[link].append('Manually Check for Captions')
            library_media[link].append('')
            library_media[link].append('')
            library_media[link].append('')
            library_media[link].append(syllabus_location)
        youtube_iframe = [s for s in iframe_list if re.search(youtube_pattern, s)]
        vimeo_iframe = [s for s in iframe_list if 'vimeo.com' in s]
        for link in youtube_iframe:
            youtube_link.setdefault(link, [])
            youtube_link[link].append(syllabus_location)
        for v_link in vimeo_iframe:
            vimeo_link.setdefault(v_link, [])
            vimeo_link[v_link].append(syllabus_location)
        for video in soup.find_all('video'):
            instructure = video.get('class')
            media_id = video.get('data-media_comment_id')
            for media_comment in instructure:
                if media_comment == 'instructure_inline_media_comment':
                    m_link = 'Video Media Comment {}'.format(media_id)
                    media_link.setdefault(m_link, [])
                    media_link[m_link].append('Manually Check for Captions')
                    media_link[m_link].append('')
                    media_link[m_link].append('')
                    media_link[m_link].append('')
                    media_link[m_link].append(syllabus_location)
        for audio in soup.find_all('audio'):
            instructure = audio.get('class')
            media_id = audio.get('data-media_comment_id')
            for media_comment in instructure:
                if media_comment == 'instructure_inline_media_comment':
                    m_link = 'Audio Media Comment {}'.format(media_id)
                    media_link.setdefault(m_link, [])
                    media_link[m_link].append('Manually Check for Captions')
                    media_link[m_link].append('')
                    media_link[m_link].append('')
                    media_link[m_link].append('')
                    media_link[m_link].append(syllabus_location)
        for file_link in soup.find_all('a'):
            instructure = file_link.get('class')
            location = file_link.get('data-api-endpoint')
            if location:
                try:
                    file_id = location.split('/')[-1:]
                    file_id_string = ', '.join(file_id)
                    get_file = course.get_file(file_id_string)
                    file_location = get_file.url.split('?')[0]
                    if 'audio' in get_file.mime_class:
                        link_name = 'Linked Audio File: {}'.format(get_file.display_name)
                        link_media.setdefault(link_name, [])
                        link_media[link_name].append('')
                        link_media[link_name].append('')
                        link_media[link_name].append('')
                        link_media[link_name].append(syllabus_location)
                        link_media[link_name].append(file_location)
                    if 'video' in get_file.mime_class:
                        link_name = 'Linked Video File: {}'.format(get_file.display_name)
                        link_media.setdefault(link_name, [])
                        link_media[link_name].append('Manually Check for Captions')
                        link_media[link_name].append('')
                        link_media[link_name].append('')
                        link_media[link_name].append('')
                        link_media[link_name].append(syllabus_location)
                        link_media[link_name].append(file_location)
                    if 'flash' in get_file.mime_class:
                        link_name = 'Linked SWF File: {}'.format(get_file.display_name)
                        link_media.setdefault(link_name, [])
                        link_media[link_name].append('Manually Check for Captions')
                        link_media[link_name].append('')
                        link_media[link_name].append('')
                        link_media[link_name].append('')
                        link_media[link_name].append(syllabus_location)
                        link_media[link_name].append(file_location)
                except:
                    pass
    except:
        pass

# Checks all module external URLs and Files in a canvas course for media links
modules = course.get_modules()
if modules:
    print('Checking Modules')
    for module in modules:
        items = module.list_module_items(include='content_details')
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
                if 'search.alexanderstreet.com' in href:
                    library_embed.append(href)
                if 'fod.infobase.com' in href:
                    library_embed.append(href)
                if 'kanopystreaming-com' in href:
                    library_embed.append(href)
            for y_link in youtube_embed:
                youtube_link.setdefault(y_link, [])
                youtube_link[y_link].append(module_url)
            for v_link in vimeo_embed:
                vimeo_link.setdefault(v_link, [])
                vimeo_link[v_link].append(module_url)
            for link in library_embed:
                library_media.setdefault(link, [])
                library_media[link].append('Manually Check for Captions')
                library_media[link].append('')
                library_media[link].append('')
                library_media[link].append('')
                library_media[link].append(module_url)
            if item.type == 'File':
                try:
                    module_location = item.html_url
                    file_id = item.content_id
                    get_file = course.get_file(file_id)
                    if 'audio' in get_file.mime_class:
                        link_name = 'Linked Audio File: {}'.format(get_file.display_name)
                        link_media.setdefault(link_name, [])
                        link_media[link_name].append('Manually Check for Captions')
                        link_media[link_name].append('')
                        link_media[link_name].append('')
                        link_media[link_name].append('')
                        link_media[link_name].append(module_location)
                        link_media[link_name].append(file_location)
                    if 'video' in get_file.mime_class:
                        link_name = 'Linked Video File: {}'.format(get_file.display_name)
                        link_media.setdefault(link_name, [])
                        link_media[link_name].append('Manually Check for Captions')
                        link_media[link_name].append('')
                        link_media[link_name].append('')
                        link_media[link_name].append('')
                        link_media[link_name].append(module_location)
                        link_media[link_name].append(file_location)
                    if 'flash' in get_file.mime_class:
                        link_name = 'Linked SWF File: {}'.format(get_file.display_name)
                        link_media.setdefault(link_name, [])
                        link_media[link_name].append('Manually Check for Captions')
                        link_media[link_name].append('')
                        link_media[link_name].append('')
                        link_media[link_name].append('')
                        link_media[link_name].append(module_location)
                        link_media[link_name].append(file_location)
                except:
                    pass

# Checks all announcements in a canvas course for media links
announce = course.get_discussion_topics(only_announcements=True)
if announce:
    print('Checking Announcements')
    for item in announce:
        announce_location = item.html_url
        if item.message:
            contents = item.message.encode('utf-8')
            soup = BeautifulSoup(contents, 'html.parser')
            href_list = []
            for link in soup.find_all('a'):
                href_list.append(link.get('href'))
            href_list_filter = filter(None, href_list)
            library_embed_fod = [s for s in href_list_filter if 'fod.infobase.com' in s]
            for link in library_embed_fod:
                library_media.setdefault(link, [])
                library_media[link].append('Manually Check for Captions')
                library_media[link].append('')
                library_media[link].append('')
                library_media[link].append('')
                library_media[link].append(announce_location)
            library_embed_alex = [s for s in href_list_filter if 'search.alexanderstreet.com' in s]
            for link in library_embed_alex:
                library_media.setdefault(link, [])
                library_media[link].append('Manually Check for Captions')
                library_media[link].append('')
                library_media[link].append('')
                library_media[link].append('')
                library_media[link].append(announce_location)
            library_embed_kanopy = [s for s in href_list_filter if 'kanopystreaming-com' in s]
            for link in library_embed_kanopy:
                library_media.setdefault(link, [])
                library_media[link].append('Manually Check for Captions')
                library_media[link].append('')
                library_media[link].append('')
                library_media[link].append('')
                library_media[link].append(announce_location)
            youtube_embed = [s for s in href_list_filter if re.search(youtube_pattern, s)]
            vimeo_embed = [s for s in href_list_filter if 'vimeo.com' in s]
            for link in youtube_embed:
                youtube_link.setdefault(link, [])
                youtube_link[link].append(announce_location)
            for v_link in vimeo_embed:
                vimeo_link.setdefault(v_link, [])
                vimeo_link[v_link].append(announce_location)
            iframe_list = []
            for link in soup.find_all('iframe'):
                iframe_list.append(link.get('src'))
            iframe_list_filter = filter(None, iframe_list)
            library_iframe_fod = [s for s in iframe_list_filter if 'fod.infobase.com' in s]
            for link in library_iframe_fod:
                library_media.setdefault(link, [])
                library_media[link].append('Manually Check for Captions')
                library_media[link].append('')
                library_media[link].append('')
                library_media[link].append('')
                library_media[link].append(announce_location)
            library_iframe_alex = [s for s in iframe_list_filter if 'search.alexanderstreet.com' in s]
            for link in library_iframe_alex:
                library_media.setdefault(link, [])
                library_media[link].append('Manually Check for Captions')
                library_media[link].append('')
                library_media[link].append('')
                library_media[link].append('')
                library_media[link].append(announce_location)
            library_iframe_kanopy = [s for s in iframe_list_filter if 'kanopystreaming-com' in s]
            for link in library_iframe_kanopy:
                library_media.setdefault(link, [])
                library_media[link].append('Manually Check for Captions')
                library_media[link].append('')
                library_media[link].append('')
                library_media[link].append('')
                library_media[link].append(announce_location)
            youtube_iframe = [s for s in iframe_list_filter if re.search(youtube_pattern, s)]
            vimeo_iframe = [s for s in iframe_list_filter if 'vimeo.com' in s]
            for link in youtube_iframe:
                youtube_link.setdefault(link, [])
                youtube_link[link].append(announce_location)
            for v_link in vimeo_iframe:
                vimeo_link.setdefault(v_link, [])
                vimeo_link[v_link].append(announce_location)
            for video in soup.find_all('video'):
                instructure = video.get('class')
                media_id = video.get('data-media_comment_id')
                for media_comment in instructure:
                    if media_comment == 'instructure_inline_media_comment video_comment':
                        m_link = 'Video Media Comment {}'.format(media_id)
                        media_link.setdefault(m_link, [])
                        media_link[m_link].append('Manually Check for Captions')
                        media_link[m_link].append('')
                        media_link[m_link].append('')
                        media_link[m_link].append('')
                        media_link[m_link].append(announce_location)
            for audio in soup.find_all('audio'):
                instructure = audio.get('class')
                media_id = audio.get('data-media_comment_id')
                for media_comment in instructure:
                    if media_comment == 'instructure_inline_media_comment audio_comment':
                        m_link = 'Audio Media Comment {}'.format(media_id)
                        media_link.setdefault(m_link, [])
                        media_link[m_link].append('Manually Check for Captions')
                        media_link[m_link].append('')
                        media_link[m_link].append('')
                        media_link[m_link].append('')
                        media_link[m_link].append(announce_location)
            for file_link in soup.find_all('a'):
                instructure = file_link.get('class')
                location = file_link.get('data-api-endpoint')
                if location:
                    try:
                        file_id = location.split('/')[-1:]
                        file_id_string = ', '.join(file_id)
                        get_file = course.get_file(file_id_string)
                        file_location = get_file.url.split('?')[0]
                        if 'audio' in get_file.mime_class:
                            link_name = 'Linked Audio File: {}'.format(get_file.display_name)
                            link_media.setdefault(link_name, [])
                            link_media[link_name].append('Manually Check for Captions')
                            link_media[link_name].append('')
                            link_media[link_name].append('')
                            link_media[link_name].append('')
                            link_media[link_name].append(announce_location)
                            link_media[link_name].append(file_location)
                        if 'video' in get_file.mime_class:
                            link_name = 'Linked Video File: {}'.format(get_file.display_name)
                            link_media.setdefault(link_name, [])
                            link_media[link_name].append('Manually Check for Captions')
                            link_media[link_name].append('')
                            link_media[link_name].append('')
                            link_media[link_name].append('')
                            link_media[link_name].append(announce_location)
                            link_media[link_name].append(file_location)
                        if 'flash' in get_file.mime_class:
                            link_name = 'Linked SWF File: {}'.format(get_file.display_name)
                            link_media.setdefault(link_name, [])
                            link_media[link_name].append('Manually Check for Captions')
                            link_media[link_name].append('')
                            link_media[link_name].append('')
                            link_media[link_name].append('')
                            link_media[link_name].append(announce_location)
                            link_media[link_name].append(file_location)
                    except:
                        pass
# Uses YouTube API to check each video for captions
print('Checking YouTube Captions')
for key in youtube_link:
    if 'playlist' in key:
        youtube_link[key].insert(0, 'this is a playlist, check individual videos')
    else:
        video_id = re.findall(youtube_pattern, key, re.MULTILINE | re.IGNORECASE)
        for item in video_id:
            is_ASR = False
            is_standard = False
            try:
                r = requests.get('{}?part=snippet&videoId={}&key={}'.format(
                    google_url, item, youtube_key
                ))
                data = r.json()
                if data['items']:
                    for e in data['items']:
                        if e['snippet']['language'] == 'en':
                            if e['snippet']['trackKind'] == 'standard':
                                is_standard = True
                            if e['snippet']['trackKind'] == 'ASR':
                                is_ASR = True

                    if is_standard is True:
                            youtube_link[key].insert(0, 'Captions found in English')
                            youtube_link[key].insert(1, '')
                            youtube_link[key].insert(2, '')
                            youtube_link[key].insert(3, '')
                    if is_standard is False and is_ASR is True:
                        youtube_link[key].insert(0, 'Automatic Captions in English')
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
                    if is_standard is False and is_ASR is False:
                        youtube_link[key].insert(0, 'No Captions in English')
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
                if not data['items']:
                    youtube_link[key].insert(0, 'No Captions')
                    r = requests.get('{}?part=contentDetails&id={}&key={}'.format(
                        google_video, item, youtube_key)
                    )
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
            vimeo_link[link].insert(0, 'Unable to Vimeo Check Video')
            vimeo_link[link].insert(1, '')
            vimeo_link[link].insert(2, '')
            vimeo_link[link].insert(3, '')
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
done = time.time() - start_time
if done > 60:
    new_done = done // 60
    print('This request took ' + str(new_done) + ' minutes')
else:
    print('This request took ' + str(done) + ' seconds')
