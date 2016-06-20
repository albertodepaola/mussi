from channels.routing import route
from collaborative_crm.consumers import *

channel_routing = [
    route('websocket.connect', updates_connect, path=r'^/updates/$'),
    route('websocket.disconnect', updates_disconnect, path=r'^/updates/$'),
    route('notify_user', notify_user),
    route('email_notification', email_notification),
    route('notify_company', notify_company),
]
