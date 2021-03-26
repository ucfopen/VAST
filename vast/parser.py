import logging
import re
from typing import List, Union

import bs4

from vast.media import Media, MediaType
from vast.provider import ContentItem

YOUTUBE_PLAYLIST_PATTERN = r"[?&]list=([^#\&\?\s]+)"  # noqa
YOUTUBE_PATTERN = r"(?:https?:\/\/)?(?:[0-9A-Z-]+\.)?(?:youtube|youtu|youtube-nocookie)\.(?:com|be)\/(?:watch\?v=|watch\?.+&v=|embed\/|v\/|.+\?v=)?([^&=\n%\?]{11})"  # noqa
VIMEO_PATTERN = r"(?:https?:\/\/)?:?\/\/(www\.|player\.)?vimeo.com\/(?:channels\/(?:\w+\/)?|video\/(?:\w+\/)?|groups\/([^\/]*)\/videos\/|)(\d+)(?:|\/\?)"  # noqa


logger = logging.getLogger(__name__)

MEDIATYPES_MAP = {
    "data-api-endpoint": MediaType.FILE,
    "data-media_comment_type": MediaType.MEDIA_COMMENT,
}

LIBRARY_MEDIA_URLS = [
    "fod.infobase.com",
    "search.alexanderstreet.com",
    "kanopystreaming-com",
]


class ContentItemParser:
    def __init__(self, content_item: ContentItem) -> None:
        self.content_item = content_item
        self.soup = bs4.BeautifulSoup(content_item.html, "html.parser")

    def parse_html(self) -> List[Media]:
        data = []
        data.extend(self._parse_a_tags())
        data.extend(self._parse_native_media_tags())
        data.extend(self._parse_iframes())
        return data

    def _discover(
        self,
        element: bs4.Tag,
        attribute: str,
        media_type: Union[MediaType, None] = None,
        url: str = None,
    ) -> Union[Media, None]:
        tag = element.get(attribute)
        if tag:

            try:
                media_type = media_type or classify_media_type(tag)
            except LookupError:
                import ipdb

                ipdb.set_trace()
                logger.warning("Couldn't classify media type for %s", tag)
                return None

            discovered = Media(
                content_item=self.content_item,
                type=media_type,
                metadata={},
                url=url or tag,
                element=element,
            )
            logger.debug("Discovered %s (%s)", discovered.url, discovered.type)
            return discovered
        return None

    def _parse_a_tags(self) -> List[Media]:
        media = []
        for element in self.soup.find_all("a", href=True):
            # files have three return types: audio, video, flash
            files = self._discover(element, "data-api-endpoint")
            if files:
                media.append(files)
                continue

            # media comments have two return types: audio, video
            media_comments = self._discover(
                element, "data-media_comment_type", MediaType.MEDIA_COMMENT
            )
            if media_comments:
                media.append(media_comments)
                continue

            links = self._discover(
                element,
                "href",
            )
            if links:
                media.append(links)

        return media

    def _parse_native_media_tags(self) -> List[Media]:
        media = []

        # videos can return video media comments
        for element in self.soup.find_all("video"):
            video_comments = self._discover(
                element,
                "data-media_comment_type",
                url=element.get("data-media_comment_id"),
            )
            if video_comments:
                media.append(video_comments)
                continue

            if element.find("source"):
                embedded_video = self._discover(element, "src")
                if embedded_video:
                    media.append(embedded_video)
                    continue

        # audio can return audio media comment _or_ embedded Canvas audio
        for element in self.soup.find_all("audio"):
            audio_comments = self._discover(
                element,
                "data-media_comment_type",
                url=element.get("data-media_comment_id"),
            )
            if audio_comments:
                media.append(audio_comments)
                continue

            embedded_audio = self._discover(element, "src")
            if embedded_audio:
                media.append(embedded_audio)
                continue

        return media

    def _parse_iframes(self) -> List[Media]:
        media = []
        for element in self.soup.find_all("iframe"):
            iframes = self._discover(element, "src")
            if iframes:
                media.append(iframes)

            videos = self._discover(
                element,
                "data-media-type",
                url=element.get("data-media-id"),
            )
            if videos:
                media.append(videos)
                continue

            audio = self._discover(
                element,
                "data-media-type",
                url=element.get("data-media-id"),
            )
            if audio:
                media.append(audio)
                continue

        return media


def parse_content(content_item: ContentItem) -> List[Media]:
    logger.debug("Parsing %s", content_item.location)
    if not content_item.external_url:
        return ContentItemParser(content_item).parse_html()

    try:
        discovered = Media(
            content_item=content_item,
            type=classify_media_type(
                content_item.mime_class or content_item.external_url
            ),
            url=content_item.external_url,
            has_captions=False,
            metadata={},
        )
        logger.debug("Discovered %s (%s)", discovered.url, discovered.type)

        return [discovered]
    except LookupError:
        logger.warn("Couldn't classify media type for %s", content_item.location)
        return []


def get_metadata(media: Media) -> Media:
    media.has_captions = True
    return media


def classify_media_type(identifier) -> MediaType:
    """
    Classify the media as youtube or vimeo or other. Returns True if
    media type allows for further checking of captions.
    """
    if re.search(YOUTUBE_PLAYLIST_PATTERN, identifier):
        return MediaType.YOUTUBE_PLAYLIST
    elif re.search(YOUTUBE_PATTERN, identifier):
        return MediaType.YOUTUBE
    elif re.search(VIMEO_PATTERN, identifier):
        return MediaType.VIMEO
    elif any(url in identifier for url in LIBRARY_MEDIA_URLS):
        return MediaType.LIBRARY_MEDIA
    elif "files" in identifier:
        return MediaType.FILE
    elif "video" == identifier:
        return MediaType.VIDEO_COMMENT
    elif "audio" == identifier:
        return MediaType.AUDIO_COMMENT
    else:
        raise LookupError("Couldn't find media type for %s", identifier)
