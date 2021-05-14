# Code
from django.urls import path
from .consumers import graphLevel, recomend, controlState, receiveButtonState, receiveMenuTimeline1, receiveMenuTimeline2


"""
Usualy you would conect functions from views
However because this is async we conect routing path to consumer file functions
Conect a router url to a object from file that calls "as_asgi()" method
"as_asgi()": Returns ASGI wrapped object application to send to the url so that user conection can see it
"""
ws_urlpatterns = [
    path("ws/graph/", graphLevel.as_asgi(), name="Websocket conection to update graph"),
    path("ws/recommend/", recomend.as_asgi(), name="Websocket conection to recommendation"),
    path("ws/controlState/", controlState.as_asgi(), name="Websocket conection to control sate"),
    path("ws/receiveButton/", receiveButtonState.as_asgi(), name="Websocket conection to receive ON/OFF states from buttons"),
    path("ws/receiveMenuTimeline1/", receiveMenuTimeline1.as_asgi(), name="Websocket conection to menu timeline for the level graph"),
    path("ws/receiveMenuTimeline2/", receiveMenuTimeline2.as_asgi(), name="Websocket conection to menu timeline for the price graph"),
]