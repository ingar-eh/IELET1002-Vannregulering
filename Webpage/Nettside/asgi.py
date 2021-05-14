"""
ASGI config for Nettside project.

It exposes the ASGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/3.2/howto/deployment/asgi/
"""

import os

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'Nettside.settings')


from channels.routing import get_default_application



# Import from channels a method that will check what type of conection is being sent
from channels.routing import ProtocolTypeRouter, URLRouter
from channels.auth import AuthMiddlewareStack

# Import websocket url list
from VMB_GUSTAV.routing import ws_urlpatterns

from django.core.asgi import get_asgi_application


"""
Variable is an insatnce of ProtocolTypeRouter
It passes the conection type that is checked in the ProtocolTypeRouter method 
Djnago checks the protocol type of the conection and delivers the right conection result
    - http: A protocol type conection that takes in POST/GET requests, handles them, and then stops
    - websocket:  A protocol type conection that can handle multiple signals back and forths betweene client and server, only stops when terminated (Good for real time data)
Inside the ProtocolTypeRouter method we have a dictionary that has:
    - http: check wich type of conection is being requested/sent
    - websocket: Hands the conection to AuthMiddlewareStack to identify user (we dont have users so it will be emtry)
                 Later hands the conection to the URLRouter that conects client/consumer to the websocket url that fits
"""
application = ProtocolTypeRouter({
    "http": get_asgi_application(),
    "websocket": AuthMiddlewareStack(URLRouter(ws_urlpatterns))
})

