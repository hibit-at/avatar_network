import os
import requests
from PIL import Image
from io import BytesIO
import math
import boto3
from datetime import datetime
import sys

# AWS設定
if os.path.exists('local.py'):
    from local import AWS_ACCESS_KEY_ID, AWS_SECRET_ACCESS_KEY, BUCKET_NAME
else:
    AWS_ACCESS_KEY_ID = os.environ.get('AWS_ACCESS_KEY_ID')
    AWS_SECRET_ACCESS_KEY = os.environ.get('AWS_SECRET_ACCESS_KEY')
    BUCKET_NAME = os.environ.get('BUCKET_NAME')
S3_REGION = 'ap-northeast-1'
SCALE = 4.5
URL = 'https://avatar-network.herokuapp.com/api/avatar/'


def get_data(limit):
    res = requests.get(URL+f'?limit={limit}').json()
    return res


def get_image_from_line(line):
    url = line['imageURL']
    item_count = line['item_count']
    res = requests.get(url)
    image = Image.open(BytesIO(res.content))
    axis = int(math.sqrt(item_count)*SCALE)
    axis = max(axis, 1)
    image = image.resize((axis, axis))
    return image


def create_image(data):
    axis = 1200
    canvas = Image.new('RGBA', (axis, axis))
    imgs = [get_image_from_line(line) for line in data]
    print(len(imgs))
    width = [img.size[0] for img in imgs]
    width.append(1001)
    print(width)
    idx = 0
    sy = 0
    sx = 0
    while idx < len(data):
        pos = idx
        reach = 0
        while reach <= axis:
            reach += width[pos]
            pos += 1
        print(reach)
        buf = range(idx, pos - 1)
        print(list(buf))
        for b in buf:
            canvas.paste(imgs[b], (sx, sy))
            sx += width[b]
        sy += width[idx]
        idx = pos
        sx = 0
    byte_io = BytesIO()
    canvas.save(byte_io, 'PNG')
    img_data = byte_io.getvalue()
    return img_data


def upload_to_s3(img_data, file_name):
    # S3クライアントの作成
    s3 = boto3.client('s3', aws_access_key_id=AWS_ACCESS_KEY_ID,
                      aws_secret_access_key=AWS_SECRET_ACCESS_KEY,
                      region_name=S3_REGION)

    # 現在の日付を取得
    date_str = datetime.now().strftime('%Y-%m-%d')
    # タイムスタンプを付けたファイル名を生成
    timestamped_file_name = f"{date_str}-{file_name}"

    # バイトデータをS3バケットにアップロード
    s3.put_object(Bucket=BUCKET_NAME,
                  Key=timestamped_file_name,
                  Body=BytesIO(img_data),
                  ContentType='image/png')


if __name__ == '__main__':
    limit = 0
    if len(sys.argv) > 1:
        limit = int(sys.argv[1])
    print(limit)
    data = get_data(limit)
    # create_image(data)
    img_data = create_image(data)
    upload_to_s3(img_data, 'summary.png')
