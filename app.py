import streamlit as st
import feedparser
import requests
from rembg import remove
from PIL import Image
from io import BytesIO

st.set_page_config(page_title="Trend Beauty Lab.jp", page_icon="💄")

# --- 翻訳関数 (最新認証) ---
def translate_text(text, api_key):
    try:
        url = "https://api-free.deepl.com/v2/translate"
        headers = {"Authorization": f"DeepL-Auth-Key {api_key}"}
        data = {"text": [text], "target_lang": "JA"}
        response = requests.post(url, headers=headers, data=data, timeout=10)
        return response.json()["translations"][0]["text"] if response.status_code == 200 else "翻訳エラー"
    except:
        return "通信エラー"

# --- 背景削除関数 ---
def remove_bg(image_url):
    try:
        response = requests.get(image_url)
        img = Image.open(BytesIO(response.content))
        output = remove(img) # 背景削除実行
        return output
    except:
        return None

# --- ログインチェック (前回同様) ---
if "password_correct" not in st.session_state:
    st.session_state["password_correct"] = False

if not st.session_state["password_correct"]:
    # ログイン画面 (省略：既存のコードを使用)
    pass 
else:
    st.title("💄 Trend Beauty Lab.jp")
    
    # カテゴリ分け（韓国・日本を追加）
    category = st.sidebar.selectbox("カテゴリ選択", ["海外トレンド", "韓国・アジア", "日本最新"])
    
    sources = {
        "海外トレンド": {
            "Allure": "https://www.allure.com/feed/rss",
            "Byrdie": "https://www.byrdie.com/rss"
        },
        "韓国・アジア": {
            "K-pop Herald (Beauty)": "http://www.koreaherald.com/common/rss_xml.php?ct=1001",
            "Soompi (Style)": "https://www.soompi.com/feed"
        },
        "日本最新": {
            "PR TIMES (美容)": "https://prtimes.jp/main/html/searchrlp/ct_id/14/rss",
            "WWDJAPAN (Beauty)": "https://www.wwdjapan.com/category/beauty/feed"
        }
    }

    selected_source = st.selectbox("情報源を選択", list(sources[category].keys()))
    
    if st.button(f"{selected_source} の最新記事を取得"):
        with st.spinner("記事を読み込み中..."):
            feed = feedparser.parse(sources[category][selected_source])
            if feed.entries:
                st.session_state["current_entries"] = feed.entries[:10]
            else:
                st.error("記事が見つかりませんでした。別のソースを試してください。")

    if "current_entries" in st.session_state:
        for i, entry in enumerate(st.session_state["current_entries"]):
            with st.expander(f"📌 {entry.title}"):
                st.write(f"🔗 [元記事を読む]({entry.link})")
                
                # 画像の抽出 (RSSからサムネイル取得を試みる)
                img_url = ""
                if 'links' in entry:
                    for link in entry.links:
                        if 'image' in link.get('type', ''):
                            img_url = link.get('href')
                
                col1, col2 = st.columns(2)
                with col1:
                    if st.button("日本語解析", key=f"tr_{i}"):
                        t_title = translate_text(entry.title, st.secrets["deepl_api_key"])
                        st.success(t_title)
                
                with col2:
                    if img_url and st.button("背景を消して画像保存", key=f"bg_{i}"):
                        with st.spinner("背景削除中..."):
                            no_bg_img = remove_bg(img_url)
                            if no_bg_img:
                                st.image(no_bg_img, caption="背景削除済み")
                                # ダウンロードボタン
                                buf = BytesIO()
                                no_bg_img.save(buf, format="PNG")
                                st.download_button("画像をダウンロード", buf.getvalue(), f"beauty_{i}.png", "image/png")
                            else:
                                st.warning("画像の背景削除に失敗しました（直リンクが許可されていない可能性があります）")
