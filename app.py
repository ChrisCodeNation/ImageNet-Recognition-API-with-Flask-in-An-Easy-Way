from flask import Flask, render_template, request
import torch
from torchvision import transforms
from torchvision.models import resnet50
from PIL import Image
import os

"""
建立一個ImageNet的辨識API
模型使用pytorch預訓練好的ResNet50
整體概念是執行app.py
會跳出一個網頁
接著上傳照片進行辨識
最後顯示結果
"""

# 固定格式
app = Flask(__name__)
model = resnet50(pretrained=True)
model.eval()

transform = transforms.Compose([
                transforms.Resize([224,224]),
                transforms.ToTensor(),
                transforms.Normalize(mean = (0.5,0.5,0.5),
                                     std = (0.5,0.5,0.5))])
# 將label轉成list
with open('./imagenet-classes.txt', 'r') as f:
    labels = [line.strip() for line in f.readlines()]

# 讀取影像
def read_image(filename):
    img = Image.open(filename)
    img = transform(img)
    # 轉成[1,3,244,244]
    img_stack = torch.stack([img])
    return img_stack

# allow files with png, jpg, jpeg
ALLOW_EXT = set(['jpg', 'jpeg', 'png'])
def allow_file(filename):
    return '.' in filename and \
           filename.rsplit('.',1)[1] in ALLOW_EXT

# 最初始頁面
@app.route('/')
def homeapge():
    return render_template('home.html')

# 進行辨識
@app.route('/predict', methods = ['GET', 'POST'])
def predict():
    if request.method == 'POST':
        file = request.files['file']
        # 判斷副檔名
        if file and allow_file(file.filename):
            filename = file.filename
            # 將影像儲存
            file_path = os.path.join('./static/images', filename)
            file.save(file_path)
            img = read_image(file_path)
            output = model(img)
            _, preds = torch.max(output.data, 1)
            classes = labels[preds[0]]
            return render_template('predict.html', classes=classes, user_image=file_path)
        else:
            return "Unable to read the file. Please check file extension."

# 固定格式
if __name__ == '__main__':
    app.run(debug=True)