from proxy.app import create_app as create_proxy_app
from thing_directory.app import create_app as create_td_app
from binding.app import create_app as create_binding_app

def start_binding():
    app = create_binding_app()
    app.run(host='0.0.0.0', port=5000)

def start_proxy():
    app = create_proxy_app()
    app.run(host='0.0.0.0', port=5001)

def start_thing_directory():
    app = create_td_app()
    app.run(host='0.0.0.0', port=5002)
