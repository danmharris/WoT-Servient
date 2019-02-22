import asyncio
import json

import aiocoap
import aiocoap.resource as resource

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

def main():
    root = resource.Site()
    root.add_resource(('.well-known', 'core'),
        resource.WKCResource(root.get_resources_as_linkheader))
    root.add_resource(('state',), PropertyResource())

    asyncio.Task(aiocoap.Context.create_server_context(root))
    asyncio.get_event_loop().run_forever()

if __name__ == '__main__':
    main()
