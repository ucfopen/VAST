from abc import ABC

from canvasapi import Canvas


class ResourceProvider(ABC):
    def __init__(self, config):
        self.config = config
        self.client = Canvas(self.config.api_url, self.config.api_key)
        self.course = self.client.get_course(self.config.course_id)

    def get_course_name(self):
        return self.course.name

    def fetch(self):
        if not hasattr(self, 'function'):
            raise NotImplementedError(
                "{} requires either a definition of 'function' or an "
                "implementation of 'fetch()'".format(self.__class__)
            )

        function = getattr(self.course, self.function)

        if hasattr(self, 'options'):
            items = function(**self.options)
        else:
            items = function()

        retrieved_data = {
            'info': [],
            'is_flat': True
        }

        for item in items:
            retrieved_data['info'].append((
                getattr(item, self.field),
                item.html_url,
            ))

        return retrieved_data


class SyllabusService(ResourceProvider):
    name = "syllabus"

    def fetch(self):
        syllabus = self.client.get_course(
            self.config.course_id,
            include='syllabus_body'
        )
        url = '{}/courses/{}/assignments/syllabus'.format(
            self.config.api_url,
            self.config.course_id
        )
        return {
            'info': [(syllabus.syllabus_body, url)],
            'is_flat': True
        }


class AnnouncementService(ResourceProvider):
    name = "announcements"
    function = "get_discussion_topics"
    field = "message"
    options = {'only_announcements': 'True'}


class ModuleService(ResourceProvider):
    name = "modules"

    def fetch(self):
        retrieved_data = {
            'info': [],
            'is_flat': False
        }

        modules = self.course.get_modules()
        for module in modules:
            for item in module.get_module_items(include='content_details'):
                if item.type == 'ExternalUrl':
                    retrieved_data['info'].append((
                        item.external_url,
                        item.html_url
                    ))
        return retrieved_data

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
        retrieved_data = {
            'info': [],
            'is_flat': True
        }

        pages = self.course.get_pages()
        for page in pages:
            p = self.course.get_page(page.url)
            retrieved_data['info'].append((p.body, page.html_url))
        return retrieved_data
