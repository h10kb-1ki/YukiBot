from flask import Flask, request, abort
from linebot import LineBotApi, WebhookHandler
from linebot.exceptions import InvalidSignatureError
from linebot.models import MessageEvent, TextMessage, TextSendMessage
import os
import requests
from bs4 import BeautifulSoup
import random

# 環境変数（Render）
CHANNEL_SECRET = os.environ.get("LINE_CHANNEL_SECRET")
CHANNEL_ACCESS_TOKEN = os.environ.get("LINE_CHANNEL_ACCESS_TOKEN")

app = Flask(__name__)
line_bot_api = LineBotApi(CHANNEL_ACCESS_TOKEN)
handler = WebhookHandler(CHANNEL_SECRET)

@app.route("/callback", methods=["POST"])
def callback():
    signature = request.headers["X-Line-Signature"]
    body = request.get_data(as_text=True)
    try:
        handler.handle(body, signature)
    except InvalidSignatureError:
        abort(400)
    return "OK"

@handler.add(MessageEvent, message=TextMessage)
def handle_message(event):
    user_message = event.message.text.strip()
    if user_message in ['cmd', 'コマンド', 'ヘルプ']:
        reply_text = cmd()
    elif user_message in ['電車', 'jr', '名鉄']:
        reply_text = train()
    elif user_message in ['バス', 'あんくる']:
        reply_text = bus()
    elif user_message in ['天気', '雨雲', '雲']:
        reply_text = weather()
    elif user_message in ['週間', '週']:
        reply_text = weekly()
    elif user_message in ['月間', '月']:
        reply_text = monthly()
    elif user_message in ['休', '休暇', '休み']:
        reply_text = yasumi()
    elif user_message in ['宇宙', '宇宙兄弟', '名言']:
        reply_text = select_message()
    else:
        reply_text = out_of_cmd()

    #reply_text = db_search(user_message)

    line_bot_api.reply_message(
        event.reply_token,
        TextSendMessage(text=reply_text)
    )

def cmd():
    txt = '電車 バス 天気 勤務（週、月、休） 宇宙兄弟'

def train():    
    url = 'https://transit.yahoo.co.jp/traininfo/detail/192/193/'
    res = requests.get(url)
    soup = BeautifulSoup(res.text, "html.parser")
    statusJ = soup.find('dd', class_='normal')
    if statusJ:
        jr_status = statusJ.text
    else:
        jr_status = '遅延あり'
        jr = f'■東海道本線[豊橋～米原]：{jr_status}（https://traininfo.jr-central.co.jp/zairaisen/status_detail.html?line=10001&lang=ja）\n'

    url = 'https://transit.yahoo.co.jp/traininfo/detail/208/0/'
    res = requests.get(url)
    soup = BeautifulSoup(res.text, "html.parser")
    statusM = soup.find('dd', class_='normal')
    if statusM:
        meitetsu_status = statusM.text
    else:
        meitetsu_status = '遅延あり'
    meitetsu = f'■名鉄名古屋本線：{meitetsu_status}（https://top.meitetsu.co.jp/em/）\n\n'
    return jr + meitetsu + '▶乗り換え案内 https://www.jorudan.co.jp/norikae/'

def bus():
    m_bus = '▶名鉄バス（安城駅発 更生病院行）\nhttps://navi.meitetsu-bus.co.jp/mb/DepQR.aspx?p=320103000 \n'
    a_left = '▶あんくるバス（左まわり）\nhttps://ankuru-bus.com/rosen_junkan_l.php \n'
    a_right = '▶あんくるバス（右まわり）\nhttps://ankuru-bus.com/rosen_junkan_r.php'
    return m_bus + a_left + a_right

def weather():
    return '▶雨雲レーダー \nhttps://tenki.jp/radar/map/'

def shift_data():
    url = 'https://drive.google.com/embeddedfolderview?id=12Zb899YTrxKT15XXixmuMUXe7s3xQi0x#list'
    res = requests.get(url)
    res.encoding = res.apparent_encoding
    soup = BeautifulSoup(res.text, "html.parser")
    titles =soup.find_all(class_='flip-entry-title')
    title_list = []
    for i in range(0, len(titles)):
        title = titles[i].get_text()
        title_list.append(title)
    refs =soup.find_all('a')
    ref_list =[]
    for i in range(0, len(refs)):
        ref = refs[i].get('href')
        ref_list.append(ref)

def weekly():
    title_list, ref_list = shift_data()
    txt = ''
    for i in range(0, len(title_list)):
        if '週間' in title_list[i]:
            txt += f'■{title_list[i]}\n{ref_list[i]}\n'
    return txt

def monthly():
    title_list, ref_list = shift_data()
    txt = ''
    for i in range(0, len(title_list)):
        if '勤務' in title_list[i]:
            if not '週間' in title_list[i]:
                txt += f'■{title_list[i]}\n{ref_list[i]}\n'
    return txt

def yasumi():
    title_list, ref_list = shift_data()
    txt = ''
    for i in range(0, len(title_list)):
        if '休' in title_list[i]:
            txt += f'■{title_list[i]}\n{ref_list[i]}\n'
    return txt

def select_message():
    sb = [
        '本気の失敗には…価値がある', 
        '迷ったときはね どっちが正しいかなんて考えちゃダメ。『どっちが楽しいか』で決めなさい', 
        'It’s a piece of cake!', 
        '俺の敵は\nだいたい俺です', 
        'グーみたいな奴がいて、チョキみたいな奴もいて、パーみたいな奴もいる\n誰が一番強いか答えを知ってる奴はいるか？', 
        '人という字は支えあっているのではない\n「支える者がいてその上に立つ者がいる」', 
        '死ぬ覚悟なんていらねえぞ\n必要なのは”生きる覚悟”だ', 
        '危機感のない者には成長もない', 
        'ネクタイを締める理由なんて1コしかねえ\n仕事が無事に終わった後に”緩める”ためだ', 
        '「空」は誰のもんでもない\n「人生」は自分のもんだ\n人生はコントロールが利く', 
        '事故った時、整備士に責任を押し付けるのはパイロットの恥っちゅうもんだ\n”心のノート”にメモっとけ', 
        '避けようのないもんはそりゃある\nだがそれを言ってどうなる\nワシらは死ぬまで生きるだけだ', 
        'やれるとこまでやって何かを見つけろよ\nどーせやるなら\nその道の一流を目指そうぜ', 
        '自分で気付いて動き出さない者にかけてやるやさしい言葉などない', 
        '大事なのは”できる”という経験を得ること', 
        '逃げ道ってのは甘えの道だ\n誰でも楽に歩けるかわりどこにも辿り着けない', 
        '”諦め”ってある意味では”決意”に似てるよな', 
        '一生消えないなら受け入れるしかない\n内ポケットの不発弾も月まで連れていく', 
        '人の悪口というのは仲間内で言う人は”凡人”\n口に出さない人は”賢人”\n不特定多数に向けて発信する人は”暇人”ですから', 
        'キノコと名乗ったからにはカゴに入れ', 
        '死人や神様に答えを求める前に周りをよく見るこった\n生きてる兄貴と話せ', 
        '本当ははじめから”バカでかいドア”なんでものはない\n小さなドアがいっぱいあるだけだ', 
        'We are lonely, but not alone.', 
        '最下位でも何でもいいから絶対…ゴールまで歩いてやる\n1位と最下位との差なんて大したことねーんだよ\nゴールすることとしないことの差に比べりゃ', 
        '新しいモノ作ろうって話なんだ\n最初は何だって”仮説”だろ', 
        '先のこと考えるのやめたんだ。わかってたけど、大事なのは結局、今だ。今、この訓練が、どうやったら最高のもんになるかだけど考えることにした。やったことは、きっと俺らの力に変わるはず。だからケンジちょっとだけ、無理なことに挑戦してこうぜ。', 
        'モノ作りには失敗することにかける金と労力が必要なんだよ。いい素材使ってるモノがいいモノとは限らねえんだ\nだけど…失敗を知って乗り越えたモノなら、それはいいモノだ', 
        'もしこれが運だとしてもねー、それも俺の実力なわけだよ。', 
        '大事なのは……動くこと\n何もせずに止まっているのは道端の石コロです\n動いて動いて輝く石は流れ星……\n「生きた石コロ」です', 
        'バカげてると思うか？茶番だと\nだがこれをやるのが今のお前の現実だ、受け入れろ\n大事なのは“できる”という経験を得ること', 
        '”止まる”も”進む”もコントロールするのはお前だ', 
        ]
    i = random.randint(0, len(sb)-1)
    return sb[i]

def out_of_cmd():
    message = [
        'I don’t really understand what you’re saying.', 
        'I’m not quite sure what you mean.', 
        'I don’t get what you’re saying.', 
        'I’m having a little trouble understanding what you’re saying.', 
        'Sorry, I don’t quite follow.', 
        'I’m afraid I don’t quite understand what you mean.', 
        'Could you clarify what you mean?', 
    ]
    i = random.randint(0, len(message)-1)
    return message[i]

@app.route("/", methods=["GET"])
def index():
    return 'OK'

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000)))
