import numpy as np
from scapy.all import *
import pickle
import os

pcap_path = "nonTor"
save_dir_path = "flows"

paths = []
filenames = []

pat = re.compile('[^\.]*\.')

def getTCP_flags(str):
    if(str == 'S'):
        return 1
    elif(str == 'A'):
        return 2
    elif (str == 'P'):
        return 4
    elif (str == 'C'):
        return 8
    elif (str == 'U'):
        return 16
    elif (str == 'E'):
        return 32
    elif (str == 'R'):
        return 64
    elif (str == 'F'):
        return 128

def convert(flow):
    if(flow[0] < flow[1]):
        return flow
    else:
        sip = flow[0]
        dip = flow[1]
        sport = flow[2]
        dport = flow[3]
        convert_flow = (dip, sip, dport, sport, flow[4])
        return convert_flow

for dirpath, dirnames, filenames in os.walk(pcap_path):
    n_files = len(filenames)
    i_file = 0

    for filename in sorted(filenames):

        i_file += 1

        path = os.path.join(dirpath, filename)

        actual_name = pat.match(filename)

        save_path = os.path.join(save_dir_path, filename[actual_name.span()[0]:actual_name.span()[1] - 1] + '_flows.p')

        if not os.path.isfile(save_path):
            print("Loading file %d/%d: %s" % (i_file, n_files, path))

            # flow_keys = set()
            flow_keys = []
            i_packet = 0
            flows = {}
            flow_feature = {}
            # flow = {}
            ## The following code is taking from the scapy sniff function
            sniff_sockets = {}
            sniff_sockets[PcapReader(path)] = path
            _main_socket = next(iter(sniff_sockets))
            read_allowed_exceptions = _main_socket.read_allowed_exceptions
            select_func = _main_socket.select
            if not all(select_func == sock.select for sock in sniff_sockets):
                warning("Warning: inconsistent socket types ! The used select function"
                        "will be the one of the first socket")
            _select = lambda sockets, remain: select_func(sockets, remain)[0]
            remain = None

            try:
                while sniff_sockets:
                    for s in list(_select(sniff_sockets, remain)):
                        try:
                            packet = s.recv()

                        except Exception as ex:
                            log_runtime.warning("Socket %s failed with '%s' and thus"
                                                " will be ignored" % (s, ex))
                            del sniff_sockets[s]
                            continue
                        except read_allowed_exceptions:
                            continue
                        if packet is None:
                            try:
                                if s.promisc:
                                    continue
                            except AttributeError:
                                pass
                            del sniff_sockets[s]
                            break

                        i_packet += 1
                        if (i_packet % 10000) == 0:
                            print("Loading packet %d" % i_packet)

                        sip = None
                        dip = None
                        sport = None
                        dport = None
                        prot = None

                        # timestamp
                        tim = (int)(packet.time*1000)
                        # packet size
                        l = len(packet)
                        # dir
                        dr = None
                        # ttl
                        ttl = None
                        # window size
                        win = None
                        # tcp flag
                        flag = None

                        if packet.haslayer(IP):
                            sip = packet[IP].src
                            dip = packet[IP].dst
                            ttl = packet[IP].ttl
                        if packet.haslayer(IPv6):
                            sip = packet[IPv6].src
                            dip = packet[IPv6].dst
                            ttl = packet[IPv6].hlim
                        if packet.haslayer(TCP):
                            # Skip if no payload
                            if getattr(packet[TCP], 'load', 0) == 0:
                                continue
                            sport = packet[TCP].sport
                            dport = packet[TCP].dport
                            prot = 'TCP'
                            win = packet[TCP].window
                            flag = getTCP_flags((str)(packet[TCP].flags)[0])
                        elif packet.haslayer(UDP):
                            if packet.haslayer(DNS):
                                pass
                                # dns_names.append(packet[4].qname.decode())
                            else:
                                sport = packet[UDP].sport
                                dport = packet[UDP].dport
                                prot = 'UDP'
                                win = 0
                                flag = 0
                        if(sip!=None and dip!=None):
                            if(sip > dip):
                                dr = 1
                            else:
                                dr = 0
                        else:
                            dr = None
                        if sip is None or dip is None or sport is None or dport is None or prot is None or ttl is None or l is None:
                            pass
                        else:
                            flow_key = (sip, dip, sport, dport, prot)
                            flow_key_convert = convert(flow_key)
                            flow_feature = (flow_key_convert, (tim, l, dr, ttl, win, flag))
                            flow_keys.append(flow_feature)
                            if not flow_key in flows:
                                flows[flow_key_convert] = 0
                            flows[flow_key_convert] += 1
            except KeyboardInterrupt:
                pass

            for s in sniff_sockets:
                s.close()

            print("Number of unique flows: %d" % len(flows))

            with open(save_path, 'wb') as file:
                pickle.dump(flow_keys, file)



