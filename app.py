import streamlit as st
import feedparser
import requests

# --- ページ設定 ---
st.set_page_config(page_title="Trend Beauty Lab.jp", page_icon="💄")

# --- 翻訳関数 (最新のヘッダー認証方式) ---
def translate_text(text, api_key):
    try:
        url = "https://api-free.deepl.com/v2/translate"
        # 最新の仕様：APIキーは headers に入れる
        headers = {
            "Authorization": f"DeepL-Auth-Key {api_key}"
        }
        # テキストデータは data に入れる
        data = {
            "text": [text],
            "target_lang": "JA"
        }
        response = requests.post(url, headers=headers, data=data, timeout=10)
        
        if response.status_code == 200:
            return response.json()["translations"][0]["text"]
        else:
            return f"DeepLエラー ({response.status_code}): {response.text}"
    except Exception as e:
        return f"通信エラー: {e}"

# --- 以下、ログイン・メイン処理は前回と同じ ---
# (中略)

def create_insta_memo(title_ja, summary_ja):
    memo = f"""
【インスタ投稿用メモ】
■タイトル案
{title_ja}

■投稿のポイント
・海外で話題の最新トレンド！
・{summary_ja[:100]}...

■ハッシュタグ
#海外コスメ #海外トレンド美容 #trend_beauty_lab #日本未上陸
    """
    return memo

# --- パスワード認証 ---
if "password_correct" not in st.session_state:
    st.session_state["password_correct"] = False

if not st.session_state["password_correct"]:
    st.title("Trend Beauty Lab ログイン")
    pwd = st.text_input("パスワードを入力してください", type="password")
    if st.button("ログイン"):
        if pwd == st.secrets["password"]:
            st.session_state["password_correct"] = True
            st.rerun()
        else:
            st.error("パスワードが違います")
else:
    # --- メイン画面 ---
    st.title("💄 Trend Beauty Lab.jp")
    
    if "saved_articles" not in st.session_state:
        st.session_state["saved_articles"] = []

    tab1, tab2 = st.tabs(["最新トレンド検索", "保存済み記事/台本"])

    with tab1:
        sources = {
            "Allure (全米No.1美容誌)": "https://www.allure.com/feed/rss",
            "Byrdie (成分/トレンド)": "https://www.byrdie.com/rss",
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
                    
                    if st.button("日本語訳 ＆ 台本案作成", key=f"tr_{i}"):
                        with st.spinner("翻訳中..."):
                            t_title = translate_text(entry.title, st.secrets["deepl_api_key"])
                            t_body = translate_text(entry.summary[:300], st.secrets["deepl_api_key"]) if 'summary' in entry else "詳細はリンク先へ"
                            
                            st.subheader("🇯🇵 日本語要約")
                            st.success(t_title)
                            st.write(t_body)
                            
                            st.session_state[f"memo_{i}"] = create_insta_memo(t_title, t_body)

                    if f"memo_{i}" in st.session_state:
                        st.text_area("そのままコピペ用メモ", st.session_state[f"memo_{i}"], height=150)
                        if st.button("この記事を保存リストへ", key=f"save_{i}"):
                            article_data = {"title": entry.title, "memo": st.session_state[f"memo_{i}"], "link": entry.link}
                            st.session_state["saved_articles"].append(article_data)
                            st.toast("保存しました！")

    with tab2:
        st.header("保存済みリスト")
        for j, article in enumerate(st.session_state["saved_articles"]):
            with st.expander(f"✅ {article['title']}"):
                st.write(article['memo'])
                st.write(f"🔗 [元記事]({article['link']})")
                if st.button("削除", key=f"del_{j}"):
                    st.session_state["saved_articles"].pop(j)
                    st.rerun()
