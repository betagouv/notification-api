from abc import ABC, abstractmethod

from app.dao import templates_dao


class SerialisedModel(ABC):

    """
    A SerialisedModel takes a dictionary, typically created by
    serialising a database object. It then takes the value of specified
    keys from the dictionary and adds them to itself as properties, so
    that it can be interacted with like a normal database model object,
    but with no risk that it will actually go back to the database.
    """

    @property
    @abstractmethod
    def ALLOWED_PROPERTIES(self):
        pass

    def __init__(self, _dict):
        for property in self.ALLOWED_PROPERTIES:
            setattr(self, property, _dict[property])

    def __dir__(self):
        return super().__dir__() + list(sorted(self.ALLOWED_PROPERTIES))


class SerialisedTemplate(SerialisedModel):
    ALLOWED_PROPERTIES = {
        'archived',
        'content',
        'id',
        'postage',
        'process_type',
        'reply_to_text',
        'subject',
        'template_type',
        'version',
    }

    @classmethod
    def from_id_and_service_id(cls, template_id, service_id):
        return cls(cls.get_dict(template_id, service_id))

    @staticmethod
    def get_dict(template_id, service_id):
        from app.schemas import template_schema

        fetched_template = templates_dao.dao_get_template_by_id_and_service_id(
            template_id=template_id,
            service_id=service_id
        )

        template_dict = template_schema.dump(fetched_template).data

        return template_dict