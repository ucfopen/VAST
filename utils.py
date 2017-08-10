from __future__ import print_function
import re

from vast_config import youtube_pattern, lib_media_urls


def add_entry(
    media_dict, link_name, caption_status, page_location,
    hour='', minute='', second='', file_location=''
):
    """
    Adds an entry to the provided dictionary at the appropriate key.

    :param media_dict: The dictionary to add the entry to.
    :type media_dict: dict
    :param link_name: The name to identify a link by - usually the URL.
    :type link_name: str
    :param caption_status: A short description of whether or not
        captions were found, what language, or if the user must
        manually check.
    :type caption_status: str
    :param page_location: The full URL to the resource in Canvas.
    :type page_location: str
    :param hour: The hours place of the duration of a video
    :type: str
    :param minute: The minutes place of the duration of a video
    :type: str
    :param second: The seconds place of the duration of a video
    :type: str
    :param file_location: The full URL to the file in Canvas.
    :type: str

    :returns: None
    """
    media_dict.setdefault(link_name, [])
    media_dict[link_name] = [caption_status, hour, minute, second, page_location, file_location]


def process_contents(
    soup, course, page_location,
    youtube_link, vimeo_link, media_link, link_media, library_media  # TODO: kill these with fire
):
    """
    Process the provided contents

    :param soup:
    :type soup: :class:`bs4.BeautifulSoup`
    :param course:
    :type course: :class:`canvasapi.course.Course`
    :param page_location: The full URL to the resource in Canvas.
    :type page_location: str or unicode
    """

    # Process Anchor Tags
    href_href_list = []
    for link in soup.find_all('a'):
        href_href_list.append(link.get('href'))

        location = link.get('data-api-endpoint')
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
        # Matches Vimeo
        if 'vimeo.com' in link:
            vimeo_link.setdefault(link, [])
            vimeo_link[link].append(page_location)
        # Matches YouTube
        elif re.search(youtube_pattern, link):
            youtube_link.setdefault(link, [])
            youtube_link[link].append(page_location)
        # Matches library media from lib_media_urls
        elif any(match_str in link for match_str in lib_media_urls):
            add_entry(library_media, link, 'Manually Check for Captions', page_location)

    # Process IFrames
    iframe_list = []
    for link in soup.find_all('iframe'):
        iframe_list.append(link.get('src'))
    iframe_list_filter = filter(None, iframe_list)

    for link in iframe_list_filter:
        # Matches Vimeo
        if 'vimeo.com' in link:
            vimeo_link.setdefault(link, [])
            vimeo_link[link].append(page_location)
        # Matches YouTube
        elif re.search(youtube_pattern, link):
            youtube_link.setdefault(link, [])
            youtube_link[link].append(page_location)
        # Matches library media from lib_media_urls
        elif any(match_str in link for match_str in lib_media_urls):
            add_entry(library_media, link, 'Manually Check for Captions', page_location)

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
