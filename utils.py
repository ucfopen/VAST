from __future__ import print_function


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
