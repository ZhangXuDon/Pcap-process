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
app_label_mapping = {
             'aim': 0,
             'browsing': 1,
             'email': 2,
             'facebook': 3,
             'ftp': 4,
             'hangout': 5,
             'icq': 6,
             'p2p': 7,
             'pop': 8,
             'ssl': 9,
             'spotify': 10,
             'vimeo': 11,
             'thunderbird': 12,
             'youtube': 13,
             'skype': 14}


flows_by_app = {key: {} for key in app_names}
i_file = 1

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

print("data processing...")
for dirpath, dirnames, filenames in os.walk(p_files_path):
    n_files = len(filenames)
    for filename in sorted(filenames):
        path = os.path.join(dirpath, filename)
        print("Loading file %d/%d: %s" % (i_file, n_files, path))
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
                continue
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
                    features = str(features).replace('(', ',').replace(')', '').replace(' ', '')
                    flow_convert = convert(flow)
                    if flow_convert not in flows_by_app[app_name]:
                        flows_by_app[app_name][flow_convert] = ''
                    flows_by_app[app_name][flow_convert] += features

                i_file += 1
            file.close()
            with open("csvfile/" + filename.replace(".p", ".csv"), mode='w', encoding='utf-8') as write_file:
                print(len(flows_by_app[app_name]))
                for _, value in flows_by_app[app_name].items():
                    write_file.write(str(app_label_mapping[app_name]) + value)
                    write_file.write('\n')
            write_file.close()
            flows_by_app = {key: {} for key in app_names}
print("data processed!")
# fname = 'extract_flows_test.csv'
# k = 0
# # with open("../datasets/features/features.txt", 'wb') as file:
# #     pickle.dump(flows_by_app, file)
# #     file.close()
# with open("" + fname, mode='w', encoding='utf-8') as write_file:
#     for app_label in range(len(flows_by_app)):
#         print(len(flows_by_app[app_names[app_label]]))
#         for _, value in flows_by_app[app_names[app_label]].items():
#             write_file.write(str(_)+str(app_label)+value)
#             write_file.write('\n')
#     write_file.close()
