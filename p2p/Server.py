import socketio
import time

sio = socketio.Server(cors_allowed_origins="*")
app = socketio.WSGIApp(sio)

nodes = {}

edges = {}

@sio.event
def connect(sid, environ):
    print(sid, 'connect')

@sio.event
def node_connect(sid, data):
    nodes[data["peer_id"]] = { "name": data["role"] }
    sio.emit('node_connect', data);
    print(f'sending data about node {data["peer_id"]}')

@sio.event
def edge_update(sid, data):
    peer_id = data["peer_id"]
    neighbor_set = set(data["neighbor_set"])
    for neighbor_id in neighbor_set:
        edge_id = f"{peer_id}_{neighbor_id}"
        edges[edge_id] = { "source": peer_id, "target": neighbor_id }
    print(f"sending edges of {peer_id}")
    sio.emit('edge_update', data)


@sio.event
def edge_traffic(sid, data):
    peer_id = data["peer_id"]
    neighbor_id = data["neighbor_id"]
    message_type = data["msg_type"]
    edge_id = f"{peer_id}_{neighbor_id}"
    print(f"{edge_id} {message_type}")
    sio.emit('edge_traffic', data)
    

@sio.event
def disconnect(sid):
    print(sid, 'disconnected')
