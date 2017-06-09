import json
import os
import threading

controller_ip="127.0.0.1"
rsu_list=['00:00:00:00:00:00:00:0b','00:00:00:00:00:00:00:0c',
'00:00:00:00:00:00:00:0d','00:00:00:00:00:00:00:0e','00:00:00:00:00:00:00:0f']

port_range=["2","3","4","5"]

         
link={'l1':["RSU1","RSU2"],
        'l2':["RSU2","RSU5"],
        'l3':["RSU5","RSU3"],
        'l4':["RSU3","RSU4"],
        'l5':["RSU4","RSU1"],
        'l6':["RSU1","RSU3"],
        'l7':["RSU4","RSU2"],
        'l8':["RSU1","RSU5"],
        'l9':["RSU4","RSU5"],
        'l10':["RSU2","RSU3"],
}

RSU_DPID = {'RSU1': '00:00:00:00:00:00:00:0b',
            'RSU2': '00:00:00:00:00:00:00:0c',
            'RSU3': '00:00:00:00:00:00:00:0d',
            'RSU4': '00:00:00:00:00:00:00:0e',
            'RSU5': '00:00:00:00:00:00:00:0f',
            }

RSU_DPID_reversed = {'00:00:00:00:00:00:00:0b': 'RSU1',
                     '00:00:00:00:00:00:00:0c': 'RSU2',
                     '00:00:00:00:00:00:00:0d': 'RSU3',
                     '00:00:00:00:00:00:00:0e': 'RSU4',
                     '00:00:00:00:00:00:00:0f': 'RSU5',
                     }


topology_list = [
    {
        "src-port": 5,
        "dst-port": 2,
        "direction": "bidirectional",
        "type": "internal",
        "dst-switch": "00:00:00:00:00:00:00:0f",
        "src-switch": "00:00:00:00:00:00:00:0b"
    },
    {
        "src-port": 5,
        "dst-port": 3,
        "direction": "bidirectional",
        "type": "internal",
        "dst-switch": "00:00:00:00:00:00:00:0f",
        "src-switch": "00:00:00:00:00:00:00:0c"
    },
    {
        "src-port": 4,
        "dst-port": 3,
        "direction": "bidirectional",
        "type": "internal",
        "dst-switch": "00:00:00:00:00:00:00:0e",
        "src-switch": "00:00:00:00:00:00:00:0c"
    },
    {
        "src-port": 4,
        "dst-port": 4,
        "direction": "bidirectional",
        "type": "internal",
        "dst-switch": "00:00:00:00:00:00:00:0e",
        "src-switch": "00:00:00:00:00:00:00:0d"
    },
    {
        "src-port": 2,
        "dst-port": 2,
        "direction": "bidirectional",
        "type": "internal",
        "dst-switch": "00:00:00:00:00:00:00:0c",
        "src-switch": "00:00:00:00:00:00:00:0b"
    },
    {
        "src-port": 3,
        "dst-port": 3,
        "direction": "bidirectional",
        "type": "internal",
        "dst-switch": "00:00:00:00:00:00:00:0d",
        "src-switch": "00:00:00:00:00:00:00:0c"
    },
    {
        "src-port": 5,
        "dst-port": 4,
        "direction": "bidirectional",
        "type": "internal",
        "dst-switch": "00:00:00:00:00:00:00:0f",
        "src-switch": "00:00:00:00:00:00:00:0d"
    },
    {
        "src-port": 5,
        "dst-port": 5,
        "direction": "bidirectional",
        "type": "internal",
        "dst-switch": "00:00:00:00:00:00:00:0f",
        "src-switch": "00:00:00:00:00:00:00:0e"
    },
    {
        "src-port": 4,
        "dst-port": 2,
        "direction": "bidirectional",
        "type": "internal",
        "dst-switch": "00:00:00:00:00:00:00:0e",
        "src-switch": "00:00:00:00:00:00:00:0b"
    },
    {
        "src-port": 3,
        "dst-port": 2,
        "direction": "bidirectional",
        "type": "internal",
        "dst-switch": "00:00:00:00:00:00:00:0d",
        "src-switch": "00:00:00:00:00:00:00:0b"
    }
]



port_trans_dict={}
port_recv_dict={}
rsu_port_dict={}
link_bw={}
old_link_traffic={'l1':'0',
        'l2':'0',
        'l3':'0',
        'l4':'0',
        'l5':'0',
        'l6':'0',
        'l7':'0',
        'l8':'0',
        'l9':'0',
        'l10':'0',
}
new_link_traffic={'l1':'0',
        'l2':'0',
        'l3':'0',
        'l4':'0',
        'l5':'0',
        'l6':'0',
        'l7':'0',
        'l8':'0',
        'l9':'0',
        'l10':'0',
}

link_latency={'l1':'1',
        'l2':'1',
        'l3':'1',
        'l4':'1',
        'l5':'1',
        'l6':'1',
        'l7':'1',
        'l8':'1',
        'l9':'1',
        'l10':'1',
}

def get_current_traffic():
    old_link_traffic=new_link_traffic.copy()
    cmd = "curl --silent http://%s:8080/wm/core/switch/all/port/json" % (controller_ip)
    curl_output_bw = os.popen(cmd).read()
    json_bw = json.loads(curl_output_bw)
    cmd = "curl --silent http://%s:8080/wm/topology/links/json " % (controller_ip)
    curl_output_latency = os.popen(cmd).read()
    topology_list = json.loads(curl_output_latency)


    for rsu in json_bw.keys():
        if rsu in rsu_list:
            for port in json_bw[rsu]["port_reply"][0]["port"]:
                if port["port_number"] in port_range:
                    port_trans_dict[port["port_number"]]=port["transmit_bytes"]
            rsu_port_dict[rsu]=port_trans_dict


    ap1_in_port = ''
    ap1_out_port = ''
    ap2_in_port = ''
    ap2_out_port = ''

    for l in link:
        ap1_DPID=RSU_DPID[link[l][0]]
        ap2_DPID=RSU_DPID[link[l][1]]
        found=0
        for neighbor in topology_list:
            if ap1_DPID == neighbor['src-switch'] and ap2_DPID == neighbor['dst-switch']:
                ap1_out_port = neighbor['src-port']
                ap2_in_port = neighbor['dst-port']
                latency=neighbor['latency']
                found=1
                
            elif ap1_DPID == neighbor['dst-switch'] and ap2_DPID == neighbor['src-switch']:
                ap1_out_port = neighbor['dst-port']
                ap2_in_port = neighbor['src-port']
                latency=neighbor['latency']
                found=1

            if found==1:
                transmission=((rsu_port_dict[ap1_DPID])[str(ap2_in_port)])
                new_link_traffic[l]=transmission
                link_latency[l]=int(latency)
                break
    for link_id in new_link_traffic.keys():
        if not float(new_link_traffic[link_id])==float(old_link_traffic[link_id]):
            link_bw[link_id]=((float(new_link_traffic[link_id])-float(old_link_traffic[link_id]))/10)
    with open('/home/lubuntu/Workspace/bandwidth.json', 'w') as bw:
        json.dump(link_bw, bw)
    with open('/home/lubuntu/Workspace/latency.json', 'w') as lat:
        json.dump(link_latency, lat)
    threading.Timer(10, get_current_traffic).start()


get_current_traffic()


