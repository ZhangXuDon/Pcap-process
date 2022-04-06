import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib
matplotlib.use('Qt5Agg')

def process_file():
    csv_file = "non-Tor.csv"
    # largest_column_count = 0
    # with open(csv_file, 'r') as temp_f:
    #     lines = temp_f.readlines()
    #     for l in lines:
    #         column_count = len(l.split(',')) + 1
    #         largest_column_count = column_count if largest_column_count < column_count else largest_column_count
    # temp_f.close()
    # print(largest_column_count)
    column_names = [i for i in range(0, 1537)]
    data = pd.read_csv(csv_file, header=None, delimiter=',', names=column_names)
    # data.iloc[:, :].values.astype(int)
    data.to_csv("non-Tor_equal_length_flows.csv", sep=',', header=False, index=False, na_rep=0)
    print("data saved!")

def del_short_flow(data):
    dataset = []
    for i in range(len(data)):
        if is_short(data.iloc[i, :]):
            continue
        else:
            dataset.append(data.iloc[i, :])
    return np.array(dataset)

def is_short(flow):
    flow = np.array(flow)
    if pk_count(flow[1:]) < 10:
        return True
    return False

def pk_count(flow, n_feature=6):
    num_feature = n_feature
    flow_len = len(flow) // num_feature
    # print(flow_len)
    pk_num = 0
    for i in range(flow_len):
        if is_last(flow[num_feature * i: num_feature * (i+1)]):
            return pk_num
        else:
            pk_num += 1
    # if(pk_num > 256):
    #     return 256
    return pk_num

def is_last(package):
    flag = False
    #np.isnan(package[0]) or
    package = np.array(package)
    # print(package, package.sum())
    if package.sum() == 0:
        flag = True
    return flag

def change_timeStamp(data):
    dataset = []
    label = np.array(data.iloc[:, 0]).reshape([-1, 1])
    for i in range(len(data)):
        dataset.append(change_time(data.iloc[i, 1:]))
    dat = np.array(dataset)
    return np.hstack((dat, label))

# 根据timestamp删掉一些包
def change_time(flow):
    pk_size = 256
    num_feature = 6
    flow = np.array(flow)
    pk_size = [pk_size - n for n in range(1, 257)]
    for i in pk_size:
        if flow[i*num_feature] != 0 and i != 0:
            micro_second_now = flow[i * num_feature]
            micro_second_pre = flow[(i - 1) * num_feature]
            mic = micro_second_now - micro_second_pre
            # if mic >= 0:
            #     flow[i * num_feature] = (int)(mic)
            if mic < 0:
                # print(mic)
                # new_flow = flow[i*pk_size:]
                # print(mic)
                # flow[i*num_feature:] = np.zeros(flow[i*num_feature:].shape, dtype=int)
                # flow[i * num_feature:] = np.nan
                # print(flow.shape)
                mic = 0
            flow[i * num_feature] = (int)(mic)
            # print(flow[i*num_feature+1] - flow[(i-1)*num_feature+1])
        if i == 0:
            flow[i*num_feature] = 0
    return flow

def flow_more_than_250(dataset):
    # pre
    labels = [1, 4, 7, 9, 13]
    # class
    # labels = [3, 5, 10, 11, 14]
    data = []
    for i in range(len(dataset)):
        if dataset.iloc[i, -1] in labels:
            data.append(dataset.iloc[i, :])
    return np.array(data)

def statistic_flows(path):
    # 统计
    # 计算最大流的包数量
    # largest_column_count = 0
    # with open(path, 'r') as temp_f:
    #     lines = temp_f.readlines()
    #     for l in lines:
    #         column_count = len(l.split(',')) + 1
    #         largest_column_count = column_count if largest_column_count < column_count else largest_column_count
    # temp_f.close()
    # print(largest_column_count)

    # column_names = [i for i in range(0, 1537)]
    # data = pd.read_csv(path, header=None, delimiter=',', names=column_names).astype(int)
    data = pd.read_csv(path, header=None, names=None, sep=',')#.astype(int)
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
    apps_num = [[key, 0, 0] for key in app_names]
    for i in range(len(data)):
        apps_num[(int)(data.iloc[i, 0])][1] += 1
    col_labels = ("Label", "Application", "Number of flows")  #, "Number of packets"
    table_content = np.empty((len(app_names), 3), dtype='object')
    table_content[:, 0] = np.array([label for label in range(len(app_names))])
    table_content[:, 1] = np.array([app_names])[0]
    table_content[:, 2] = np.array([apps_num[key][1] for key in range(len(app_names))])
    # table_content[:, 2] = np.array([apps_num[key][2] for key in range(16)])
    plt.figure(figsize=(8, 6))
    ax = plt.gca()
    the_table = ax.table(cellText=table_content, colLabels=col_labels, loc='center')
    # ax.tick_params(bottom=False, top=False, left=False, right=False)
    # table_props = the_table.properties
    plt.xticks([])
    plt.yticks([])
    the_table.auto_set_font_size(False)
    the_table.set_fontsize(9)
    plt.show()

def statistic_flow_length(path):
    data = pd.read_csv(path, header=None, names=None, sep=',')
    flow_length = {key: 0 for key in range(1, 257)}
    for i in range(len(data)):
        flow_length[pk_count(data.iloc[i, 1:])] += 1
    plt.figure()
    plt.bar([i for i in range(1, 256)], [flow_length[i] for i in range(1, 256)])
    print(flow_length)
    plt.show()


if __name__ == '__main__':
    # 得到等长数据格式，再删去短流
    # process_file()
    # data = pd.read_csv("non-Tor_equal_length_flows.csv", header=None, names=None, sep=',')
    # data = del_short_flow(data)
    # print(data.shape)
    # pd.DataFrame(data).to_csv("dataset.csv", header=False, index=False, sep=',')
    #
    # # 重置timestamp并把label位置置后
    # dataset = pd.read_csv("dataset.csv", header=None, sep=',')
    # dataset = change_timeStamp(dataset)
    # pd.DataFrame(dataset).to_csv("dataset_final.csv", header=False, index=False, sep=',')

    # timestamp 有负值
    # 看哪些类别样本数满足条件
    # dataset = pd.read_csv("dataset_final.csv", header=None, sep=',')
    # dataset = flow_more_than_250(dataset)
    # pd.DataFrame(dataset).to_csv("non-Tor_pre.csv", header=False, index=False, sep=',')

    # dataset = pd.read_csv("../datasets/features/non-vpn/dataset_final.csv", header=None, sep=',')
    # statistic_flows("dataset_final.csv")
    statistic_flow_length("non-Tor_equal_length_flows.csv")
