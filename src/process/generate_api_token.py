import time
import jwt

model = 'mirage'

if model == 'mirage':
    ak = "2ZQadUQCRvHbP7xKLrQ5PSBbVjx" # 填写您的ak
    sk = "QOYBgg3dYLtnacgi8h6txLm0ajucxWVJ" # 填写您的sk
elif model == 'vqa':
    ak = '2ZnO3279j01wbmtvpcZhZ8MDn72'
    sk = 'lnHLPX766a1tVhDBYKsYp78qAn6875gF'


def encode_jwt_token(ak, sk):
    headers = {
        "alg": "HS256",
        "typ": "JWT"
    }
    payload = {
        "iss": ak,
        "exp": int(time.time()) + 18000000, # 填写您期望的有效时间，此处示例代表当前时间+30分钟
        "nbf": int(time.time()) - 5 # 填写您期望的生效时间，此处示例代表当前时间-5秒
    }
    token = jwt.encode(payload, sk, headers=headers)
    return token

authorization = encode_jwt_token(ak, sk)
print(authorization) # 打印生成的API_TOKEN
