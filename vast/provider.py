import logging
from abc import ABC
from typing import Iterable, List, Union

from attr import dataclass
from canvasapi import Canvas
from canvasapi.exceptions import CanvasException

logger = logging.getLogger(__name__)


@dataclass
class ContentItem:
    location: str
    html: Union[str, None] = None
    mime_class: Union[str, None] = None
    external_url: Union[str, None] = None


class ResourceProvider(ABC):
    name: str = ""
    function: str = ""
    field: str = ""
    options: dict = {}

    def __init__(self, config):
        self.config = config
        self.client = Canvas(self.config.canvas_api_url, self.config.canvas_api_key)
        self.course = self.client.get_course(self.config.course_id)

    def fetch(self) -> Iterable[ContentItem]:
        if not hasattr(self, "function"):
            raise NotImplementedError(
                "{} requires either a definition of a canvasapi course 'function'"
                "or an implementation of 'fetch()'".format(self.__class__)
            )
        function = getattr(self.course, self.function)

        if hasattr(self, "options"):
            items = function(**self.options)
        else:
            items = function()

        if not hasattr(self, "field"):
            raise NotImplementedError(
                "{} requires either a definition of 'field'"
                "or an implementation of 'fetch()'".format(self.__class__)
            )

        for item in items:
            content = ContentItem(
                html=getattr(item, self.field), location=item.html_url
            )
            logger.debug(content)
            yield content


class AnnouncementService(ResourceProvider):
    name = "announcements"
    function = "get_discussion_topics"
    field = "message"
    options = {"only_announcements": "True"}


class AssignmentService(ResourceProvider):
    name = "assignments"
    function = "get_assignments"
    field = "description"


class DiscussionService(ResourceProvider):
    name = "discussions"
    function = "get_discussion_topics"
    field = "message"


class PageService(ResourceProvider):
    name = "pages"

    def fetch(self):
        retrieved_data = []
        pages = self.course.get_pages()
        for page in pages:
            _page = self.course.get_page(page.url)
            retrieved_data.append(ContentItem(html=_page.body, location=page.html_url))
        return retrieved_data


class SyllabusService(ResourceProvider):
    name = "syllabus"

    def fetch(self) -> List[ContentItem]:
        syllabus = self.client.get_course(
            self.config.course_id, include="syllabus_body"
        )
        if not syllabus.syllabus_body:
            return []

        url = "{}/courses/{}/assignments/syllabus".format(
            self.config.canvas_api_url, self.config.course_id
        )
        return [ContentItem(html=syllabus.syllabus_body, location=url)]


class ModuleService(ResourceProvider):
    name = "modules"

    def fetch(self):
        retrieved_data = []
        modules = self.course.get_modules()
        for module in modules:
            for item in module.get_module_items(include="content_details"):
                if item.type == "ExternalUrl":
                    retrieved_data.append(
                        ContentItem(
                            external_url=item.external_url, location=item.html_url
                        )
                    )
                if item.type == "File":
                    try:
                        file = self.course.get_file(item.content_id)
                        path = file.url.split("?")[0]
                        retrieved_data.append(
                            ContentItem(
                                external_url=path,
                                location=item.html_url,
                                mime_class=file.mime_class,
                            )
                        )
                    except CanvasException:
                        logger.exception("Unable to fetch linked file")
                        continue
        return retrieved_data
