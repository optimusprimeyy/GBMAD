# GBC-based method using Markov random walk for Anomaly Detection (GBMAD)
# Please refer to the following papers:
# Granular-Ball Computing-Based Markov Random Walk for Anomaly Detection.
# Uploaded by Sihan Wang on April. 15, 2024. E-mail:wangsihan0713@foxmail.com.
import gc
import os
import psutil
import numpy as np
from sklearn.preprocessing import MinMaxScaler
from GettingGranularBalls import GettingGranularBalls
import warnings
warnings.filterwarnings("ignore")


class GB:
    def __init__(self, data):
        self.data = data[:, :-1]  # Delete the indexed column
        self.center = self.data.mean(0)  # Get the center of the GB.
        self.xuhao = list(data[:, -1])  # Save the serial number of each sample in the GB
        self.score = 0  # Initialize the anomaly score for each GB to 0


# Wrap GB into a class and add it to the collection gb_dist
def add_center(gb_list):
    # input:
    # gb_list is the list of GBs, where each element represents the array of all the samples in the GB.
    gb_dist = {}
    for i in range(0, len(gb_list)):
        gb = GB(gb_list[i])
        gb_dist[i] = gb
    return gb_dist


def get_Dist(center1, center2, radius1, radius2):
    # input:
    # center1 and radius1 denote the center and radius of the first GB.
    # center2 and radius2 denote the center and radius of the second GB.
    dis_GB = np.linalg.norm(center1 - center2) + radius2 + radius1
    return dis_GB


def main():
    gc.collect()
    pid = os.getpid()
    p = psutil.Process(pid)
    info_start = p.memory_full_info().uss / 1024

    L = 8  # Set the minimum number of samples L in the grain ball
    d = 0.35  # Set the damping factor for Markov random walk.
    data_name = 'Iris'

    # 1. Call the GB generation function to get the label, data, granule list, radius list and center list, respectively
    label, data, gb_list, radius_list, center_list = GettingGranularBalls(data_name, L)

    gb_dist = add_center(gb_list)  # Assemble the resulting GBs list into sets

    # 2.1 Calculate the distance matrix based on GBs
    Dis = []
    for x in range(len(gb_dist)):
        dis_list = []
        for y in range(len(gb_dist)):
            if x == y:  # The distance between the GB and itself is zero.
                dis_list.append(0)
                continue
            dis = get_Dist(center_list[x], center_list[y], radius_list[x], radius_list[y])
            dis_list.append(dis)
        Dis.append(dis_list)
    Dis = np.asarray(Dis)

    # 2.2 Normalize the distance matrix.
    scaler = MinMaxScaler(feature_range=(0, 1))
    Dis = scaler.fit_transform(Dis)

    # 3.1 Calculate the state transfer matrix based on GBs.
    A = Dis
    diag_A = A.sum(axis=1)
    B = np.diag(diag_A)
    P = np.linalg.solve(B, A)

    # 3.2 Markov Random Walk
    phi_t = np.ones(len(gb_list)) / + len(gb_list)
    phi_t_temp = np.ones(len(gb_list))
    i = 0
    while np.linalg.norm(pi_t_temp - pi_t, 1) > 0.0001:
        pi_t_temp = pi_t
        pi_t = d + (1 - d) * pi_t @ P
        i += 1
    pi_t_w = pi_t

    # 4.1 Calculate Anomaly Degree AD of each GB.
    AD = pi_t_w
    for i in range(len(gb_dist)):
        gb_dist[i].score = AD[i]

    # 4.2 Assign an anomaly score to each sample in each GB.
    samples_scores = []
    for i in range(0, len(data)):
        for j in range(0, len(gb_dist)):
            if i in gb_dist[j].xuhao:  # If sample i is in the GB_j
                samples_scores.append(AD[j] * ((1 - len(gb_dist) / len(data)) ** (1 / 3)))

    # 5. Output the anomaly scores of samples
    print(samples_scores)

    info_end = p.memory_full_info().uss / 1024
    print("The program is consuming memory" + str(info_end - info_start) + "KB")


if __name__ == '__main__':
    main()
