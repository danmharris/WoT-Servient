import asyncio
import json
import aiocoap
import aiocoap.resource as resource
from common.td_util import ThingDescriptionBuilder, ObjectBuilder, NumberBuilder

def td_builder():
    td = ThingDescriptionBuilder('urn:coap-thing', 'CoAP Thing')

    schema = ObjectBuilder()
    schema.add_number('state')

    td.add_property('state', 'coap://localhost/state', schema.build(), True)
    td.add_event('stateChange', 'coap://localhost/state', schema.build())

    return td.build()

class PropertyResource(resource.ObservableResource):
    def __init__(self):
        super().__init__()
        self.content = {
            'state': 0
        }

    async def render_get(self, request):
        return aiocoap.Message(payload=json.dumps(self.content).encode())

    async def render_put(self, request):
        payload = json.loads(request.payload)
        self.content = {
            'state': payload['state']
        }
        self.updated_state()
        return aiocoap.Message(payload=json.dumps({
            'message': 'changed'
        }).encode())

class TdResource(resource.Resource):
    async def render_get(self, request):
        return aiocoap.Message(payload=json.dumps(td_builder()).encode())

def main():
    root = resource.Site()
    root.add_resource(('.well-known', 'core'),
        resource.WKCResource(root.get_resources_as_linkheader))
    root.add_resource(('state',), PropertyResource())
    root.add_resource(('td',), TdResource())

    asyncio.Task(aiocoap.Context.create_server_context(root))
    asyncio.get_event_loop().run_forever()

if __name__ == '__main__':
    main()
