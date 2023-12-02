from flask import Flask, render_template, Response, jsonify, request, url_for
import cv2
from ultralytics import YOLO
import time
import os
import math
from waitress import serve
from PIL import Image
import json
import base64
from datetime import datetime
from flask_wtf import FlaskForm
from wtforms import FileField, SubmitField,StringField,DecimalRangeField,IntegerRangeField
from werkzeug.utils import secure_filename
from wtforms.validators import InputRequired,NumberRange

app = Flask(__name__)

webcam_status = False

# app.config['SEND_FILE_MAX_AGE_DEFAULT'] = 0

# model = YOLO('model/best.pt')
# cam = cv2.VideoCapture(0)
# def video_detection(path_x):
#     video_capture = path_x
#     #Create a Webcam Object
#     cap=cv2.VideoCapture(video_capture)
#     frame_width=int(cap.get(3))
#     frame_height=int(cap.get(4))
#     #out=cv2.VideoWriter('output.avi', cv2.VideoWriter_fourcc('M', 'J', 'P','G'), 10, (frame_width, frame_height))

#     model=YOLO("model/kelapa.pt")
#     classNames = ['buah matang', 'buah mentah']
#     while True:
#         success, img = cap.read()
#         results=model(img,stream=True)
#         for r in results:
#             boxes=r.boxes
#             for box in boxes:
#                 x1,y1,x2,y2=box.xyxy[0]
#                 x1,y1,x2,y2=int(x1), int(y1), int(x2), int(y2)
#                 print(x1,y1,x2,y2)
#                 cv2.rectangle(img, (x1,y1), (x2,y2), (255,0,255),3)
#                 conf=math.ceil((box.conf[0]*100))/100
#                 cls=int(box.cls[0])
#                 class_name=classNames[cls]
#                 label=f'{class_name} {conf}'
#                 t_size = cv2.getTextSize(label, 0, fontScale=2, thickness=2)[0]
#                 print(t_size)
#                 c2 = x1 + t_size[0], y1 - t_size[1] - 3
#                 cv2.rectangle(img, (x1,y1), c2, [255,0,255], -1, cv2.LINE_AA)  # filled
#                 cv2.putText(img, label, (x1,y1-2),0, 1,[255,255,255], thickness=2,lineType=cv2.LINE_AA)
#         yield img
#         #out.write(img)
#         #cv2.imshow("image", img)
#         #if cv2.waitKey(1) & 0xFF==ord('1'):
#             #break
#     #out.release()
# cv2.destroyAllWindows()
# def generate_frames(path_x):
#     yolo_output = video_detection(path_x)
#     for detection_ in yolo_output:
#         ref,buffer=cv2.imencode('.jpg',detection_)

#         frame=buffer.tobytes()
#         yield (b'--frame\r\n'
#                     b'Content-Type: image/jpeg\r\n\r\n' + frame +b'\r\n')

# def generate_frames_web(path_x):
#     yolo_output = video_detection(path_x)
#     for detection_ in yolo_output:
#         ref,buffer=cv2.imencode('.jpg',detection_)

#         frame=buffer.tobytes()
#         yield (b'--frame\r\n'
#                     b'Content-Type: image/jpeg\r\n\r\n' + frame +b'\r\n')

def generate_frames_web(path_x):
    global webcam_status

    video_capture = path_x
    cap = cv2.VideoCapture(video_capture)
    frame_width = int(cap.get(3))
    frame_height = int(cap.get(4))

    model = YOLO("model/kelapa.pt")
    classNames = ['buah matang', 'buah mentah']

    while webcam_status:
        success, img = cap.read()
        results = model(img, stream=True)

        for r in results:
            boxes = r.boxes
            for box in boxes:
                x1, y1, x2, y2 = box.xyxy[0]
                x1, y1, x2, y2 = int(x1), int(y1), int(x2), int(y2)
                print(x1, y1, x2, y2)
                cv2.rectangle(img, (x1, y1), (x2, y2), (255, 0, 255), 3)
                conf = math.ceil((box.conf[0] * 100)) / 100
                cls = int(box.cls[0])
                class_name = classNames[cls]
                label = f'{class_name} {conf}'
                t_size = cv2.getTextSize(label, 0, fontScale=2, thickness=2)[0]
                print(t_size)
                c2 = x1 + t_size[0], y1 - t_size[1] - 3
                cv2.rectangle(img, (x1, y1), c2, [255, 0, 255], -1, cv2.LINE_AA)  # filled
                cv2.putText(img, label, (x1, y1 - 2), 0, 1, [255, 255, 255], thickness=2, lineType=cv2.LINE_AA)

        _, jpeg = cv2.imencode('.jpg', img)
        frame = jpeg.tobytes()
        yield (b'--frame\r\n'
               b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')

    cap.release()
    cv2.destroyAllWindows()

@app.route('/')
def index():
    wt = print('Welcome to')
    return render_template('index.html')
@app.route('/contact')
def contact():
    return render_template('contact.html')
@app.route('/about')
def about():
    return render_template('about.html')
@app.route('/startchecking',methods=['GET','POST'])
def startchecking():
    return render_template('startchecking3.html')
# def upload():
#     if 'file' not in request.files:
#         return 'No file part'

#     file = request.files['file']

#     if file.filename == '':
#         return 'No selected file'

#     upload_folder = os.path.join(os.getcwd(), 'upload')
#     if not os.path.exists(upload_folder):
#         os.makedirs(upload_folder)

#     file.save(os.path.join(upload_folder, file.filename))
#     return 'File successfully uploaded'


@app.route('/save_image', methods=['POST','GET'])
def save_image():
    try:
        # Dapatkan data JSON dari permintaan
        data = request.json
        image_data_url = data.get('image')

        # Validasi data
        if not image_data_url:
            return jsonify({'message': 'Invalid data'}), 400

        # Ubah data URL menjadi format gambar
        _, image_data = image_data_url.split(',')
        image_binary = base64.b64decode(image_data)

        # Tambahkan timestamp ke nama file untuk membuatnya unik
        timestamp = datetime.now().strftime('%Y%m%d%H%M%S')
        namafile = f'captured_image_{timestamp}.png'

        # Simpan gambar ke direktori "photosnap"
        save_path = os.path.join(os.getcwd(), 'static/photosnap', namafile)
        with open(save_path, 'wb') as f:
            f.write(image_binary)

        return jsonify({'message': 'Image saved successfully', 'image_url': url_for('static', filename=namafile)})
    except Exception as e:
        print('Error saving image:', str(e))
        return jsonify({'message': 'Internal server error'}), 500

@app.route("/detect", methods=["POST"])
def detect():
    buf = request.files["image_file"]
    boxes = detect_objects_on_image(Image.open(buf.stream))
    return Response(
      json.dumps(boxes),  
      mimetype='application/json'
    )
def detect_objects_on_image(buf):
    model = YOLO("model/best.pt")
    results = model(buf, conf=0.8)
    result = results[0]
    output = []
    for box in result.boxes:
        x1, y1, x2, y2 = [
          round(x) for x in box.xyxy[0].tolist()
        ]
        class_id = box.cls[0].item()
        prob = round(box.conf[0].item(), 2)
        output.append([
          x1, y1, x2, y2, result.names[class_id], prob
        ])
    return output

# @app.route('/video_feed')
# def video_feed():
#     return Response(generate_frames(), mimetype='multipart/x-mixed-replace; boundary=frame')

# @app.route('/take_snapshot', methods=['GET'])
# def take_snapshot():
#     ret, frame = cam.read()
#     if ret:
#         cv2.imwrite('photosnap/snapshot.jpg', frame)
#         return jsonify(status='success', message='Snapshot taken and saved.')
#     else:
#         return jsonify(status='error', message='Failed to take snapshot.')

# @app.route('/webapp')
# def webapp():
#     #return Response(generate_frames(path_x = session.get('video_path', None),conf_=round(float(session.get('conf_', None))/100,2)),mimetype='multipart/x-mixed-replace; boundary=frame')
#     return Response(generate_frames_web(path_x=0), mimetype='multipart/x-mixed-replace; boundary=frame')

@app.route('/webapp')
def webapp():
    return Response(generate_frames_web(path_x=0), mimetype='multipart/x-mixed-replace; boundary=frame')

@app.route('/webapp/start', methods=['POST'])
def start_webcam():
    global webcam_status

    # Jika webcam sudah aktif, kembalikan respons bahwa webcam sudah aktif
    if webcam_status:
        return jsonify({'message': 'Webcam is already started'}), 400

    # Logika untuk memulai webcam (contoh: mengubah status menjadi True)
    webcam_status = True

    return jsonify({'message': 'Webcam started successfully'}), 200

@app.route('/webapp/stop', methods=['POST'])
def stop_webcam():
    global webcam_status

    # Jika webcam sudah nonaktif, kembalikan respons bahwa webcam sudah nonaktif
    if not webcam_status:
        return jsonify({'message': 'Webcam is already stopped'}), 400

    # Logika untuk menghentikan webcam (contoh: mengubah status menjadi False)
    webcam_status = False

    return jsonify({'message': 'Webcam stopped successfully'}), 200


# @app.route('/upload', methods=['POST'])
# def upload():
#     if 'file' not in request.files:
#         return 'No file part'

#     file = request.files['file']

#     if file.filename == '':
#         return 'No selected file'

#     upload_folder = 'upload/'
#     if not os.path.exists(upload_folder):
#         os.makedirs(upload_folder)

#     file.save(os.path.join(upload_folder, file.filename))
#     return 'File successfully uploaded'
   
if __name__ == '__main__':
  app.run(host = '0.0.0.0', debug = True)
