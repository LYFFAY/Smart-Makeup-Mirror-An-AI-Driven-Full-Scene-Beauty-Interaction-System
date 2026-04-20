import os, json, requests
from fastapi import FastAPI
from fastapi.responses import HTMLResponse
import uvicorn

app = FastAPI()
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# --- 豆包 API 配置 ---
RAW_KEY = "ark-11a0a68f-0f00-4249-a2da-551ca43a3a16e"
ENDPOINT_ID = "doubao-seed-2-0-pro-260215"

# --- 13 种妆容超强容错数据库 (包含全量同音词) ---
MAKEUP_DB = {
    "classic": {
        "name": "中式古典妆",
        "keywords": ["古典", "舒华", "叶舒华", "中式古典", "鼓点", "古点", "谷点", "固点", "股典", "古电", "古店",
                     "骨典", "书华", "淑华", "姝华", "疏华", "殊华", "输华", "舒桦", "舒骅", "舒画", "舒话", "舒滑",
                     "树华", "数华", "术华", "苏华", "素华", "舒娃", "舒哇", "低饱和古典"],
        "params": {"lip_color": "rgba(180, 40, 40, 0.4)", "gloss": 0.3, "blush": "rgba(200, 50, 50, 0.2)"},
        "url": "https://www.xiaohongshu.com/search_result/69a041d9000000001a034f1c?xsec_token=ABvZoUk4LEnEArFSSNGG23BHEMKBKiU66GmK6ZRhyaNm4=&xsec_source=pc_search"
    },
    "earth": {
        "name": "中式大地妆",
        "keywords": ["大地", "大滴", "大底", "大帝", "大弟", "打滴", "打地", "达地", "大迪", "大蒂", "大抵", "张婧仪",
                     "张静怡", "张静宜", "张靖怡", "张靖宜", "张景怡", "张敬仪", "张竟仪", "章静怡", "张晶怡", "张菁怡",
                     "地母", "地亩", "地木", "地牧", "爆改浓颜"],
        "params": {"lip_color": "rgba(160, 82, 45, 0.5)", "gloss": 0.2, "blush": "rgba(160, 82, 45, 0.15)"},
        "url": "http://xhslink.com/o/9WKBIR6Htkw"
    },
    "fox": {
        "name": "中式狐系妆",
        "keywords": ["狐系", "壶系", "胡系", "狐狸", "约会", "魅惑", "没货", "美货", "狐戏", "媚惑", "约回", "狐莉",
                     "有手就会", "老婆快来", "胡戏"],
        "params": {"lip_color": "rgba(200, 0, 50, 0.5)", "gloss": 0.4, "blush": "rgba(255, 20, 147, 0.25)"},
        "url": "http://xhslink.com/o/6VmjpOSdnVi"
    },
    "asian": {
        "name": "欧美亚裔妆",
        "keywords": ["亚裔", "欧美亚裔", "黄黑皮", "亚一", "压抑", "氛围感", "四分钟", "4分钟", "跟练版", "压一氛围"],
        "params": {"lip_color": "rgba(139, 69, 19, 0.5)", "gloss": 0.1, "blush": "rgba(160, 82, 45, 0.3)"},
        "url": "http://xhslink.com/o/3j939lSbkom"
    },
    "tomboy": {
        "name": "欧美中性妆",
        "keywords": ["中性", "欧美中性", "浓颜少年", "少年妆", "菱形脸", "我看花了眼", "千呼万唤", "重性", "终性",
                     "种性"],
        "params": {"lip_color": "rgba(120, 80, 70, 0.4)", "gloss": 0, "blush": "rgba(100, 100, 100, 0.1)"},
        "url": "http://xhslink.com/o/2zt8xZAJ1Tn"
    },
    "doggy": {
        "name": "日系狗狗妆",
        "keywords": ["狗狗", "日系狗狗", "无辜", "眼妆", "勾勾", "日系勾勾", "狗狗眼", "新手宝宝"],
        "params": {"lip_color": "rgba(255, 127, 80, 0.3)", "gloss": 0.5, "blush": "rgba(255, 160, 122, 0.3)"},
        "url": "http://xhslink.com/o/1wnab7kvC34"
    },
    "manga": {
        "name": "日系漫画妆",
        "keywords": ["漫画", "日系漫画", "古早感", "大眼睛", "催的", "速学", "古早感漫画", "忙话", "慢画", "满画"],
        "params": {"lip_color": "rgba(255, 105, 180, 0.4)", "gloss": 0.4, "blush": "rgba(255, 192, 203, 0.4)"},
        "url": "http://xhslink.com/o/4jqE3ipdbKE"
    },
    "moe": {
        "name": "萌感少年妆",
        "keywords": ["萌感", "萌系", "少年", "正太", "含金量", "盟感", "梦感", "猛感", "谁懂这个"],
        "params": {"lip_color": "rgba(255, 182, 193, 0.3)", "gloss": 0.2, "blush": "rgba(255, 228, 225, 0.4)"},
        "url": "http://xhslink.com/o/A9MVirsCHty"
    },
    "idol": {
        "name": "韩系女团妆",
        "keywords": ["女团", "韩系女团", "蕾妆", "方圆脸", "又韩又蕾", "寒系", "女团妆", "一点也不难"],
        "params": {"lip_color": "rgba(255, 20, 147, 0.4)", "gloss": 0.6, "blush": "rgba(255, 105, 180, 0.3)"},
        "url": "http://xhslink.com/o/3lzz9YkHPPn"
    },
    "smoky": {
        "name": "韩系小烟熏",
        "keywords": ["烟熏", "小烟熏", "韩系烟熏", "微醺", "李彩煐", "李彩英", "一菜鸟", "李彩云", "烟熏韩妆"],
        "params": {"lip_color": "rgba(150, 50, 50, 0.5)", "gloss": 0.2, "blush": "rgba(120, 60, 60, 0.2)"},
        "url": "http://xhslink.com/o/1NaRdfkWLfJ"
    },
    "rose": {
        "name": "低饱和玫瑰妆",
        "keywords": ["玫瑰", "低饱和", "玫瑰妆", "清冷", "拿捏", "没瑰", "梅瑰", "三分钟妆教", "3min"],
        "params": {"lip_color": "rgba(188, 143, 143, 0.5)", "gloss": 0.2, "blush": "rgba(219, 112, 147, 0.2)"},
        "url": "http://xhslink.com/o/8nPiNBSj5ep"
    },
    "simple": {
        "name": "淡颜妆",
        "keywords": ["日常", "素颜", "氛围感", "淡妆", "淡人", "冬季淡人", "冬季淡妆", "蛋妆", "诞妆", "蛋颜"],
        "params": {"lip_color": "rgba(255, 192, 203, 0.2)", "gloss": 0.2, "blush": "rgba(255, 182, 193, 0.15)"},
        "url": "http://xhslink.com/o/AjnMOLNpeDV"
    },
    "fast": {
        "name": "快速出门妆",
        "keywords": ["快速", "出门", "制服", "女高", "马上", "超高", "出片率", "女高妆", "块速", "块素"],
        "params": {"lip_color": "rgba(255, 160, 122, 0.3)", "gloss": 0.3, "blush": "rgba(255, 218, 185, 0.2)"},
        "url": "http://xhslink.com/o/7hNr4mjlGqh"
    }
}


def get_doubao_reply(makeup_name):
    """
    现在会传入匹配到的妆容名称，强制 AI 在回复中包含它。
    """
    try:
        url = "https://ark.cn-beijing.volces.com/api/v3/chat/completions"
        headers = {"Content-Type": "application/json", "Authorization": f"Bearer {RAW_KEY}"}
        payload = {
            "model": ENDPOINT_ID,
            "messages": [
                {"role": "system",
                 "content": "你是小镜。说话极度温柔甜美。当主人选好妆容后，你必须首先告诉主人：'好的主人，为您推荐[妆容名称]！'。然后夸奖主人的品味，并引导主人点击下方的链接。"},
                {"role": "user", "content": f"主人现在匹配了：{makeup_name}"}
            ]
        }
        response = requests.post(url, headers=headers, json=payload, timeout=5)
        return response.json()['choices'][0]['message']['content']
    except:
        # 兜底回复现在也包含名称了
        return f"好的主人，为您推荐{makeup_name}！主人今天也要美美哒出门哦。小镜在下方为您准备了详细的秘籍链接，快点开看看嘛~"


@app.get("/")
async def get_index():
    with open(os.path.join(BASE_DIR, "index.html"), "r", encoding="utf-8") as f:
        return HTMLResponse(content=f.read())


@app.get("/api/ai_chat")
async def ai_chat(text: str):
    text_l = text.lower().strip()

    # 暖心开场白识别：如果用户只是打招呼
    if any(k in text_l for k in ["你好", "小镜", "在吗", "嗨"]):
        return {
            "name": "初始状态",
            "reply": "你好主人，今天也要美美哒出门哦！想画什么妆容直接告诉小镜吧~",
            "params": MAKEUP_DB["simple"]["params"],
            "url": None
        }

    # 妆容匹配逻辑
    matched_style = None
    for style_id, data in MAKEUP_DB.items():
        if any(k in text_l for k in data["keywords"]):
            matched_style = data
            break

    if not matched_style:
        matched_style = MAKEUP_DB["simple"]  # 没听清默认给淡妆

    # 关键修改：将匹配到的妆容名字传给 AI
    reply_text = get_doubao_reply(matched_style['name'])

    return {**matched_style, "reply": reply_text}


if __name__ == "__main__":
    uvicorn.run(app, host="127.0.0.1", port=8000)