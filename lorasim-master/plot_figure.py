import numpy as np
import matplotlib.pyplot as plt
from scipy.interpolate import spline
from pylab import mpl

mpl.rcParams['font.sans-serif'] = ['FangSong'] # 指定默认字体
mpl.rcParams['axes.unicode_minus'] = False # 解决保存图像是负号'-'显示为方块的问题


'''
command:
                nrNodes:     0
        Collision Ratio:     1
             Throughput:     4
                    DER:     6
      Experiment Number:     7
           SendDuration:     8
'''
# 重复实验的结果 关于节点数目
def get_cdf_from_file(nrNodes,exper_number, command,sendDuration, fname):
    ans = []
    tmp = []
    with open(fname, 'r') as myfile:
        for line in myfile:
            tmp = line.split()
            if len(tmp) == 9:
                if nrNodes == int(tmp[0]):
                    if sendDuration == int(tmp[8]):
                        if exper_number == int(tmp[7]):
                            ans.append(float(tmp[command]))
    myfile.close()
    return np.array(ans)


def plot_cdf(exper_number, command, fname):
    data = get_cdf_from_file(500, exper_number, command, 300000, fname)
    p = 1. * np.arange(len(data)) / (len(data) - 1)
    data_sorted = np.sort(data)
    # plot the sorted data:
    plt.plot(data_sorted, p)
    plt.show()

'''
command:
                nrNodes:     0
        Collision Ratio:     1
             Throughput:     4
                    DER:     6
      Experiment Number:     7
           SendDuration:     8
'''
def get_nodes_data_from_file(exper_number, command, fname):
    ans = []
    std = []
    nrNodesList = [50,100,200,300,400,500,600,700,800,900,1100,1300,1500,1700,1800,2000]
    for i in range(0,len(nrNodesList)):
         tmp = get_cdf_from_file(nrNodesList[i],exper_number, command, 300000,fname)
         avg_tmp = tmp.mean(0)
         std_tmp = tmp.std(0)
         ans.append(avg_tmp)
         std.append(std_tmp)
    return ans,std,nrNodesList


# plot fig with different comnmands(avg value)：DER, Throughput
def plot_avg_nodes(command,fname):
    experiment_number = [0,2,5,6]
    colors =['black','blue','gray','red']
    labels=['static SF = 12','static SF = 7','ADR','DBS']
    linewidth = 2
    # linestyle = ['--','-.','--','o-']
    ncolors = len(plt.rcParams['axes.prop_cycle'])
    fig, ax = plt.subplots()
    for j in range(0,4):
        ans, std, nrNodesList = get_nodes_data_from_file(experiment_number[j],command, fname)
        for i in range(0,len(nrNodesList)):
            ax.errorbar(nrNodesList, ans, std, label=labels[j],color =colors[j],linewidth=linewidth)
    plt.show()


# get duration file
def get_duration_data_from_file(exper_number, command):
    ans = []
    std = []
    fname = "data/exptimeDuration"
    duration = [300000,1320000,1800000]
    fnametmp = ['5','22','30']
    for i in range(0,len(duration)):
         tmp = get_cdf_from_file(1000,exper_number, command, duration[i], fname+fnametmp[i]+".dat")
         avg_tmp = tmp.mean(0)
         std_tmp = tmp.std(0)
         ans.append(avg_tmp)
         std.append(std_tmp)
    return ans,std


# plot fig with different comnmands(avg value)：DER, Throughput
def plot_avg_duration(command):
    duration = [300000, 1320000, 1800000]
    colors =['black','gray','red']
    labels=['static SF = 12','ADR','DBS']
    width = 0.25
    experiment_number = [0,5,6]
    ans_all =[]
    std_all = []
    index = np.arange(3)
    fig, ax = plt.subplots()
    rec =[]
    for j in range(0,3):
        ans, std = get_duration_data_from_file(experiment_number[j], command)
        rec.append(ax.bar(index+ width*j, ans, width=width, label=labels[j], color=colors[j], yerr=std))
    plt.xticks(index + width / 2, (str(5), str(22), str(30)))
    plt.legend((rec[0], rec[1],rec[2]), ('static SF = 12','ADR','DBS'))
    plt.show()


if __name__ == "__main__":
    #plot_cdf(6, 4, "data/expnumberOfNodes.dat")
    n_groups = 5
    x = [50, 300,  600,  900, 1500]
    x_throughput = [50, 100, 200, 300, 400, 500, 600, 700,800, 900, 1100, 1300, 1500, 1700, 1800, 2000]
    # # python loraDir.py 50 300000 0 7200000 1 numOfNodes power:14dbm payload = 20byte
    # #DER
    # der_0 = [0.7525083612040134, 0.5892098555649957, 0.3479931682322801, 0.19969427459699834, 0.11206009466968513,
    #          0.06923721709974853, 0.04220439483780956, 0.023594767337673975, 0.014977140154501025, 0.008661417322834646,
    #          0.002983721720738754, 0.0005148667782211353, 0.00022113497526052466,0,0,0]
    # der_5 = [0.9571788413098237, 0.9663341645885287, 0.938291785860237, 0.9561690621887007, 0.936124254268669, 0.9382096429159125,
    #          0.9381805409202669, 0.9247467438494935,  0.9197903014416776, 0.9143778801843317, 0.9092138884713663, 0.8920478220455784,
    #          0.8852934674477727, 0.773765839816038, 0.7730433976261127, 0.753138249231025]
    # der_6 = [0.9941908713692946,0.9935787671232876, 0.9891417832532888, 0.9861687413554634, 0.9772562052134178, 0.9709760344970562,
    #          0.9695084432898066, 0.960098109595597, 0.960000000, 0.9569641523525019,  0.9481863321077967, 0.9283852071196369,
    #          0.9275325907936242, 0.8404845912803178, 0.8228321751458386, 0.8184935064935065]
    # der_8 = [ 0.9950413223140496,0.994540109197816, 0.9869680309509264, 0.9882352941176471, 0.9689898679766656, 0.9614548494983277,
    #           0.9695084432898066, 0.960098109595597, 0.94, 0.9349114660021898, 0.9110482678835401, 0.9063213589529379,
    #           0.8152858438089637,  0.7927219593654328, 0.7967696834373239]
    # der_0_sf_7 = [0.9904596704249783,0.9741127348643006,0.9526163988463123,0.9300013999720006,0.9071436108473145,0.8814232519652462,
    #               0.8599649737302977,0.8382318363508112,0.8163944658275252, 0.797616848328099, 0.7608944516522934, 0.7272345782626941,
    #               0.6923269252139127, 0.6572872287724165, 0.6353477870193305,0.607651208415077]
    # #throughput
    # throughput_0 = [2.488888888888889, 3.852777778, 4.52777778, 3.991666667, 3.025, 2.294444443, 1.68055555556, 1.097222223,
    #                 0.7916666666, 0.519444445, 0.21944444444444, 0.0444444444444446, 0.022222222222223, 0.0111111, 0.0000, 0.0001]
    # throughput_5 = [3.166666665,  6.4583333333, 12.75555556, 18.66388888, 25.28055555, 31.675, 37.09722222, 42.6, 48.73611114,
    #                 55.11666666666667, 67.21111111111111, 77.30833333333334, 83.99166666666666, 86.86111111111111, 85.86111111111111,
    #                 83.86111111111111]
    # throughput_6 = [3.3277777,6.447222222, 13.15833333, 19.80555557, 26.13888889, 32.525, 39.39166666, 44.58055556, 50.091666666,
    #                 56.95, 69.4888888888889, 80.12222222222222 , 92.29722222222222, 94.62222222222222, 98.34444444444445,
    #                 109.41666666666667]
    # throughput_0_sf_7 = [3.172222222222222, 6.480555555555555, 12.844444444444445, 18.45277777777778, 23.880555555555556,
    #                      29.58888888888889, 34.1, 39.611111111111114, 43.6, 47.97222222222222, 55.388888888888886, 62.580555555555556,
    #                      69.225, 73.71111111111111, 76.6, 80.875]
    # #latency
    #
    # latency_5_mean=[447.54944, 270.0849, 313.7327, 307.6423,302.16 ]
    # latency_6_mean= [459.223, 279.6801, 323.76, 317, 311.4927]
    # latency_0_mean = [1712.1280000000002, 1700.1280000000002, 1709.1280000000002,1734.1280000000002,1719]
    # n_groups = 5
    # index = np.arange(n_groups)


#     # python loraDir.py 50 300000 0 7200000 1 numOfNodes power:14dbm payload = 40byte
#     # DER
    der_0 = [0.657117278424351, 0.40221857025472474, 0.17296726504751847, 0.07642322361915525, 0.02837624802942722,
             0.011562630917469627, 0.005712245626561942, 0.000712245626561942, 0.000012245626561942, 0.000002245626561942,
             0.000000245626561942, 0.000000045626561942, 0.0000000005626561942, 0, 0, 0]
#     der_5 = [0.9887640449438202, 0.9851362510322048, 0.9731712429260113, 0.9642021203359493, 0.9479804797009657,
#              0.9474706528164851,
#              0.9294719148340104, 0.9112193962443547, 0.9007107023411371, 0.9034360741223577, 0.8927201610146964,
#              0.8437700706486834,
#              0.8508924384120942, 0.6633080409932992, 0.6613464341121715, 0.4690379303801472]
#     der_6 = [0.9934102141680395, 0.9937473947478116, 0.9883575883575884, 0.9803292410714286, 0.9770114942528736,
#              0.9689044130175498,
#              0.9579988928867976, 0.9556756756756757, 0.9493097160718937, 0.9464950586072167, 0.9363134867795321,
#              0.9150836907795014,
#              0.9082341131528316, 0.7750644883920894, 0.768614558251528, 0.556154988185601]
#     der_8 = [0.9950413223140496, 0.994540109197816, 0.9869680309509264, 0.9882352941176471, 0.9689898679766656,
#              0.9614548494983277,
#              0.9695084432898066, 0.960098109595597, 0.94, 0.9349114660021898, 0.9110482678835401, 0.9063213589529379,
#              0.8152858438089637, 0.7927219593654328, 0.7967696834373239]
    der_0_sf_7 = [0.9896373056994818, 0.9787494891704127, 0.9542976939203355, 0.9217559894751419, 0.9046375600584917,
                  0.878698224852071,
                  0.8623233367804205, 0.8378603268945022, 0.8203520869247244, 0.7918774721736731, 0.7605018057403535,
                  0.7180358344818745,
                  0.6844724618447247, 0.6545556860442356, 0.6406210054152044, 0.6089542306972489]
    der_0_sf_9 = [0.967, 0.916, 0.85, 0.80, 0.73,
                  0.68,
                  0.63, 0.582, 0.536, 0.49, 0.43,
                  0.36,
                  0.31, 0.26, 0.24, 0.21]
#     # throughput
#     throughput_0 = [2.0388888888888888, 2.7194444444444446, 2.275, 1.5027777777777778, 0.75, 0.38333333333333336, 0.2222222222222222,
#                     0.00100,
#                     0.00001, 0.00100, 0.00100, 0.00100, 0.00100, 0.00100,
#                     0.0000, 0.0001]
#     throughput_0 = np.array(throughput_0)*2
#     throughput_5 = [3.422222222222222, 6.627777777777778, 12.897222222222222, 19.45277777777778, 25.36111111111111 , 31.675,
#                     36.86388888888889, 42.59444444444444,
#                     47.87777777777778,
#                     53.9, 65.3, 72.98611111111111, 85.67777777777778, 74.79166666666667,
#                     78.15277777777777,
#                     61.794444444444444]
#     throughput_5 = np.array(throughput_5) * 2
#     throughput_0_sf_7 = [3.183333333333333, 6.652777777777778, 12.644444444444444, 18.488888888888887, 24.058333333333334,
#                          29.7, 34.74444444444445, 39.15833333333333,
#                          43.62222222222222,
#                          47.825, 55.56944444444444, 62.227777777777774, 68.76666666666667, 69.31388888888888, 65.56666666666666,
#                          62.34444444444445]
#     throughput_0_sf_7 = np.array(throughput_0_sf_7) * 2
#     throughput_6 = [3.35, 6.622222222222222, 13.205555555555556, 19.519444444444446,
#                          25.73611111111111,
#                          31.591666666666665, 38.458333333333336, 44.2, 50.61666666666667, 57.19722222222222, 68.3638888888889,
#                          78.81666666666666,
#                          90.47777777777777, 87.6361111111111, 92.21666666666667, 73.88055555555556]
#     throughput_6 = np.array(throughput_6) * 2
#     # latency
#
#     latency_5_mean = [447.54944, 270.0849, 313.7327, 307.6423, 302.16]
#     latency_6_mean = [459.223, 279.6801, 323.76, 317, 311.4927]
#     latency_0_mean = [1712.1280000000002, 1700.1280000000002, 1709.1280000000002, 1734.1280000000002, 1719]
#     n_groups = 5
#     index = np.arange(n_groups)
#
#     # Collision ratio
#     collision_0 = [383/1117, 1453/2434, 3915/4735, 6536/7079,9242/9515, 11792/11935,13921/14005,
#                    16344/16741,
#                    18743/19029, 21396/21590, 26393/26477, 31055/31076, 36160/36177, 0.9996,
#                    0.9998, 0.9999]
#     collision_5 = [9/1191, 21/2406, 82/4894, 133/7027, 297/9722, 401/12154, 646/14235, 796/16584,
#                    1089/19075,
#                     1339/21700 , 1807/26612, 2581/31199, 3477/36188, 7536/40809,
#                     8934/43116,
#                     9735/47921]
#     collision_6 = [6/1210, 13/2381, 52/4911, 85/7225, 219/9629, 349/12059, 446/14627, 665/16716,
#                     1089/19224,
#                     921/21424, 1367/26383, 2225/31069, 2595/35823, 6464/ 40529, 7618/43027,
#                     8766/48125]
#
#     collision_0_sf_7 = [11/1153, 62/2395, 230/4854, 500/7143,
#                         879/9477,
#                         1433/12085, 1999/14275, 2751/17012, 3530/19226, 4381/21652, 6266/26206,
#                         8450/30979,
#                         11074/35996, 13834/ 40372, 15826/43403, 18799/47914]
#
#     # # DER
    lines_der0 = plt.plot(x_throughput, der_0, '--',label='static SF = 12')
    plt.setp(lines_der0, linewidth=4.0, color='red')
    lines_der0 = plt.plot(x_throughput, der_0_sf_9, '-.', label='static SF = 9')
    plt.setp(lines_der0, linewidth=4.0, color='black')
    lines_der5 = plt.plot(x_throughput, der_0_sf_7,label='static SF = 7')
    plt.setp(lines_der5, linewidth=3.0,color='gray')
    #lines_der8 = plt.plot(x, der_8, 'o-', c='gray')
    plt.legend(loc = 'best')
    plt.grid(True)
    #plt.title('Deployment')  # 显示图表标题
    ax=plt.gca()
    ax.set_ylabel('temp',fontsize=16,labelpad = 12.5)
    ax.set_xlabel('temp',fontsize=16, labelpad=12.5)
    plt.xlabel('节点个数')  # x轴名称
    plt.ylabel('传输成功率')  # y轴名称
    plt.axis('tight')
    plt.savefig('imag/' + 'DifferentSFDER'+'.png')
    plt.show()
#
#     #throughtput
#     lines_thr0 = plt.plot(x_throughput, throughput_0, '--',label='static SF = 12')
#     plt.setp(lines_thr0, linewidth=4.0, color='black')
#     lines_thr0 = plt.plot(x_throughput, throughput_0_sf_7, '-.', label='static SF = 7')
#     plt.setp(lines_thr0, linewidth=4.0, color='blue')
#     lines_thr5 = plt.plot(x_throughput, throughput_5,label='ADR')
#     plt.setp(lines_thr5, linewidth=3.0,color='gray')
#     lines_thr6 = plt.plot(x_throughput, throughput_6, 'r--',label='DBS')
#     plt.setp(lines_thr6, linewidth=4.0)
#     #lines_der8 = plt.plot(x, der_8, 'o-', c='gray')
#     plt.legend(loc = 'best')
#     plt.grid(True)
#     #plt.title('Deployment')  # 显示图表标题
#     ax=plt.gca()
#     ax.set_ylabel('temp',fontsize=16,labelpad = 12.5)
#     ax.set_xlabel('temp',fontsize=16, labelpad=12.5)
#     plt.xlabel('节点个数')  # x轴名称
#     plt.ylabel('吞吐量（bps）')  # y轴名称
#     plt.axis('tight')
#     plt.savefig('imag/' + 'Throughput'+'.pdf')
#     plt.show()
#
#
# # # collision ratio
# #     lines_col0 = plt.plot(x_throughput, collision_0, '--',label='static SF = 12')
# #     plt.setp(lines_col0, linewidth=4.0, color='black')
# #     lines_col07 = plt.plot(x_throughput, collision_0_sf_7, '-.', label='static SF = 7')
# #     plt.setp(lines_col07, linewidth=4.0, color='blue')
# #     lines_col5 = plt.plot(x_throughput, collision_5,label='ADR')
# #     plt.setp(lines_col5, linewidth=3.0,color='gray')
# #     lines_col6 = plt.plot(x_throughput, collision_6, 'r--',label='DBS')
# #     plt.setp(lines_col6, linewidth=4.0)
# #     #lines_der8 = plt.plot(x, der_8, 'o-', c='gray')
# #     plt.legend(loc = 'best')
# #     plt.grid(True)
# #     #plt.title('Deployment')  # 显示图表标题
# #     ax=plt.gca()
# #     ax.set_ylabel('temp',fontsize=16,labelpad = 12.5)
# #     ax.set_xlabel('temp',fontsize=16, labelpad=12.5)
# #     plt.xlabel('节点个数')  # x轴名称
# #     plt.ylabel('冲突率')  # y轴名称
# #     plt.axis('tight')
# #     plt.savefig('imag/' + 'CollisionNumber'+'.pdf')
# #     plt.show()
#
# ''''
#     # Latency
#     width = 0.25
#     lines_der5 = plt.bar(index + width, latency_6_mean, width, color='r', label='BSR')
#     lines_der0 = plt.bar(index, latency_5_mean, width, color='gray', label='ADR')
#     lines_der5 = plt.bar(index + width*2, latency_0_mean, width, color='black', label='static_SF')
#     plt.xticks(index + width / 2, (str(50), str(300),  str(600),  str(900), str(1500)))
#     plt.legend(loc='best')
#     plt.grid(True)
#     # plt.title('Deployment')  # 显示图表标题
#     ax = plt.gca()
#     ax.set_ylabel('temp', fontsize=16, labelpad=12.5)
#     ax.set_xlabel('temp', fontsize=16, labelpad=12.5)
#     plt.xlabel('节点个数')  # x轴名称
#     plt.ylabel('延迟（ms）')  # y轴名称
#     plt.axis('tight')
#     plt.savefig('imag/' + 'Latency' + '.pdf')
#     plt.show()
# '''

 # # python loraDir.py 50 300000 0 7200000 1 numOfNodes power:14dbm payload = 40byte
 #    # DER
 #    der_0 = [0.8569065343258891, 0.692600422832981, 0.48722741433021804, 0.33688433868289985, 0.2356814381270903,
 #             0.16423752810860331, 0.11031340604721801, 0.07863145258103241, 0.05334093618785962, 0.03990534081945153,
 #             0.019233716475095787, 0.009490221224751523, 0.004644354997607453, 0.001644354997607453, 0, 0]
 #    der_5 = [0.9974226804123711, 0.9966130397967824, 0.9930672268907563, 0.9882747068676717, 0.9836492397417205,
 #             0.982098458478369,
 #             0.9733637747336378, 0.9648149241395596, 0.962748171368861, 0.9612495968299314, 0.9584810705707423 ,
 #             0.9440097878231752,
 #             0.9398992725237829, 0.7958773991382687, 0.7937952382060651, 0.608569810608444]
 #    der_6 = [0.9983416252072969, 0.9970649895178197, 0.9938753959873284, 0.992756651344198, 0.9879269425239914,
 #             0.9833900838800764,
 #             0.9789372246696035, 0.9758146792294304, 0.9728854291834282, 0.9720925891357103, 0.9669600182080267,
 #             0.9553323768531803,
 #             0.952170529709299, 0.8727479425648123, 0.8666651279802433, 0.6868372714369207 ]
 #    der_8 = [0.9950413223140496, 0.994540109197816, 0.9869680309509264, 0.9882352941176471, 0.9689898679766656,
 #             0.9614548494983277,
 #             0.9695084432898066, 0.960098109595597, 0.94, 0.9349114660021898, 0.9110482678835401, 0.9063213589529379,
 #             0.8152858438089637, 0.7927219593654328, 0.7967696834373239]
 #    der_0_sf_7 = [0.9900414937759336, 0.9807460890493381, 0.9682438192668372, 0.9511012605624047, 0.9336186201857843,
 #                  0.9188783174762143,
 #                  0.9026100236012773, 0.8901039799211187, 0.8748292170257488, 0.8570112400958172, 0.8308249190321966,
 #                  0.8041656083312166,
 #                  0.7746215249105423, 0.7514462202176684, 0.7254927697928288, 0.7122901528438987]
 #    # throughput
 #    throughput_0 = [2.8,4.55,6.5167,6.7638,6.2638,5.478,4.438,3.639,2.858,2.39,1.394,0.822,0.4583,0.1001,0.0000,0]
 #    throughput_0 = np.array(throughput_0)/2
 #    throughput_5 = [3.225, 6.538, 13.1305, 19.67, 26.237, 32.9167, 39.0805, 45.39, 51.186, 57.95, 69.83, 81.44, 79.31, 69.31, 65, 60]
 #    throughput_5 = np.array(throughput_5) / 2
 #    throughput_0_sf_7 = [3.3138,6.7917,12.61,19.072,24.847,30.583,36.13,41.375,46,51,60,70,80,85,92,94]
 #    throughput_0_sf_7 = np.array(throughput_0_sf_7) /2
 #    throughput_6 = [3.34,6.605,13.072,19.79,26.59,32.89,39.5,45,51,57,70,83,95,98,104,98]
 #    throughput_6 = np.array(throughput_6) /2
 #    # latency
 #
 #    latency_5_mean = [447.54944, 270.0849, 313.7327, 307.6423, 302.16]
 #    latency_6_mean = [459.223, 279.6801, 323.76, 317, 311.4927]
 #    latency_0_mean = [1712.1280000000002, 1700.1280000000002, 1709.1280000000002, 1734.1280000000002, 1719]
 #    n_groups = 5
 #    index = np.arange(n_groups)
 #
 #    # Collision ratio
 #    collision_0 = [383/1117, 1453/2434, 3915/4735, 6536/7079,9242/9515, 11792/11935,13921/14005,
 #                   16344/16741,
 #                   18743/19029, 21396/21590, 26393/26477, 31055/31076, 36160/36177, 0.9996,
 #                   0.9998, 0.9999]
 #    collision_5 = [9/1191, 21/2406, 82/4894, 133/7027, 297/9722, 401/12154, 646/14235, 796/16584,
 #                   1089/19075,
 #                    1339/21700 , 1807/26612, 2581/31199, 3477/36188, 7536/40809,
 #                    8934/43116,
 #                    9735/47921]
 #    collision_6 = [6/1210, 13/2381, 52/4911, 85/7225, 219/9629, 349/12059, 446/14627, 665/16716,
 #                    1089/19224,
 #                    921/21424, 1367/26383, 2225/31069, 2595/35823, 6464/ 40529, 7618/43027,
 #                    8766/48125]
 #
 #    collision_0_sf_7 = [11/1153, 62/2395, 230/4854, 500/7143,
 #                        879/9477,
 #                        1433/12085, 1999/14275, 2751/17012, 3530/19226, 4381/21652, 6266/26206,
 #                        8450/30979,
 #                        11074/35996, 13834/ 40372, 15826/43403, 18799/47914]
 #
 #    # DER
 #    lines_der0 = plt.plot(x_throughput, der_0, '--',label='static SF = 12')
 #    plt.setp(lines_der0, linewidth=4.0, color='black')
 #    lines_der0 = plt.plot(x_throughput, der_0_sf_7, '-.', label='static SF = 7')
 #    plt.setp(lines_der0, linewidth=4.0, color='blue')
 #    lines_der5 = plt.plot(x_throughput, der_5,label='ADR')
 #    plt.setp(lines_der5, linewidth=3.0,color='gray')
 #    lines_der6 = plt.plot(x_throughput, der_6, 'r--',label='DBS')
 #    plt.setp(lines_der6, linewidth=4.0)
 #    #lines_der8 = plt.plot(x, der_8, 'o-', c='gray')
 #    plt.legend(loc = 'best')
 #    plt.grid(True)
 #    #plt.title('Deployment')  # 显示图表标题
 #    ax=plt.gca()
 #    ax.set_ylabel('temp',fontsize=16,labelpad = 12.5)
 #    ax.set_xlabel('temp',fontsize=16, labelpad=12.5)
 #    plt.xlabel('节点个数')  # x轴名称
 #    plt.ylabel('DER')  # y轴名称
 #    plt.axis('tight')
 #    plt.savefig('imag/' + 'NodesOfNumber'+'.pdf')
 #    plt.show()

    # #throughtput
    # lines_thr0 = plt.plot(x_throughput, throughput_0, '--',label='static SF = 12')
    # plt.setp(lines_thr0, linewidth=4.0, color='black')
    # lines_thr0 = plt.plot(x_throughput, throughput_0_sf_7, '-.', label='static SF = 7')
    # plt.setp(lines_thr0, linewidth=4.0, color='blue')
    # lines_thr5 = plt.plot(x_throughput, throughput_5,label='ADR')
    # plt.setp(lines_thr5, linewidth=3.0,color='gray')
    # lines_thr6 = plt.plot(x_throughput, throughput_6, 'r--',label='DBS')
    # plt.setp(lines_thr6, linewidth=4.0)
    # #lines_der8 = plt.plot(x, der_8, 'o-', c='gray')
    # plt.legend(loc = 'best')
    # plt.grid(True)
    # #plt.title('Deployment')  # 显示图表标题
    # ax=plt.gca()
    # ax.set_ylabel('temp',fontsize=16,labelpad = 12.5)
    # ax.set_xlabel('temp',fontsize=16, labelpad=12.5)
    # plt.xlabel('节点个数')  # x轴名称
    # plt.ylabel('吞吐量（bps）')  # y轴名称
    # plt.axis('tight')
    # plt.savefig('imag/' + 'Throughput'+'.pdf')
    # plt.show()


# # collision ratio
#     lines_col0 = plt.plot(x_throughput, collision_0, '--',label='static SF = 12')
#     plt.setp(lines_col0, linewidth=4.0, color='black')
#     lines_col07 = plt.plot(x_throughput, collision_0_sf_7, '-.', label='static SF = 7')
#     plt.setp(lines_col07, linewidth=4.0, color='blue')
#     lines_col5 = plt.plot(x_throughput, collision_5,label='ADR')
#     plt.setp(lines_col5, linewidth=3.0,color='gray')
#     lines_col6 = plt.plot(x_throughput, collision_6, 'r--',label='DBS')
#     plt.setp(lines_col6, linewidth=4.0)
#     #lines_der8 = plt.plot(x, der_8, 'o-', c='gray')
#     plt.legend(loc = 'best')
#     plt.grid(True)
#     #plt.title('Deployment')  # 显示图表标题
#     ax=plt.gca()
#     ax.set_ylabel('temp',fontsize=16,labelpad = 12.5)
#     ax.set_xlabel('temp',fontsize=16, labelpad=12.5)
#     plt.xlabel('节点个数')  # x轴名称
#     plt.ylabel('冲突率')  # y轴名称
#     plt.axis('tight')
#     plt.savefig('imag/' + 'CollisionNumber'+'.pdf')
#     plt.show()

''''
    # Latency
    width = 0.25
    lines_der5 = plt.bar(index + width, latency_6_mean, width, color='r', label='BSR')
    lines_der0 = plt.bar(index, latency_5_mean, width, color='gray', label='ADR')
    lines_der5 = plt.bar(index + width*2, latency_0_mean, width, color='black', label='static_SF')
    plt.xticks(index + width / 2, (str(50), str(300),  str(600),  str(900), str(1500)))
    plt.legend(loc='best')
    plt.grid(True)
    # plt.title('Deployment')  # 显示图表标题
    ax = plt.gca()
    ax.set_ylabel('temp', fontsize=16, labelpad=12.5)
    ax.set_xlabel('temp', fontsize=16, labelpad=12.5)
    plt.xlabel('节点个数')  # x轴名称
    plt.ylabel('延迟（ms）')  # y轴名称
    plt.axis('tight')
    plt.savefig('imag/' + 'Latency' + '.pdf')
    plt.show()
'''