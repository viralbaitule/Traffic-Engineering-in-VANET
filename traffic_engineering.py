#!/usr/bin/python3
import json
import os
import sys
import time
import random
start = time.time()


RSU_DPID = {'RSU1': '00:00:00:00:00:00:00:0b',
            'RSU2': '00:00:00:00:00:00:00:0c',
            'RSU3': '00:00:00:00:00:00:00:0d',
            'RSU4': '00:00:00:00:00:00:00:0e',
            'RSU5': '00:00:00:00:00:00:00:0f',
            }

car_ip={"192.168.0.1":"car1",
        "192.168.0.2":"car2",
        "192.168.0.3":"car3",
        "192.168.0.4":"car4",
}

RSU_DPID_reversed = {'00:00:00:00:00:00:00:0b': 'RSU1',
                     '00:00:00:00:00:00:00:0c': 'RSU2',
                     '00:00:00:00:00:00:00:0d': 'RSU3',
                     '00:00:00:00:00:00:00:0e': 'RSU4',
                     '00:00:00:00:00:00:00:0f': 'RSU5',
                     }

graph = {'RSU1': set(['RSU2', 'RSU3', 'RSU4', 'RSU5']),
         'RSU2': set(['RSU1', 'RSU3', 'RSU4', 'RSU5']),
         'RSU3': set(['RSU1', 'RSU2', 'RSU4', 'RSU5']),
         'RSU4': set(['RSU1', 'RSU2', 'RSU3', 'RSU5']),
         'RSU5': set(['RSU1', 'RSU2', 'RSU3', 'RSU4']),
         }

link = {'l1': ["RSU1", "RSU2"],
        'l2': ["RSU2", "RSU5"],
        'l3': ["RSU5", "RSU3"],
        'l4': ["RSU3", "RSU4"],
        'l5': ["RSU4", "RSU1"],
        'l6': ["RSU1", "RSU3"],
        'l7': ["RSU4", "RSU2"],
        'l8': ["RSU1", "RSU5"],
        'l9': ["RSU4", "RSU5"],
        'l10': ["RSU2", "RSU3"],
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



link_max_bandwidth={'l1':30.0,
        'l2':30.0,
        'l3':30.0,
        'l4':600.0,
        'l5':30.0,
        'l6':30.0,
        'l7':30.0,
        'l8':30.0,
        'l9':600.0,
        'l10':30.0,
}
link_min_lat={'l1':25.0,
        'l2':10.0,
        'l3':10.0,
        'l4':5.0,
        'l5':25.0,
        'l6':25.0,
        'l7':25.0,
        'l8':25.0,
        'l9':25.0,
        'l10':5.0,
}

path_hop_dict={}
normalized_bw_dict={}
normalized_latency_dict={}
normalized_bdp_dict={}
path_cost_dict={}
controller_ip = '127.0.0.1'

def normalization(old_max,old_min,value):
    new_max=100.0
    new_min=0
    return ((((new_max-new_min)/(old_max-old_min))*(value-old_max))+new_max)


def dfs_paths(graph, start, goal):
    stack = [(start, [start])]
    while stack:
        (vertex, path) = stack.pop()
        for next in graph[vertex] - set(path):
            if next == goal:
                yield path + [next]
            else:
                stack.append((next, path + [next]))

def get_best_path(dfs_path_links, dfs_path_RSU):
    # algorith and equation
    # get bandwidth, latency ,rssi, hop count and puting them in dictonary having key as link and path
    with open('/home/lubuntu/Workspace/bandwidth.json') as bw:    
        link_bandwidth_dict = json.load(bw)
    with open('/home/lubuntu/Workspace/latency.json') as lat:    
        link_latency_dict = json.load(lat)
    with open('/home/lubuntu/Workspace/rssi.json') as rssi:
        car_rssi_dict = json.load(rssi)
    normalized_rssi=normalization(-7,-3,round((float(car_rssi_dict[car_ip[str(src_ip)]])/10),0))
    for path in dfs_path_RSU.keys():
        path_hop_dict[path]=len(dfs_path_RSU[path])
    for link in link_bandwidth_dict.keys():
        new_max_bw=link_max_bandwidth[link]
        new_min_bw=0
        new_max_lat=float(max(link_latency_dict.values()))
        new_min_lat=link_min_lat[link]
        normalized_bw=normalization(new_max_bw,new_min_bw,(link_bandwidth_dict[link]/1000))
        normalized_bw_dict[link]=normalized_bw
        normalized_lat=normalization(new_max_lat,new_min_lat,float(link_latency_dict[link]))
        normalized_latency_dict[link]=normalized_lat
        bdp=normalized_bw*normalized_lat
        normalized_bdp=normalization(10000.0,0.0,bdp)
        normalized_bdp_dict[link]=normalized_bdp
    for path in dfs_path_links:
        weight=3
        normalized_hop_count=normalization(5,2,path_hop_dict[path])
        path_bdp=0
        for link in dfs_path_links[path]:
            path_bdp=path_bdp+normalized_bdp_dict[link]
        path_cost=(weight*normalized_hop_count)+path_bdp+normalized_rssi
        normalized_path_cost=normalization(500.0,0,path_cost)
        path_cost_dict[path]=normalized_path_cost
    p_dst=random.choice(path_dest)
    path_cost_dict[path_src],path_cost_dict[p_dst]=path_cost_dict[p_dst],path_cost_dict[path_src]
    data_graph = open("/home/lubuntu/Workspace/data_for_graph.txt", "wb+")
    data_graph.close()
    data_graph = open("/home/lubuntu/Workspace/data_for_graph.txt", "ab+")
    inp = "Source IP: %s \t" % (src_ip)
    data_graph.write(inp)
    inp = "Destination IP: %s \n" % (dst_ip)
    data_graph.write(inp)
    inp = "Source DPID: %s \t" % (src_DPID)
    data_graph.write(inp)
    inp = "Destination DPID: %s \n" % (dst_DPID)
    data_graph.write(inp)
    data_graph.write("Normalized BW:\n")
    data_graph.write(str(normalized_bw_dict))
    data_graph.write("\n")
    data_graph.write("Normalized: Latency:\n")
    data_graph.write(str(normalized_latency_dict))
    data_graph.write("\n")
    data_graph.write("Normalized Path Cost:\n")
    data_graph.write(str(path_cost_dict))
    data_graph.write("\n")
    data_graph.write("Paths :\n")
    data_graph.write(str(dfs_path_RSU))
    data_graph.write("\n")
    data_graph.write("\n")
    inp = "Best Path: %s \n" % (min(path_cost_dict, key=path_cost_dict.get))
    data_graph.write(inp)
    data_graph.close()
    best_path=min(path_cost_dict, key=path_cost_dict.get)
    return best_path


def path_list_generation(src, dest):
    path_list = list(dfs_paths(graph, src, dest))
    j = 1
    dfs_path_links = {}
    dfs_path_RSU = {}

    for path in path_list:
        var = 'p' + str(j)
        link_list = []
        dfs_path_RSU[var] = path

        # Path with Links
        for i in range(len(path) - 1):
            for k, v in link.items():
                if path[i] in v and path[i + 1] in v:
                    link_list.append(k)

        dfs_path_links[var] = link_list
        j += 1

    for k, v in dfs_path_links.items():
        print (k, ':', v)

    for k, v in dfs_path_RSU.items():
        print (k, ':', v)  
    bestpath=get_best_path(dfs_path_links,dfs_path_RSU)
    return bestpath, dfs_path_RSU, dfs_path_links



def get_ap_data_list(ap1_DPID, ap2_DPID):
    ap_data_list = []
    ap1_in_port = ''
    ap1_out_port = ''
    ap2_in_port = ''
    ap2_out_port = ''

    for neighbor in topology_list:
        if ap1_DPID == neighbor['src-switch'] and ap2_DPID == neighbor['dst-switch']:
            ap1_out_port = neighbor['src-port']
            ap2_in_port = neighbor['dst-port']
        elif ap1_DPID == neighbor['dst-switch'] and ap2_DPID == neighbor['src-switch']:
            ap1_out_port = neighbor['dst-port']
            ap2_in_port = neighbor['src-port']

    if ap1_DPID == src_DPID:
        ap1_in_port = src_in_port
    if ap2_DPID == dst_DPID:
        ap2_out_port = dst_in_port

    ap_data_list = [{'ap_DPID': ap1_DPID, 'ap_in_port': ap1_in_port, 'ap_out_port': ap1_out_port}, {'ap_DPID': ap2_DPID, 'ap_in_port': ap2_in_port, 'ap_out_port': ap2_out_port}]
    return ap_data_list


def get_pairs(best_path):
    for i in range(len(best_path) - 1):
        ap1_DPID = RSU_DPID[best_path[i]]
        ap2_DPID = RSU_DPID[best_path[i + 1]]
        ap_data_list = get_ap_data_list(ap1_DPID, ap2_DPID)
        flow_rule_pusher(ap_data_list, src_ip, dst_ip)


def flow_rule_pusher(ap_data_list, src_ip, dst_ip):
    # create new flow rules
    cmd_ap1_f1 = ''
    cmd_ap1_f2 = ''
    cmd_ap1_r1 = ''
    cmd_ap1_r2 = ''
    cmd_ap2_f1 = ''
    cmd_ap2_f2 = ''
    cmd_ap2_r1 = ''
    cmd_ap2_r2 = ''
    fo = open("/home/lubuntu/Workspace/rules.txt", "ab+")
    cmd_ap1_f1 = "curl -s -d '{\"switch\": \"%s\", \"name\":\"%s\", \"ipv4_src\":\"%s\", \"ipv4_dst\":\"%s\", \
\"eth_type\":\"%s\", \"cookie\":\"0\",\"idle_timeout\":\"5\", \"priority\":\"1000\",\"active\":\"true\", \"actions\":\"output=%s\"}' \
http://%s:8080/wm/staticflowpusher/json" % (ap_data_list[0]['ap_DPID'], ap_data_list[0]['ap_DPID'] + '_' + src_ip + "_" + dst_ip + ".f", src_ip, dst_ip, "0x800", ap_data_list[0]['ap_out_port'], controller_ip)
    curl_output = os.popen(cmd_ap1_f1).read()
    fo.write(cmd_ap1_f1)
    fo.write("\n")
    cmd_ap1_f2 = "curl -s -d '{\"switch\": \"%s\", \"name\":\"%s\", \"arp_spa\":\"%s\", \"arp_tpa\":\"%s\", \
\"eth_type\":\"%s\", \"cookie\":\"0\",\"idle_timeout\":\"5\", \"priority\":\"1000\",\"active\":\"true\", \"actions\":\"output=%s\"}' \
http://%s:8080/wm/staticflowpusher/json" % (ap_data_list[0]['ap_DPID'], ap_data_list[0]['ap_DPID'] + '_' + src_ip + "_" + dst_ip + ".farp", src_ip, dst_ip, "0x806", ap_data_list[0]['ap_out_port'], controller_ip)
    curl_output = os.popen(cmd_ap1_f2).read()
    fo.write(cmd_ap1_f2)
    fo.write("\n")
    if ap_data_list[0]['ap_DPID'] == src_DPID:
        cmd_ap1_r1 = "curl -s -d '{\"switch\": \"%s\", \"name\":\"%s\", \"ipv4_src\":\"%s\", \"ipv4_dst\":\"%s\", \
\"eth_type\":\"%s\", \"cookie\":\"0\",\"idle_timeout\":\"5\", \"priority\":\"1000\",\"active\":\"true\", \"actions\":\"output=%s\"}' \
http://%s:8080/wm/staticflowpusher/json" % (ap_data_list[0]['ap_DPID'], ap_data_list[0]['ap_DPID'] + '_' + dst_ip + "_" + src_ip + ".r", dst_ip, src_ip, "0x800", ap_data_list[0]['ap_in_port'], controller_ip)
        curl_output = os.popen(cmd_ap1_r1).read()
        fo.write(cmd_ap1_r1)
        fo.write("\n")
        cmd_ap1_r2 = "curl -s -d '{\"switch\": \"%s\", \"name\":\"%s\", \"arp_spa\":\"%s\", \"arp_tpa\":\"%s\", \
\"eth_type\":\"%s\", \"cookie\":\"0\",\"idle_timeout\":\"5\", \"priority\":\"1000\",\"active\":\"true\", \"actions\":\"output=%s\"}' \
http://%s:8080/wm/staticflowpusher/json" % (ap_data_list[0]['ap_DPID'], ap_data_list[0]['ap_DPID'] + '_' + dst_ip + "_" + src_ip + ".rarp", dst_ip, src_ip, "0x806", ap_data_list[0]['ap_in_port'], controller_ip)
        curl_output = os.popen(cmd_ap1_r2).read()
        fo.write(cmd_ap1_r2)
        fo.write("\n")
    cmd_ap2_r1 = "curl -s -d '{\"switch\": \"%s\", \"name\":\"%s\", \"ipv4_src\":\"%s\", \"ipv4_dst\":\"%s\", \
\"eth_type\":\"%s\", \"cookie\":\"0\",\"idle_timeout\":\"5\", \"priority\":\"1000\",\"active\":\"true\", \"actions\":\"output=%s\"}' \
http://%s:8080/wm/staticflowpusher/json" % (ap_data_list[1]['ap_DPID'], ap_data_list[1]['ap_DPID'] + '_' + dst_ip + "_" + src_ip + ".r", dst_ip, src_ip, "0x800", ap_data_list[1]['ap_in_port'], controller_ip)
    curl_output = os.popen(cmd_ap2_r1).read()
    fo.write(cmd_ap2_r1)
    fo.write("\n")
    cmd_ap2_r2 = "curl -s -d '{\"switch\": \"%s\", \"name\":\"%s\", \"arp_spa\":\"%s\", \"arp_tpa\":\"%s\", \
\"eth_type\":\"%s\", \"cookie\":\"0\",\"idle_timeout\":\"5\", \"priority\":\"1000\",\"active\":\"true\", \"actions\":\"output=%s\"}' \
http://%s:8080/wm/staticflowpusher/json" % (ap_data_list[1]['ap_DPID'], ap_data_list[1]['ap_DPID'] + '_' + dst_ip + "_" + src_ip + ".rarp", dst_ip, src_ip, "0x806", ap_data_list[1]['ap_in_port'], controller_ip)
    curl_output = os.popen(cmd_ap2_r2).read()
    fo.write(cmd_ap2_r2)
    fo.write("\n")
    if ap_data_list[1]['ap_DPID'] == dst_DPID:
        cmd_ap2_f1 = "curl -s -d '{\"switch\": \"%s\", \"name\":\"%s\", \"ipv4_src\":\"%s\", \"ipv4_dst\":\"%s\", \
\"eth_type\":\"%s\", \"cookie\":\"0\",\"idle_timeout\":\"5\", \"priority\":\"1000\",\"active\":\"true\", \"actions\":\"output=%s\"}' \
http://%s:8080/wm/staticflowpusher/json" % (ap_data_list[1]['ap_DPID'], ap_data_list[1]['ap_DPID'] + '_' + src_ip + "_" + dst_ip + ".f", src_ip, dst_ip, "0x800", ap_data_list[1]['ap_out_port'], controller_ip)
        curl_output = os.popen(cmd_ap2_f1).read()
        fo.write(cmd_ap2_f1)
        fo.write("\n")
        cmd_ap2_f2 = "curl -s -d '{\"switch\": \"%s\", \"name\":\"%s\", \"arp_spa\":\"%s\", \"arp_tpa\":\"%s\", \
\"eth_type\":\"%s\", \"cookie\":\"0\",\"idle_timeout\":\"5\", \"priority\":\"1000\",\"active\":\"true\", \"actions\":\"output=%s\"}' \
http://%s:8080/wm/staticflowpusher/json" % (ap_data_list[1]['ap_DPID'], ap_data_list[1]['ap_DPID'] + '_' + src_ip + "_" + dst_ip + ".farp", src_ip, dst_ip, "0x806", ap_data_list[1]['ap_out_port'], controller_ip)
        curl_output = os.popen(cmd_ap2_f2).read()
        fo.write(cmd_ap2_f2)
        fo.write("\n")
    fo.close()


def get_connected_RSU(src_ip, dst_ip):
    global src_DPID
    src_DPID = ''
    global src_in_port
    src_in_port = ''
    global dst_DPID
    dst_DPID = ''
    global dst_in_port
    dst_in_port = ''
    cmd = 'curl -s http://localhost:8080/wm/device/?ipv4=%s' % src_ip
    curl_output = os.popen(cmd).read()
    json_parsed = json.loads(curl_output)
    try:
        src_DPID = json_parsed['devices'][0]['attachmentPoint'][0]['switch']
        src_in_port = json_parsed['devices'][0]['attachmentPoint'][0]['port']
    except IndexError:
        print("Car %s not yet known to RSU's, ping and try again" % src_ip)
        sys.exit()

    cmd = 'curl -s http://localhost:8080/wm/device/?ipv4=%s' % dst_ip
    curl_output = os.popen(cmd).read()
    json_parsed = json.loads(curl_output)
    try:
        dst_DPID = json_parsed['devices'][0]['attachmentPoint'][0]['switch']
        dst_in_port = json_parsed['devices'][0]['attachmentPoint'][0]['port']
    except IndexError:
        print("Car %s not yet known to RSU's, ping and try again" % dst_ip)
        sys.exit()
    return src_DPID, src_in_port, dst_DPID, dst_in_port


def main():
    global src_ip
    global dst_ip
    global fo
    global topology_list
    topology_list=[]
    fo = open("/home/lubuntu/Workspace/rules.txt", "wb+")
    cmd = "curl --silent http://%s:8080/wm/topology/links/json " % (controller_ip)
    curl_output = os.popen(cmd).read()
    topology_list = json.loads(curl_output)
    src_ip = sys.argv[1]
    dst_ip = sys.argv[2]
    inp = "Source IP and b: %s \t" % (src_ip)
    fo.write(inp)
    inp = "Destination IP: %s \n" % (dst_ip)
    fo.write(inp)
    fo.close()
    src_DPID, src_in_port, dst_DPID, dst_in_port = get_connected_RSU(src_ip, dst_ip)
    src_RSU = RSU_DPID_reversed[src_DPID]
    dst_RSU = RSU_DPID_reversed[dst_DPID]
    bestpath, dfs_path_RSU, dfs_path_links = path_list_generation(src_RSU, dst_RSU)
    get_pairs(dfs_path_RSU[bestpath])


if __name__ == "__main__":
    main()
    end = time.time()
    print(end - start)
# main()
# will be triggered wheneven there is new srcip and dstip
# 1. get_connected_RSU() --> this will return soruce and destination rsu dipd and in ports
# 2. path_list_generation()--> this will generated the possible paths between source dpid and dest dpid
# and also calls
#   2.1. get_best_path() --> this will return best path key i.e example p1 or p2
# 3. value of best path i.e example ['RSU1', 'RSU3', 'RSU2', 'RSU5'] will be pass to get_pairs()
#   3.1 from which flow_rule_pusher() is called to push flow rules on the pair of devices
