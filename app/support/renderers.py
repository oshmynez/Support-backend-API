import json

from rest_framework.renderers import JSONRenderer


class UserJSONRenderer(JSONRenderer):
    """Outputting the received data to the user field"""
    charset = 'utf-8'

    def render(self, data, media_type=None, renderer_context=None):
        errors = data.get('errors', None)
        if errors is not None:
            return super(UserJSONRenderer, self).render(data)

        return json.dumps({
            'user': data
        })


class TicketJSONRenderer(JSONRenderer):
    """Outputting the received data to the ticket field"""
    charset = 'utf-8'

    def render(self, data, media_type=None, renderer_context=None):
        errors = data.get('errors', None)
        if errors is not None:
            return super(TicketJSONRenderer, self).render(data)

        return json.dumps({
            'ticket': data
        })
