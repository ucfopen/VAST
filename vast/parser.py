from bs4 import BeautifulSoup
import re

youtube_playlist_pattern = r'[?&]list=([^#\&\?\s]+)'  # noqa
youtube_pattern = r'(?:https?:\/\/)?(?:[0-9A-Z-]+\.)?(?:youtube|youtu|youtube-nocookie)\.(?:com|be)\/(?:watch\?v=|watch\?.+&v=|embed\/|v\/|.+\?v=)?([^&=\n%\?]{11})'  # noqa
vimeo_pattern = r'(http|https)?:\/\/(www\.|player\.)?vimeo.com\/(?:channels\/(?:\w+\/)?|video\/(?:\w+\/)?|groups\/([^\/]*)\/videos\/|)(\d+)(?:|\/\?)'  # noqa

lib_media_urls = ['fod.infobase.com', 'search.alexanderstreet.com', 'kanopystreaming-com']

class Parser:
    to_check = []
    no_check = []

    def parse_content(self, content_pair, flat):
        # Check all links
        if flat:
            soup = BeautifulSoup(content_pair[0], 'html.parser')

            for elem in soup.find_all('a'):
                # Check if the link is an internal Canvas file
                file_api_endpoint = elem.get('data-api-endpoint')
                if file_api_endpoint:
                    self.no_check.append({
                        'type': 'internal file',
                        'link_loc': content_pair[1],
                        'media_loc': file_api_endpoint
                    })

                # instructure inline media comment
                inline_media = elem.get('data-media_comment_type')
                if inline_media:
                    self.no_check.append({
                        'type': '{} media comment'.format(inline_media),
                        'link_loc': content_pair[1],
                        'media_loc': 'N/A'
                    })

                # Check all other specific anchor tags ...

            for elem in soup.find_all('video'):
                self.no_check.append({
                        'type': 'canvas video comment',
                        'link_loc': content_pair[1],
                        'media_loc': 'N/A'
                    })

            for elem in soup.find_all('audio'):
                self.no_check.append({
                        'type': 'canvas audio comment',
                        'link_loc': content_pair[1],
                        'media_loc': 'N/A'
                    })

            # Check all iframe elements
            for elem in soup.find_all('iframe'):
                src = elem.get('src')
                if src:
                    check, media_type = self.classify(src)
                    if check:
                        self.to_check.append({
                            'type': media_type,
                            'link_loc': content_pair[1],
                            'media_loc': src,
                            'captions': []
                        })
                    else:
                        self.no_check.append({
                            'type': 'external',
                            'link_loc': content_pair[1],
                            'media_loc': src
                        })
        else:
            # Otherwise not flat and just plain links in content pair to be classified
            check, media_type = self.classify(content_pair[0])
            if check:
                self.to_check.append({
                    'type': media_type,
                    'link_loc': content_pair[1],
                    'media_loc': content_pair[0],
                    'captions': []
                })
            else:
                self.no_check.append({
                    'type': 'external',
                    'link_loc': content_pair[1],
                    'media_loc': content_pair[0]
                })

        return self.to_check, self.no_check
                
    def classify(self, link):
        """
        Classify the media as youtube or vimeo or other. Returns True if 
        media type allows for further checking of captions.
        """
        if re.search(youtube_playlist_pattern, link):
            return True, 'youtube_playlist'
        elif re.search(youtube_pattern, link):
            return True, 'youtube'
        elif re.search(vimeo_pattern, link):
            return True, 'vimeo'
        else:
            return False, 'external'