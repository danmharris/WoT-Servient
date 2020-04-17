import click
import sys
import json
import asyncio
import jwt
from aiocoap import Context, Message
from aiocoap.numbers.codes import POST

def read_config(path='/etc/wot-network.ini'):
    """Reads and parses a configuration file

    Takes 1 argument
    path - Path to configuration file (defaults to /etc/wot-network.ini)
    """
    try:
        config = configparser.ConfigParser()
        config.read(path)
        return config
    except:
        print('No config file')
        sys.exit(1)

def read_bool(value):
    """Converts string to boolean"""
    return value == 'yes'

@click.group()
@click.option('--config', default='/etc/wot-network.ini', help='Path to config file')
@click.pass_context
def cli(ctx, config):
    """Main CLI utility"""
    ctx.ensure_object(dict)
    ctx.obj['CONFIG'] = config

@cli.command()
@click.argument('description')
@click.pass_context
def generate_api_token(ctx, description):
    """Generates a JWT for accessing services"""
    config = read_config(ctx.obj['CONFIG'])
    secret = config['DEFAULT']['secret']
    click.echo(jwt.encode({'description': description}, secret, algorithm='HS256').decode())

@cli.command()
@click.argument('psk')
@click.argument('identity')
@click.pass_context
def generate_ikea_psk(ctx, psk, identity):
    """Generates credentials to communicate with IKEA devices"""
    config = read_config(ctx.obj['CONFIG'])
    address = config['IKEA']['gateway']
    res = asyncio.get_event_loop().run_until_complete(_generate_psk(address, psk, identity))
    click.echo(res)

async def _generate_psk(address, psk, identity):
    c = await Context.create_client_context()
    uri = 'coaps://{}:5684/'.format(address)
    c.client_credentials.load_from_dict({
        uri+'*': {
            'dtls': {
                'psk': psk.encode(),
                'client-identity': b'Client_identity',
            }
        }
    })
    payload = '{{"9090":"{}"}}'.format(identity).encode()
    request = Message(code=POST, payload=payload, uri='coaps://{}:5684/15011/9063'.format(address))
    response = await c.request(request).response
    return json.loads(response.payload)['9091']
