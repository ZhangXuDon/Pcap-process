import pickle
import os
import numpy as np
import matplotlib.pyplot as plt
import matplotlib

matplotlib.use('Qt5Agg')
# Set console width
desired_width = 320
np.set_printoptions(linewidth=desired_width)

p_files_path = "flows"

# Order is important because 'tor' is included in 'torrent' and tor filenames also include other app names
app_names = ['aim',
             'browsing',
             'email',
             'facebook',
             'ftp',
             'hangout',
             'icq',
             'p2p',
             'pop',
             'ssl',
             'spotify',
             'vimeo',
             'thunderbird',
             'youtube',
             'skype']

flows_by_app = {key: {} for key in app_names}
tuple_list = []
labels = []
i_file = 0

use_vpn = False

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


for dirpath, dirnames, filenames in os.walk(p_files_path):
    for filename in filenames:
        path = os.path.join(dirpath, filename)
        # print(filename)
        # Look at non-vpn and non-tor files
        if use_vpn or filename.find('vpn') == -1:
            found = 0
            app_name = ''
            # Organize by application
            for app in app_names:
                if filename.lower().find(app) != -1:
                    found += 1
                    app_name = app
                    break
            if found == 0:
                print("Could not find corresponding app")
            if found == 2:
                print("Found to corresponding apps")
            with open(path, 'rb') as file:
                flows = pickle.load(file)
                # print(flows)
                for tup_feat in flows:
                    # break
                    # Discard IP addresses
                    features = tup_feat[1]
                    flow = tup_feat[0]
                    flow_convert = convert(flow)
                    # print(flow, flow_convert)

                    if flow_convert not in flows_by_app[app_name]:
                        flows_by_app[app_name][flow_convert] = 0
                    flows_by_app[app_name][flow_convert] += 1

                    # 先创建一个五元组列表
                    # if flow not in tuple_list:
                    #     tuple_list.append(flow)
                i_file += 1

# Calculate the flow overlap between apps
n_overlapping_flows = np.zeros((len(app_names), len(app_names)), dtype='int')
n_ambiguous_packets = np.zeros((len(app_names), len(app_names)), dtype='int')
# Which flows in an app are also used in another app
overlapping_flows_by_app = {key: {} for key in app_names}

for i_app1, app1 in enumerate(app_names):
    for i_app2, app2 in enumerate(app_names):
        if i_app1 != i_app2:
            overlapping_flows = set(flows_by_app[app1].keys()) & set(flows_by_app[app2].keys())
            n_overlapping_flows[i_app1, i_app2] = len(overlapping_flows)

            for flow in overlapping_flows:
                overlapping_flows_by_app[app1][flow] = flows_by_app[app1][flow]

# Percentage of flows in an app also used in another app
unique_flows_by_app = {key: 0 for key in app_names}
# Percentage of packets recorded for an app that can be clearly associated with it
unambiguous_packets_by_app = {key: 0 for key in app_names}

n_flows_total   = 0
n_packets_total  = 0
n_unique_flows_total = 0
n_unambiguous_packets_total = 0

for app in app_names:
    print(app)
    # Calculate percentage of unique flows
    n_flows_this_app            = len(flows_by_app[app])
    n_non_unique_flows_this_app = len(overlapping_flows_by_app[app])
    n_unique_flows_this_app     = n_flows_this_app - n_non_unique_flows_this_app
    flow_overlap_this_app       = n_unique_flows_this_app / n_flows_this_app

    # Calculate percentage of unambiguous packets
    n_packets_this_app              = sum(list(flows_by_app[app].values()))
    n_ambiguous_packets_this_app    = sum(list(overlapping_flows_by_app[app].values()))
    n_unambiguous_packets_this_app  = n_packets_this_app - n_ambiguous_packets_this_app
    unambiguous_packets_this_app    = n_unambiguous_packets_this_app / n_packets_this_app

    unambiguous_packets_by_app[app] = unambiguous_packets_this_app
    unique_flows_by_app[app]        = flow_overlap_this_app

    n_flows_total += n_flows_this_app
    n_packets_total += n_packets_this_app
    n_unique_flows_total += n_unique_flows_this_app
    n_unambiguous_packets_total += n_unambiguous_packets_this_app

print("%f%% of all flows can be associated with a specific application" % (n_unique_flows_total / n_flows_total))
print("%f%% of all packets can be associated with a specific application" % (n_unambiguous_packets_total / n_packets_total))

name_mapping = {
        'AIM chat': 'aim',
        'Browsing': 'browsing',
        'Email':    'email',
        'Facebook': 'facebook',
        'FTPS':     'ftp',
        'Hangouts': 'hangout',
        'ICQ_chat':      'icq',
        'P2P':    'p2p',
        'POP':  'pop',
        'SSL': 'ssl',
        'Spotify': 'spotify',
        'Vimeo': 'vimeo',
        'Thunderbird': 'thunderbird',
        'Youtube': 'youtube',
        'Skype':    'skype',
}
col_labels = ("Label", "Application", "Number of flows", "Number of packets")  # , "Unique flows", "Unambiguous packets")
table_content = np.empty((len(app_names), 4), dtype='object')
table_content[:, 0]      = np.array([label for label in range(len(app_names))])
table_content[:, 1]      = np.array([list(name_mapping.keys())])[0]  # + ["Total/ Average"]
table_content[:, 2]    = np.array([len(flows_by_app[app]) for app in list(name_mapping.values())])
table_content[:, 3]    = np.array([sum(list(flows_by_app[app].values())) for app in list(name_mapping.values())])
# table_content[-1, 1]     = table_content[:-1, 1].sum()
# table_content[-1, 2]     = table_content[:-1, 2].sum()
# table_content[:-1, 3]    = np.array([unique_flows_by_app[app] for app in list(name_mapping.values())]).round(decimals=2)
# table_content[-1, 3]     = np.round(n_unique_flows_total / n_flows_total, decimals=2)
# table_content[:-1, 4]    = np.array([unambiguous_packets_by_app[app] for app in list(name_mapping.values())]).round(decimals=2)
# table_content[-1, 4]     = np.round(n_unambiguous_packets_total / n_packets_total, decimals=2)

# Use the following lines for a reduced view
# table_content = np.concatenate((np.expand_dims(table_content[:, 0],1), table_content[:, 3:]), axis=1)
# col_labels = ("Application", "Unique flows", "Unambiguous packets")

# fig = plt.figure()
plt.figure(figsize=(8, 6))
ax = plt.gca()
the_table = ax.table(cellText=table_content, colLabels=col_labels, loc='center')
table_props = the_table.properties
the_table.auto_set_font_size(False)

plt.xticks([])
plt.yticks([])
the_table.set_fontsize(9)
plt.show()
