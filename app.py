import streamlit as st
import feedparser

# --- ページ設定 ---
st.set_page_config(page_title="Trend Beauty Lab", page_icon="💄", layout="centered")

# --- ログイン機能 ---
def check_password():
    """パスワードが正しければTrueを返す"""
    def password_entered():
        if st.session_state["password"] == st.secrets["password"]:
            st.session_state["password_correct"] = True
            del st.session_state["password"]  # セキュリティのため入力パスワードを削除
        else:
            st.session_state["password_correct"] = False

    if "password_correct" not in st.session_state:
        # 初回アクセス時：パスワード入力欄を表示
        st.text_input("パスワードを入力してください", type="password", on_change=password_entered, key="password")
        return False
    elif not st.session_state["password_correct"]:
        # パスワードを間違えた時
        st.text_input("パスワードを入力してください", type="password", on_change=password_entered, key="password")
        st.error("😕 パスワードが間違っています")
        return False
    return True

# --- メイン画面（ログイン成功時のみ表示） ---
if check_password():
    st.title("💄 Trend Beauty Lab - 情報収集ツール")
    st.write("海外の最新美容トレンドを取得します。")

    # サンプルとしてVogue BeautyのRSSから情報を取得
    rss_url = "https://www.vogue.com/feed/beauty/rss"
    
    if st.button("最新ニュースを取得する"):
        with st.spinner("記事を取得中..."):
            feed = feedparser.parse(rss_url)
            
            if feed.entries:
                for entry in feed.entries[:5]:  # 最新5件を表示
                    st.subheader(entry.title)
                    st.write(f"🔗 [元記事を読む]({entry.link})")
                    st.write("---")
            else:
                st.warning("記事が取得できませんでした。")