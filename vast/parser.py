import re

from bs4 import BeautifulSoup

youtube_playlist_pattern = r"[?&]list=([^#\&\?\s]+)"  # noqa
youtube_pattern = r"(?:https?:\/\/)?(?:[0-9A-Z-]+\.)?(?:youtube|youtu|youtube-nocookie)\.(?:com|be)\/(?:watch\?v=|watch\?.+&v=|embed\/|v\/|.+\?v=)?([^&=\n%\?]{11})"  # noqa
vimeo_pattern = r"(?:https?:\/\/)?:?\/\/(www\.|player\.)?vimeo.com\/(?:channels\/(?:\w+\/)?|video\/(?:\w+\/)?|groups\/([^\/]*)\/videos\/|)(\d+)(?:|\/\?)"  # noqa
lib_media_urls = [
    "fod.infobase.com",
    "search.alexanderstreet.com",
    "kanopystreaming-com",
]


class Parser:
    to_check = []
    no_check = []

    def parse_content(self, content_pair, flat):
        """
        Parse each content pair returning 2 lists, one that
        needs to be checked for captions and one that does not
        """
        # Check all links
        if flat:
            soup = BeautifulSoup(content_pair[0], "html.parser")

            for elem in soup.find_all("a", href=True):
                # Check if the link is an internal Canvas file
                file_api_endpoint = elem.get("data-api-endpoint")
                if file_api_endpoint:
                    self.no_check.append(
                        {
                            "type": "internal file",
                            "link_loc": content_pair[1],
                            "media_loc": file_api_endpoint,
                            "meta_data": [],
                        }
                    )

                # Check if the link is a media comment (internal file)
                data_media_comment = elem.get("data-media_comment_type")
                if data_media_comment:
                    self.no_check.append(
                        {
                            "type": "canvas media comment",
                            "link_loc": content_pair[1],
                            "media_loc": content_pair[1],
                            "meta_data": [],
                        }
                    )

                # Check any plain anchor tags with just an href
                # Otherwise not flat and just two plain links in content pair to be classified
                a_href = elem.get("href")
                check, media_type = self.classify(a_href)
                if check:
                    self.to_check.append(
                        {
                            "type": media_type,
                            "link_loc": content_pair[1],
                            "media_loc": a_href,
                            "captions": [],
                            "meta_data": [],
                        }
                    )

                # Check for library media in regular <a≥ tags
                if any(url in a_href for url in lib_media_urls):
                    self.no_check.append(
                        {
                            "type": "library media",
                            "link_loc": content_pair[1],
                            "media_loc": a_href,
                            "meta_data": [],
                        }
                    )

            # Check for Canvas audio/video comments
            for elem in soup.find_all("video"):
                self.no_check.append(
                    {
                        "type": "canvas video comment",
                        "link_loc": content_pair[1],
                        "media_loc": elem.get("data-media_comment_id"),
                        "meta_data": [],
                    }
                )

            for elem in soup.find_all("audio"):
                self.no_check.append(
                    {
                        "type": "canvas audio comment",
                        "link_loc": content_pair[1],
                        "media_loc": elem.get("data-media_comment_id"),
                        "meta_data": [],
                    }
                )

            # Check all iframe elements
            for elem in soup.find_all("iframe"):
                src = elem.get("src")
                if src:
                    check, media_type = self.classify(src)
                    # Check for library media in iframes
                    if any(url in src for url in lib_media_urls):
                        self.no_check.append(
                            {
                                "type": "library media",
                                "link_loc": content_pair[1],
                                "media_loc": src,
                                "meta_data": [],
                            }
                        )
                    elif check:
                        self.to_check.append(
                            {
                                "type": media_type,
                                "link_loc": content_pair[1],
                                "media_loc": src,
                                "captions": [],
                                "meta_data": [],
                            }
                        )
                    else:
                        self.no_check.append(
                            {
                                "type": "external",
                                "link_loc": content_pair[1],
                                "media_loc": src,
                                "meta_data": [],
                            }
                        )
        else:
            # Otherwise not flat and just two plain links in content pair to be classified
            check, media_type = self.classify(content_pair[0])
            if check:
                self.to_check.append(
                    {
                        "type": media_type,
                        "link_loc": content_pair[1],
                        "media_loc": content_pair[0],
                        "captions": [],
                        "meta_data": [],
                    }
                )
            else:
                self.no_check.append(
                    {
                        "type": "external",
                        "link_loc": content_pair[1],
                        "media_loc": content_pair[0],
                        "meta_data": [],
                    }
                )

        return self.to_check, self.no_check

    def classify(self, link):
        """
        Classify the media as youtube or vimeo or other. Returns True if
        media type allows for further checking of captions.
        """
        if re.search(youtube_playlist_pattern, link):
            return True, "youtube_playlist"
        elif re.search(youtube_pattern, link):
            return True, "youtube"
        elif re.search(vimeo_pattern, link):
            return True, "vimeo"
        else:
            return False, "external"
