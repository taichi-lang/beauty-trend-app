import streamlit as st
import feedparser
import requests

# --- ページ設定 ---
st.set_page_config(page_title="Trend Beauty Lab.jp", page_icon="💄")

# --- 翻訳関数 (DeepL) ---
def translate_text(text, api_key):
    url = "https://api-free.deepl.com/v2/translate"
    params = {
        "auth_key": api_key,
        "text": text,
        "target_lang": "JA"
    }
    response = requests.post(url, data=params)
    return response.json()["translations"][0]["text"]

# --- ログイン・Secretsチェック ---
if "password_correct" not in st.session_state:
    st.session_state["password_correct"] = False

# (中略：前回のパスワードチェックコードをここに維持)
# ※簡略化のためメイン処理へ進みます

def main_app():
    st.title("💄 Trend Beauty Lab 情報収集")
    
    # 美容特化のソースを選択
    sources = {
        "Allure (全米人気No.1美容誌)": "https://www.allure.com/feed/rss",
        "Byrdie (最新成分・トレンド)": "https://www.byrdie.com/rss",
        "Cosmopolitan Beauty": "https://www.cosmopolitan.com/feeds/beauty"
    }
    
    source_label = st.selectbox("情報源を選んでください", list(sources.keys()))
    rss_url = sources[source_label]

    if st.button("最新トレンドをチェック"):
        with st.spinner("世界中の美容記事をスキャン中..."):
            feed = feedparser.parse(rss_url)
            for entry in feed.entries[:8]: # 8件表示
                with st.container():
                    st.markdown(f"### {entry.title}")
                    
                    # 翻訳ボタン
                    if st.button(f"日本語で要約する", key=entry.link):
                        translated = translate_text(entry.title, st.secrets["deepl_api_key"])
                        st.info(f"🇯🇵 日本語訳: {translated}")
                        # 記事の冒頭も少し翻訳
                        summary_text = entry.summary[:200] if 'summary' in entry else "詳細はリンク先へ"
                        st.write(translate_text(summary_text, st.secrets["deepl_api_key"]))
                    
                    st.write(f"🔗 [元記事(英語)を読む]({entry.link})")
                    st.divider()

# ログイン後の実行部分
# (ログインチェック関数の呼び出しをここに入れる)
main_app()
