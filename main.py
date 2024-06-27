import pyaudio
import wave
import base64
import urllib
import requests
import json
import pyttsx3 as pyttsx

engine = pyttsx.init()

#百度智能云替换为自己的
C_API_KEY = "Your_API_KEY"
C_SECRET_KEY = "Your_SECRET_KEY"

#百度千帆大模型替换为自己的
L_API_Key = 'Your_API_KEY'
L_Secret_Key = 'Your_SECRET_KEY'

def get_access_token_C():
    """
    使用 AK，SK 生成鉴权签名（Access Token）
    :return: access_token，或是None(如果错误)
    """
    url = "https://aip.baidubce.com/oauth/2.0/token"
    params = {"grant_type": "client_credentials", "client_id": C_API_KEY, "client_secret": C_SECRET_KEY}
    return str(requests.post(url, params=params).json().get("access_token"))

def get_access_token_L():
    """
    使用 API Key，Secret Key 获取access_token，替换下列示例中的应用API Key、应用Secret Key
    """
#    API_Key = 'fxOjed6yirtXlNkswHJxUXkP'
#    Secret_Key = 'kFQswsA5EdmD8DckWIyWmH80Clj00uoo'
    url = f"https://aip.baidubce.com/oauth/2.0/token?grant_type=client_credentials&client_id={L_API_Key}&client_secret={L_Secret_Key}"
 
    payload = json.dumps("")
    headers = {
        'Content-Type': 'application/json',
        'Accept': 'application/json'
    }
 
    response = requests.request("POST", url, headers=headers, data=payload)
    return response.json().get("access_token")

def get_file_content_as_base64(path, urlencoded=False):
    """
    获取文件base64编码
    :param path: 文件路径
    :param urlencoded: 是否对结果进行urlencoded 
    :return: base64编码信息
    """
    with open(path, "rb") as f:
        content = base64.b64encode(f.read()).decode("utf8")
        if urlencoded:
            content = urllib.parse.quote_plus(content)
    return content

def main():
    
    CHUNK = 1024
    FORMAT = pyaudio.paInt16
    CHANNELS = 1
    RATE = 16000
    RECORD_SECONDS = 5
    WAVE_OUTPUT_FILENAME = "output.wav"

    while True:
        p = pyaudio.PyAudio()

        stream = p.open(format=FORMAT,
                        channels=CHANNELS,
                        rate=RATE,
                        input=True,
                        frames_per_buffer=CHUNK)
        print("开始录音，请说话...")
        frames = []

        for i in range(0, int(RATE / CHUNK * RECORD_SECONDS)):
            data = stream.read(CHUNK)
            frames.append(data)
        print("录音结束。")
        stream.stop_stream()
        stream.close()
        p.terminate()

        wf = wave.open(WAVE_OUTPUT_FILENAME, 'wb')
        wf.setnchannels(CHANNELS)
        wf.setsampwidth(p.get_sample_size(FORMAT))
        wf.setframerate(RATE)
        wf.writeframes(b''.join(frames))
        wf.close()

        url_C = "https://vop.baidu.com/server_api"

        # speech 可以通过 get_file_content_as_base64("C:\fakepath\output.wav",False) 方法获取
        payload_C = json.dumps({
            "format": "wav",
            "rate": 16000,
            "channel": 1,
            "cuid": "mzxm5vxjLGK0rFXzTPjZLon20l5C98iI",
            "token": get_access_token_C(),
            "dev_pid": 1537,
            "speech": get_file_content_as_base64("F:/xiangmu/LLM/wenxin/output.wav") ,
            "len": 159788
        })
        headers_C = {
            'Content-Type': 'application/json',
            'Accept': 'application/json'
        }

        response1 = requests.request("POST", url_C, headers=headers_C, data=payload_C)
        for line in response1.iter_lines():
            data_str1 = line.decode("UTF-8")
            if data_str1:  # 间隔输出空行 因此要判断是否为空
                json_str1 = data_str1.replace('data:', '')
                json_out1 = json.loads(json_str1)
                out1 = json_out1.get('result')
                print(out1)


            information =  {
                "messages": [],
                'stream': True
            }

            input1 = str(out1)
            information['messages'].append({
                "role": "user",
                "content": input1
            })

            if input1=='好的。':
                Switch = False

            url_L = "https://aip.baidubce.com/rpc/2.0/ai_custom/v1/wenxinworkshop/chat/yi_34b_chat?access_token=" + get_access_token_L()

            payload_L = json.dumps(information)
            headers_L = {
                'Content-Type': 'application/json'
            }

            response2 = requests.request("POST", url_L, headers=headers_L, data=payload_L,stream = True)
            output2 = str()
            for line in response2.iter_lines():
                data_str2 = line.decode("UTF-8")
                if data_str2:  # 间隔输出空行 因此要判断是否为空
                    json_str2 = data_str2.replace('data:', '')
                    json_out2 = json.loads(json_str2)
                    out2 = json_out2.get('result')
                    output2 += out2
                    print(out2)
                    engine.say(out2)
                    engine.runAndWait()

            information['messages'].append({
                "role": "assistant",
                "content": output2
            }) # 把模型的输出再返回给模型 实现上下文连续对话

if __name__ == '__main__':
    main()
    print('结束对话')
