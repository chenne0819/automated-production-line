import threading
import time
import multiprocessing as mp
import DobotDllType as dType
import socket
import pandas as pd
import pymysql
import random
# server

# 伺服器 IP 地址
HOST = '10.0.38.95'
# 伺服器端口號
PORT = 64110
# 檢查有無重複
cache = set()


# mysql訂單連線
def mysql_order():
    # 連接 MySQL 數據庫(要改成自己的)
    with pymysql.connect(host='120.110.113.150',
                         user='username',
                         password='your password',
                         database='your Database') as order:
        # 創建一個游標對象
        with order.cursor() as cur:
            # 執行一個查詢
            cur.execute('SELECT * FROM Orders')

            # 獲取查詢結果(fetchall只能抓少量資料)
            result = cur.fetchall()
            # print(type(result)) -> tuple

            # 將查詢結果轉換成 pandas 的 DataFrame 格式
            df = pd.DataFrame(result, columns=[i[0] for i in cur.description])

            # 顯示 DataFrame
            print(df, '\n')

    # 自動關閉游標和連接order.close(), cur.close()
    return df


# 第一台手臂抓物體到輸送帶&啟動輸送帶(注意COM)
def yolo_move(x, y):
    CON_STR = {
        dType.DobotConnect.DobotConnect_NoError:  "DobotConnect_NoError",
        dType.DobotConnect.DobotConnect_NotFound: "DobotConnect_NotFound",
        dType.DobotConnect.DobotConnect_Occupied: "DobotConnect_Occupied"}

    api = dType.load()
    state = dType.ConnectDobot(api, "COM4", 115200)[0]
    print("Connect status:", CON_STR[state])

    if state == dType.DobotConnect.DobotConnect_NoError:
        # 清空队列
        dType.SetQueuedCmdClear(api)

        # 设置运动参数
        dType.SetHOMEParams(api, 200, 200, 200, 200, isQueued=1)  # 設定回參數
        dType.SetPTPJointParams(api, 200, 200, 200, 200, 200, 200, 200, 200, isQueued=1)  # 設定關節點參數
        dType.SetPTPCommonParams(api, 100, 100, isQueued=1)  # 速度,加速度

        '''
            在YOLO的x, y是0.48, 0.56這是倍率
            camera原大小是640 * 480
            所以將x * 640, y * 480
        '''
        x = x * 640
        y = y * 480
        # 找出鏡頭接近(0,0)的座標設為原點和機器座標
        # print(x, y)

        '''
        找出機器座標在鏡頭320,240(正中間)的位置
        將39-47行更改
        '''
        if x >= 320:
            y_grab = (-7.3630) + (x - 320) * 0.3031
        else:
            y_grab = (-7.3630) - (320 - x) * 0.3031

        if y >= 240:
            x_grab = 214.2041 + (y - 240) * 0.3194
        else:
            x_grab = 214.2041 - (240 - y) * 0.3194

        print(f'物體在機器手臂的座標: {x_grab}, {y_grab}')

        # 放的x,y,z固定(以下的參數都是根據你的手臂座標進行調整)
        x_put, y_put, z_put = 84.5956, -224.7439, 14.1903

        # 最高z點固定, z_down物體放置的高度
        z_up, z_down = 115.9008, -43.6553

        # 取得點位置
        current_pose = dType.GetPose(api)
        # 關節座標轉是current_pose[7]
        dType.SetPTPCmdEx(api, 4, 0,  0,  0, current_pose[7], 1)
        # 下去吸的點OK
        dType.SetPTPCmd(api, dType.PTPMode.PTPMOVLXYZMode, x_grab, y_grab, z_down, current_pose[3], 1)
        # 吸盤開OK
        dType.SetEndEffectorSuctionCup(api, 1, 1, isQueued=1)
        # 上點OK
        dType.SetPTPCmdEx(api, 4, (-5.1021), (-2.0097), 3.5568, current_pose[7], 1)
        # 關節座標
        dType.SetPTPCmdEx(api, 4, (-69.7604), 3.5966, 3.4854, current_pose[7], 1)
        # 下點OK
        dType.SetPTPCmd(api, dType.PTPMode.PTPMOVLXYZMode, x_put, y_put, z_put, current_pose[3], 1)
        # 吸盤關閉OK
        dType.SetEndEffectorSuctionCup(api, 1, 0, isQueued=1)  # 能否控制/吸住/列隊
        # 放下物體的上點
        dType.SetPTPCmd(api, dType.PTPMode.PTPMOVLXYZMode, x_put, y_put, z_up, current_pose[3], 1)

        # 停止机器人运动
        dType.SetQueuedCmdStopExec(api)

        # 开始执行指令队列
        dType.SetQueuedCmdStartExec(api)

        # 啟動輸送帶
        STEP_PER_CRICLE = 360.0 / 1.8 * 10.0 * 16.0
        MM_PER_CRICLE = 3.1415926535898 * 36.0
        vel = float((-50)) * STEP_PER_CRICLE / MM_PER_CRICLE
        dType.SetEMotorEx(api, 0, 1, int(vel), 1)

    # 断开连接
    dType.DisconnectDobot(api)


# 第二台手臂做出排序(注意COM)
def yolo_move2(cls, stack_num, order_num):
    CON_STR2 = {
        dType.DobotConnect.DobotConnect_NoError:  "DobotConnect_NoError\n",
        dType.DobotConnect.DobotConnect_NotFound: "DobotConnect_NotFound",
        dType.DobotConnect.DobotConnect_Occupied: "DobotConnect_Occupied"}

    api2 = dType.load()
    state = dType.ConnectDobot(api2, "COM3", 115200)[0]
    print("Connect status:", CON_STR2[state])

    while True:

        dType.SetInfraredSensor(api2, 1, 1, 0)
        if (dType.GetInfraredSensor(api2, 1)[0]) == 1:
            current_pose = dType.GetPose(api2)
            # 關節座標轉是current_pose[7]
            dType.SetPTPCmdEx(api2, 4, (-88.6526), (-2.0097), 3.5568, current_pose[7], 1)
            dType.SetPTPCmdEx(api2, 4, (-88.5026), 9.2403, 57.4869, current_pose[7], 1)
            dType.SetEndEffectorSuctionCupEx(api2, 1, 1)  # 吸取
            dType.SetPTPCmdEx(api2, 4, (-88.6526), (-2.0097), 3.5568, current_pose[7], 1)

            # order_num: red blue pink, cls: red pink blue 利用and確保兩個條件都符合, 用-=1將訂單減少用來茶訂單是否完成
            # red
            if cls == '0' and order_num[0]:
                dType.SetPTPCmdEx(api2, 4, 1.4879, (-2.0097), 3.5568, current_pose[7], 1)
                dType.SetPTPCmdEx(api2, 2, 186.1855, 21.2696, (-46.7294) + stack_num[0] * 20.5252, current_pose[3], 1)
                dType.SetEndEffectorSuctionCupEx(api2, 0, 1)
                order_num_shared[0] = order_num[0] - 1
                count_stack_shared[0] = stack_num[0] + 1

            # pink
            elif cls == '1' and order_num[2]:
                dType.SetPTPCmdEx(api2, 4, 1.4879, (-2.0097), 3.5568, current_pose[7], 1)
                dType.SetPTPCmdEx(api2, 2, 186.1844, (-72.9302), (-46.2392) + stack_num[1] * 20.5252, current_pose[3], 1)
                dType.SetEndEffectorSuctionCupEx(api2, 0, 1)
                order_num_shared[2] = order_num[2] - 1
                count_stack_shared[2] = stack_num[2] + 1

            # blue
            elif cls == '2' and order_num[1]:
                dType.SetPTPCmdEx(api2, 4, 1.4879, (-2.0097), 3.5568, current_pose[7], 1)
                dType.SetPTPCmdEx(api2, 2, 287.2669, (-87.7728), (-46.2392) + stack_num[2] * 20.5252, current_pose[3], 1)
                dType.SetEndEffectorSuctionCupEx(api2, 0, 1)
                order_num_shared[1] = order_num[1] - 1
                count_stack_shared[1] = stack_num[1] + 1

            else:
                print("超出訂單所需")
                dType.SetPTPCmdEx(api2, 4, (-89.0366), 34.5829, (-5.72), current_pose[7], 1)
                dType.SetPTPCmdEx(api2, 2, 4.7733,  (-283.8532), (-49.1875) + stack_num[3] * 20.5252 , current_pose[3], 1)
                dType.SetEndEffectorSuctionCupEx(api2, 0, 1)
                dType.SetPTPCmdEx(api2, 4, (-89.0366), 34.5829, (-5.72), current_pose[7], 1)
                dType.SetPTPCmdEx(api2, 4, (-88.6526), (-2.0097), 3.5568, current_pose[7], 1)
                count_stack_shared[3] = stack_num[3] + 1

            dType.SetPTPCmdEx(api2, 4, 1.4879, (-2.0097), 3.5568, current_pose[7], 1)

            # 停止机器人运动
            dType.SetQueuedCmdStopExec(api2)

            # 开始执行指令队列
            dType.SetQueuedCmdStartExec(api2)

            # 断开连接
            dType.DisconnectDobot(api2)
            break


if __name__ == "__main__":
    # 建立 socket 物件，並綁定 IP 和 port
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.bind((HOST, PORT))
        s.listen()
        print(f"伺服器已啟動，監聽地址：{HOST}:{PORT}")
        # 接收資料表(可以改寫input選擇)
        order_df = mysql_order()

        # 挑一筆資料
        rand_int = random.randint(0, 3)
        choose_order = order_df.iloc[[rand_int]]
        print(choose_order)

        # 取出 red blue pink 的數量存成list
        order_num = [choose_order.iloc[0][i] for i in range(1, 4)]
        print(order_num)

        # 計算第幾次堆疊(red, blue, pink, 超過數量或不在訂單所需的產品)
        count_stack = {'0': 0, '1': 0, '2': 0, 'x': 0}
        count_stack_list = list(count_stack.values())

        # 建立一個用於觀測每次搬運結果的DataFrame, 先將內容設為 0
        order_category = ["red", "blue", "pink", "none"]
        remaining_orders = [0, 0, 0, None]
        stacked_quantity = [0, 0, 0, None]

        # 建立 DataFrame，並指定索引為剩餘訂單:Remaining Orders, 同種類的堆疊的數量Stacked Count
        df_result = pd.DataFrame([remaining_orders, stacked_quantity],
                                 columns=order_category,
                                 index=['Remaining Orders', 'Stacked Count'])

        # 無窮迴圈等待客戶端連線
        while True:
            # 等待客戶端連接
            conn, addr = s.accept()
            with conn:
                print('Client connected:', addr)
                while True:
                    data = conn.recv(1024)  # 接收 client 傳來的資料
                    if not data:
                        break
                    cls, x, y = data.decode().split(",")  # 將資料解碼，得到 x, y 座標
                    # 將其str轉成浮點數
                    # cls = float(cls)
                    x, y = float(x), float(y)
                    print(cls, x, y)

                    # 傳送訊息給客戶端
                    message = '啟動機器'
                    conn.send(message.encode())

                    # 平行處理兩台機器的移動
                    t1 = threading.Thread(target=yolo_move, args=(x, y))
                    # 開始執行兩個執行緒
                    t1.start()
                    # 等待兩個執行緒結束
                    t1.join()

                    time.sleep(1)

                    # 利用共享變數來將參數回傳更新
                    order_num_shared = mp.Array('i', order_num)
                    count_stack_shared = mp.Array('i', count_stack_list)

                    t2 = threading.Thread(target=yolo_move2, args=(cls, count_stack_list, order_num))
                    t2.start()
                    t2.join()

                    # 訂單產品數量會在處理之後逐漸減少, 所以將訂單產品數量的資料更新
                    order_num = list(order_num_shared)
                    df_result.loc['Remaining Orders'] = order_num + [None]  # 將剩餘的訂單產品數量更新到 df_result
                    # print(f'剩下的訂單數量: {order_num}')

                    # 將已經堆疊的訂單產品數量更新到 df_result
                    count_stack_list = list(count_stack_shared)
                    df_result.loc['Stacked Count'] = count_stack_list  # 將剩餘的訂單產品數量更新到 df_result
                    # print(f'更新後的堆疊: {count_stack_list}')

                    # 堆疊三個0, 1, 2所以到2就歸0
                    # count_stack[cls] = count_stack[cls] + 1 if count_stack[cls] < 2 else 0

                    # 印出df_result來確認搬運和分類的結果
                    print(df_result)

                    # 計算訂單的值若總和等於0, 代表訂單完成
                    print(f"{order_df.iloc[0][0]}'s order is done!") if sum(order_num) == 0 else print(f'{order_num} keep going!')

                    # 在這裡儲存 x, y 座標並回傳確認訊息給 client
                    conn.sendall(b'Coordinates received')

