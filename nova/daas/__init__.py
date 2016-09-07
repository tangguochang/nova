from nova import context as sys_context

from Crypto.Cipher import AES
import hashlib
import string
import os
from nova.i18n import _
from webob import exc
from nova import exception

from nova.db import base
import nova.context as syscontext
db_ins = base.Base()

def get_spice_connection_agent(func):
    def wrapped(self, context, instance, console_type):
        proxy_ip = None
        if console_type == "spice":
            for srv in context.to_dict()["service_catalog"]:
                if srv["type"] == "connection":
                    for edp in srv["endpoints"]:
                        proxy_ip = edp["publicURL"]
            connect_info = self.compute_rpcapi.get_spice_console(context,
                instance=instance, console_type=console_type)
            if not proxy_ip:
                return {'url': '%s:%s' % (connect_info['host'], connect_info['port'])}
            else:
                port = 40000
                base = 0
                compute_nodes = db_ins.db.compute_node_get_all(syscontext.get_admin_context())
                for n in compute_nodes:
                    if n['host_ip'] == connect_info['host']:
                        port = int(connect_info['port'])%5900 + port + base*200
                    base = base + 1
                return {'url': '%s:%s' % (proxy_ip, port)}
        else:
            return func(self, context, instance, console_type)
    return wrapped
