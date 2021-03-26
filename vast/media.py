from enum import Enum
from typing import Union

import bs4
from attr import dataclass

from vast.provider import ContentItem


class MediaType(Enum):
    YOUTUBE_PLAYLIST = "youtube_playlist"
    YOUTUBE = "youtube"
    VIMEO = "vimeo"
    EXTERNAL = "external"
    FILE = "file"
    MEDIA_COMMENT = "media_comment"
    VIDEO_COMMENT = "video_comment"
    AUDIO_COMMENT = "audio_comment"
    LIBRARY_MEDIA = "library_media"


@dataclass
class Media:
    content_item: ContentItem
    url: str
    metadata: dict
    type: MediaType
    element: Union[bs4.Tag, None] = None
    has_captions: bool = False
    # VAST only checks for captions in English currently, but providers
    # support multiple languages
    # config file: set languages to search for
    # captions_found = [
    #   Caption(language="en"),
    #   Caption(language="fr")
    # ]
    # [caption]
