HS100 = {
    '@context': 'https://iot.schema.org',
    'description': 'TP Link HS100 Smart Plug',
    'properties': {
        'state': {
            'title': 'State',
            'description': 'Whether the plug is on',
            'readOnly': False,
            'type': 'boolean',
            'forms': [
                {
                    'op': 'readproperty',
                    'href': '/properties/state',
                    'htv:methodName': 'GET',
                },
                {
                    'op': 'writeproperty',
                    'href': '/properties/state',
                    'htv:methodName': 'PUT',
                },
            ],
        }
    },
    'actions': {
        'toggle': {
            'title': 'Toggle',
            'description': 'Toggle the state of the plug',
            'forms': [{
                'op': 'invokeaction',
                'href': '/actions/toggle',
                'htv:methodName': 'POST',
            }],
        },
    },
}
