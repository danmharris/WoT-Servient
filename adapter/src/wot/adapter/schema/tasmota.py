PLUG = {
    '@context': 'https://iot.schema.org',
    'description': 'Tasmota Plug',
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
        },
        'power': {
            'title': 'Power',
            'description': 'Total power consumption',
            'readOnly': True,
            'type': 'integer',
            'forms': [{
                'op': 'readproperty',
                'href': '/properties/power',
                'htv:methodName': 'GET',
            }],
        },
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
