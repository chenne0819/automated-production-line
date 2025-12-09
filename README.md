# automated-production-line

[YouTube Demo](https://youtu.be/dcsEkommlak)

---

## Project Description

This project focuses on building an automated and intelligent order-processing workflow. It retrieves order data from a database and uses object detection to identify items within each order, improving processing efficiency and reducing the likelihood of human error.

---

### Objectives

- Automate order processing by retrieving order data from a MySQL database and identifying items within each order.
- Improve accuracy and performance by using object-detection techniques (such as YOLO) to quickly and reliably recognize objects.
- Increase processing speed by integrating a robotic arm to automate the item-sorting workflow.

---

## Project Structure

- **My_code/**: Custom scripts and a modified version of `detect.py`.
- **dobot/**: Official Dobot SDK and related code.
- **yolov7/**: Official YOLOv7 source code.
- **image_label/**: Training images, labels, and test images for object-detection training and validation.

---

## Installation & Usage

### 1. Download Dobot and YOLOv7 Code

- Clone or download the Dobot SDK to your local directory.  
- Clone or download the YOLOv7 repository.  
- Copy the scripts inside **My_code/** into the corresponding folders of Dobot and YOLOv7.

### 2. Install Dependencies

```bash
cd yolov7
pip install -r requirements.txt
pip install pymysql
```

### 3. Configure the Dobot Server

This project uses TCP communication to simulate a factory scenario where the robotic arm may not directly support Python APIs. Python’s built-in socket module is used to send commands to the arm.

1. Open dobot_yolomove.py and update:

 - HOST: Set it to your local network IP.

2. Modify robot motion commands in dobot_yolomove.py according to:

 - Your robot’s position

 - Coordinate system

 - Picking and sorting actions

3. Database Setup

 - Create a database identical to the one shown in the demo video.

 - Keep track of your database username and password.

4. Configure the YOLOv7 Client

 Open detect_fix.py and modify:

 - HOST: Set this to the Dobot server IP.

 - weights path: Provide the path to your YOLOv7 model weights.

5. Run the Program

Start the server:

```bash
  python dobot/dobot_yolomove.py
```

Start the client:

```bash
  python yolov7/detect_fix.py
```

Adjust paths and settings according to your environment to ensure the system runs correctly.

---

### Contribution

Designed a simplified production-line system combining YOLO-based object detection with a database-driven order-processing workflow, simulating a lightweight automated sorting line.

---

### Contact

If you have any questions, feel free to contact:

 - Email: cucuchen105@gmail.com
