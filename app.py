import streamlit as st
import feedparser
import requests

# --- ページ設定 ---
st.set_page_config(page_title="Trend Beauty Lab.jp", page_icon="💄")

# --- 翻訳関数 ---
def translate_text(text, api_key):
    try:
        url = "https://api-free.deepl.com/v2/translate"
        params = {
            "auth_key": api_key,
            "text": text,
            "target_lang": "JA"
        }
        response = requests.post(url, data=params, timeout=10)
        return response.json()["translations"][0]["text"]
    except Exception as e:
        return f"翻訳エラー: {e}"

# --- パスワード認証 ---
def check_password():
    if "password_correct" not in st.session_state:
        st.session_state["password_correct"] = False

    if st.session_state["password_correct"]:
        return True

    st.title("Trend Beauty Lab ログイン")
    pwd = st.text_input("パスワードを入力してください", type="password")
    if st.button("ログイン"):
        if pwd == st.secrets["password"]:
            st.session_state["password_correct"] = True
            st.rerun()
        else:
            st.error("パスワードが違います")
    return False

# --- メイン処理 ---
if check_password():
    st.title("💄 Trend Beauty Lab.jp")
    
    # セッション状態の初期化（保存リスト用）
    if "saved_articles" not in st.session_state:
        st.session_state["saved_articles"] = []

    tab1, tab2 = st.tabs(["最新トレンド検索", "保存済み記事一覧"])

    with tab1:
        sources = {
            "Allure (美容専門誌)": "https://www.allure.com/feed/rss",
            "Byrdie (成分・トレンド)": "https://www.byrdie.com/rss",
            "Cosmopolitan Beauty": "https://www.cosmopolitan.com/feeds/beauty"
        }
        source_label = st.selectbox("情報源を選択", list(sources.keys()))
        
        if st.button("最新情報を取得"):
            feed = feedparser.parse(sources[source_label])
            st.session_state["current_feed"] = feed.entries[:10]

        if "current_feed" in st.session_state:
            for i, entry in enumerate(st.session_state["current_feed"]):
                with st.expander(f"📌 {entry.title}"):
                    st.write(f"🔗 [元記事を読む]({entry.link})")
                    
                    # 翻訳ボタン
                    if st.button("日本語に翻訳", key=f"tr_{i}"):
                        with st.spinner("翻訳中..."):
                            translated_title = translate_text(entry.title, st.secrets["deepl_api_key"])
                            st.success(f"【タイトル】{translated_title}")
                            if 'summary' in entry:
                                translated_body = translate_text(entry.summary[:300], st.secrets["deepl_api_key"])
                                st.write(translated_body)

                    # 保存ボタン
                    if st.button("この記事を保存する", key=f"save_{i}"):
                        article_data = {"title": entry.title, "link": entry.link}
                        if article_data not in st.session_state["saved_articles"]:
                            st.session_state["saved_articles"].append(article_data)
                            st.toast("記事を保存しました！")

    with tab2:
        st.header("保存した記事")
        if not st.session_state["saved_articles"]:
            st.write("保存された記事はありません。")
        else:
            for j, article in enumerate(st.session_state["saved_articles"]):
                st.write(f"・[{article['title']}]({article['link']})")
                if st.button("削除", key=f"del_{j}"):
                    st.session_state["saved_articles"].pop(j)
                    st.rerun()
