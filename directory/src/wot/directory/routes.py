from wot.directory.db import get_db
from wot.directory.services import DirectoryService

from flask import Blueprint, jsonify, request
from requests import HTTPError

bp = Blueprint('directory', __name__)

@bp.route('/things/', methods=['GET'])
def get_things():
    """ returns all things known to the system """
    return jsonify(DirectoryService(get_db()).get_things())

@bp.route('/sources/', methods=['POST'])
def new_sources():
    """
    Creates new sources. This takes the uri where descriptions can be found
    """

    failed = list()
    for source in request.get_json():
        try:
            DirectoryService(get_db()).new_source(source)
        except HTTPError:
            failed.append(source)

    if len(failed) > 0:
        return (jsonify({
            'status': 'warning',
            'message': 'not all created ({})'.format(','.join(failed)),
            }), 201, None)

    return (jsonify({'status': 'success'}), 201, None)

@bp.route('/sources/', methods=['GET'])
def get_sources():
    """
    Lists all sources and their URIs
    """
    return jsonify(DirectoryService(get_db()).get_sources())

@bp.route('/sources/sync', methods=['POST'])
def sync():
    """
    Force sync of all sources
    """
    updated = DirectoryService(get_db()).sync()

    return jsonify({
        'status': 'success',
        'message': '{} updated'.format(updated),
        })
