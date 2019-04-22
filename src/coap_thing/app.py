"""This module contains an example CoAP thing to test observable endpoints"""
import asyncio
import json
import aiocoap
import aiocoap.resource as resource
from common.td_util import ThingDescriptionBuilder, ObjectBuilder

def td_builder():
    """Builds a thing description for this device"""
    td = ThingDescriptionBuilder('urn:coap-thing', 'CoAP Thing')

    schema = ObjectBuilder()
    schema.add_number('state')

    td.add_property('state', 'coap://localhost/state', schema.build(), True)
    td.add_event('stateChange', 'coap://localhost/state', schema.build())

    return td.build()

class PropertyResource(resource.ObservableResource):
    """Sample property on the device

    This is an observable endpoint so can be subscribed to
    """
    def __init__(self):
        """Sets the default state to 0"""
        super().__init__()
        self.content = {
            'state': 0
        }

    async def render_get(self, request):
        """Returns the state when a GET request is performed"""
        # pylint: disable=unused-argument
        return aiocoap.Message(payload=json.dumps(self.content).encode())

    async def render_put(self, request):
        """Updates the state when a PUT request is performed"""
        payload = json.loads(request.payload)
        self.content = {
            'state': payload['state']
        }
        self.updated_state()
        return aiocoap.Message(payload=json.dumps({
            'message': 'changed'
        }).encode())

class TdResource(resource.Resource):
    """Thing description resource"""
    async def render_get(self, request):
        """Return the thing description on a GET request"""
        # pylint: disable=unused-argument
        return aiocoap.Message(payload=json.dumps(td_builder()).encode())

def main():
    """Main entry point. Sets up aiocoap server with resources"""
    root = resource.Site()
    root.add_resource(('.well-known', 'core'),
                      resource.WKCResource(root.get_resources_as_linkheader))
    root.add_resource(('state',), PropertyResource())
    root.add_resource(('td',), TdResource())

    asyncio.Task(aiocoap.Context.create_server_context(root))
    asyncio.get_event_loop().run_forever()

if __name__ == '__main__':
    main()
