# automated-production-line

[YouTube Demo](https://youtu.be/dcsEkommlak)

---

## 專案說明

這個專案是關於自動化&智慧化訂單處理的項目。它使用資料庫取得訂單和物體辨識技術來辨識訂單中的物品，從而提高訂單處理的效率並降低錯誤的可能性。

---

### 目標

- 自動化訂單處理，從資料庫MySQL中抓取訂單資料並辨識訂單中的物品。
- 提升準確性和效能，使用物體辨識技術（如 Yolo）快速而準確地識別訂單中的物品。
- 提高訂單處理速度，整合機器手臂以實現自動化的物品分類過程。

---

## 專案結構

- My_code/：我自己的程式碼和更改過的detect.py。
- dobot/：Dobot 官方程式碼。
- yolov7/：Yolov7 官方程式碼。
- image_label/：包含訓練圖片、標籤以及測試圖片，用於檢測訓練結果。

---

## 安裝與使用

1.下載 Dobot 和 Yolov7 程式碼：

- Clone 或下載 Dobot 的程式碼到本地目錄。<br>
- Clone 或下載 Yolov7 的程式碼到本地目錄。<br>
- 在Dobot 和 Yolov7 的資料夾中找到 My_code 中的程式碼。

2.安裝相依套件：
```bash
  cd yolov7
  pip install -r requirement.txt
  pip install pymsql
```

3.修改 Dobot 伺服器端設定：

這邊運用到伺服器端口的原因:
為了模擬在工廠的手臂可能沒有python的api，所以會用到TCP傳輸協定將訊息傳給手臂，
剛好python內建就有包含socket的套件

(1)打開 dobot_yolomove.py 檔案，找到並修改以下參數：

HOST：設定為網路ip位置。

(2)根據手臂的位置、座標系、以及動作來修改dobot_yolomove.py的機器動作執行指令

(3)設定資料庫：

建立與影片中相同的資料庫，並記下資料庫的使用者名稱和密碼。

(4)修改 Yolov7 客戶端設定：

- 打開 detect_fix.py 檔案，找到並修改以下參數：

- HOST：設定為 Dobot 伺服器端的主機地址。
- weights 的路徑：設定為 Yolov7 模型權重的路徑。

(5)執行程式：

首先執行Server端 dobot/dobot_yolomove.py 檔案。
然後執行Client端 yolov7/detect_fix.py 檔案。
請根據你的實際情況，將範例中的路徑和設定調整為正確的值。請確保你已按照上述步驟進行修改和設定，以確保程式的正常執行。

## 貢獻
設計簡單版本結合YOLO運用的生產線，並且結合資料庫達成一個簡易的訂單模擬

## 聯絡方式
如果有任何問題，請通過以下方式聯絡我們：
- 電子郵件：cucuchen105@gmail.com
