"""
 Test ICP localisation
 Apply a random displacement to a scan and check the error of the recovered position through ICP
 author: David Filliat
"""

import numpy as np
import matplotlib.pyplot as plt
import math
import time

import readDatasets as datasets
import icp

def test(dist_thres, percent):
    # Reading some data
    scanList = datasets.read_u2is(56)
    scanOriginal = scanList[55]
    scanTruePose = np.array([0.3620, 0.0143, 0.0483])  # Manual estimation for scan 55 of u2is dataset

    # Initialise error log
    nb_test = 10
    poseError = np.zeros((3, nb_test))

    time_start = time.process_time()
    for a in range(nb_test):

        idref = np.random.randint(50)
        refscan = scanList[idref]
        # Generate random displacement and applies it to the second scan
        randT = np.random.rand(2, 1) - 0.5
        randR = 0.6*np.random.rand(1, 1) - 0.3
        R = np.array([[math.cos(randR), -math.sin(randR)], [math.sin(randR), math.cos(randR)]])
        scan = datasets.transform_scan(scanOriginal, R, randT)

        # # Displays initial positions
        plt.cla()
        # for stopping simulation with the esc key.
        plt.gcf().canvas.mpl_connect('key_release_event', lambda event: [exit(0) if event.key == 'escape' else None])
        plt.plot(refscan["x"], refscan["y"], "ob", label='Ref Scan')
        plt.plot(scan["x"], scan["y"], ".r", label='Scan before ICP')
        plt.axis("equal")

        # perform ICP
        R, t, error = icp.icp(refscan, scan, 200, 1e-7, dist_thres, percent)

        # Apply motion to scan
        scan = datasets.transform_scan(scan, R, t)
        poseError[:, a] = np.transpose(scan["pose"] - scanTruePose)

        # # Display
        plt.axis("equal")
        plt.plot(scan["x"], scan["y"], ".g", label='Scan after ICP')
        plt.legend()
        plt.pause(0.1)


    time_elapsed = time.process_time() - time_start
    tErrors = np.sqrt(np.square(poseError[0, :]) + np.square(poseError[1, :]))
    oErrors = np.sqrt(np.square(poseError[2, :]))
    print("Mean (var) translation error : {:e} ({:e})".format(np.mean(tErrors), np.var(tErrors)))
    print("Mean (var) rotation error : {:e} ({:e})".format(np.mean(oErrors), np.var(oErrors)))
    print("Mean computation time : {:f}".format(time_elapsed/nb_test))
    print("Press Q in figure to finish...")
    plt.show()
    return np.mean(tErrors),np.var(tErrors),np.mean(oErrors),np.var(oErrors),time_elapsed/nb_test


if __name__=="__main__":
    # dist_thres_list=[0.02*i for i in range(20)]
    # # percent_list=[0.05*i for i in range(3,20)]
    # te_list=[]
    # vt_list=[]
    # oe_list=[]
    # vo_list=[]
    # time_list=[]
    # for t in dist_thres_list:
    #     te,vt,oe,vo,ti=test(t,0.85)
    #     te_list.append(te)
    #     vt_list.append(vt)
    #     oe_list.append(oe)
    #     vo_list.append(vo)
    #     time_list.append(ti)
    #
    # plt.figure()
    # plt.errorbar(dist_thres_list,te_list,yerr=vt_list,elinewidth=2,fmt="-ro",label="translation error")
    # plt.errorbar(dist_thres_list,oe_list,yerr=vo_list,elinewidth=2,fmt="-bo",label="rotation error")
    # plt.plot(dist_thres_list, time_list, "-yo", label="time")
    # plt.title("Performance with different thresholds")
    # plt.xlabel("threshold")
    # plt.ylabel("value")
    # plt.legend()
    # plt.show()
    test(0.3,0.85)