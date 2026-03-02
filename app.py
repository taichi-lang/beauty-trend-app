import streamlit as st
import feedparser
import requests
from rembg import remove
from PIL import Image
from io import BytesIO

# --- ページ設定 ---
st.set_page_config(page_title="Trend Beauty Lab.jp", page_icon="💄", layout="centered")

# --- 翻訳関数 ---
def translate_text(text, api_key):
    try:
        url = "https://api-free.deepl.com/v2/translate"
        headers = {"Authorization": f"DeepL-Auth-Key {api_key}"}
        data = {"text": [text], "target_lang": "JA"}
        response = requests.post(url, headers=headers, data=data, timeout=10)
        if response.status_code == 200:
            return response.json()["translations"][0]["text"]
        return f"翻訳エラー: {response.status_code}"
    except:
        return "通信エラーが発生しました"

# --- 背景削除関数 ---
def remove_bg(image_url):
    try:
        response = requests.get(image_url, timeout=10)
        img = Image.open(BytesIO(response.content))
        return remove(img)
    except Exception:
        return None

# --- インスタ構成案作成 ---
def generate_insta_plan(title_ja, summary_ja):
    plan = f"""
✨【インスタ4枚構成案】✨

■1枚目（表紙：悩みに刺す！）
「海外でバズり散らかしてる〇〇が凄すぎた...」
（小文字：英語の一次情報から徹底解説）

■2枚目（何がすごいの？）
【特徴】{title_ja}
・注目のポイント：{summary_ja[:60]}...

■3枚目（成分・使い心地）
・「{summary_ja[60:120]}...」という評価
・テクスチャーや香りの特徴

■4枚目（結論：どうすればいい？）
・こんな人におすすめ！
・日本からは〇〇で買える

📌 ハッシュタグ
#海外コスメ #韓国コスメ #日本未上陸 #トレンド美容 #trend_beauty_lab
    """
    return plan

# --- パスワード認証 ---
if "password_correct" not in st.session_state:
    st.session_state["password_correct"] = False

if not st.session_state["password_correct"]:
    st.title("Trend Beauty Lab ログイン")
    pwd = st.text_input("パスワードを入力", type="password")
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

    # 大枠のタブ（検索と保存リスト）
    tab_main, tab_saved = st.tabs(["🔍 最新トレンド検索", "📁 保存済み・投稿案"])

    with tab_main:
        # --- 地域のタブ分け ---
        region_tabs = st.tabs(["🇰🇷 韓国", "🇯🇵 日本", "🌍 それ以外（海外）"])

        sources = {
            "🇰🇷 韓国": {
                "K-pop Herald (Beauty)": "http://www.koreaherald.com/common/rss_xml.php?ct=1001",
                "Soompi (Style)": "https://www.soompi.com/feed"
            },
            "🇯🇵 日本": {
                "PR TIMES (美容)": "https://prtimes.jp/main/html/searchrlp/ct_id/14/rss",
                "WWDJAPAN (Beauty)": "https://www.wwdjapan.com/category/beauty/feed"
            },
            "🌍 それ以外（海外）": {
                "Allure (全米No.1美容誌)": "https://www.allure.com/feed/rss",
                "Byrdie (成分/トレンド)": "https://www.byrdie.com/rss",
                "Cosmopolitan Beauty": "https://www.cosmopolitan.com/feeds/beauty"
            }
        }

        # 各地域タブの中身を生成
        for i, region in enumerate(sources.keys()):
            with region_tabs[i]:
                selected_source = st.selectbox(f"{region}の情報源を選択", list(sources[region].keys()), key=f"source_{i}")
                
                if st.button(f"📰 {selected_source} の最新記事を取得", key=f"btn_{i}"):
                    with st.spinner("記事を読み込み中..."):
                        feed = feedparser.parse(sources[region][selected_source])
                        if feed.entries:
                            st.session_state["current_entries"] = feed.entries[:10]
                            st.success(f"{len(st.session_state['current_entries'])}件の記事を取得しました！下にスクロールしてください👇")
                        else:
                            st.error("記事が見つかりませんでした。別のソースをお試しください。")

        st.divider()

        # --- 取得した記事の表示エリア ---
        if "current_entries" in st.session_state:
            st.subheader("📋 取得した記事一覧")
            for j, entry in enumerate(st.session_state["current_entries"]):
                with st.expander(f"📌 {entry.title}"):
                    st.write(f"🔗 [元記事をブラウザで開く]({entry.link})")

                    # 画像URLを探す処理（RSSの仕様の違いを吸収）
                    img_url = ""
                    if 'links' in entry:
                        for link in entry.links:
                            if 'image' in link.get('type', ''):
                                img_url = link.get('href')
                    if not img_url and 'media_content' in entry:
                        img_url = entry.media_content[0]['url']

                    # ボタンを横並びに配置
                    col1, col2 = st.columns(2)

                    with col1:
                        if st.button("🇯🇵 日本語解析＆台本作成", key=f"tr_{j}"):
                            with st.spinner("翻訳＆構成案を作成中..."):
                                t_title = translate_text(entry.title, st.secrets["deepl_api_key"])
                                raw_text = entry.get('summary', '') or entry.get('description', '')
                                t_body = translate_text(raw_text[:500], st.secrets["deepl_api_key"])

                                st.success(t_title)
                                st.session_state[f"plan_{j}"] = generate_insta_plan(t_title, t_body)

                    with col2:
                        if img_url and st.button("✂️ 背景を消して画像保存", key=f"bg_{j}"):
                            with st.spinner("AIが背景を削除中...（数秒かかります）"):
                                no_bg_img = remove_bg(img_url)
                                if no_bg_img:
                                    st.image(no_bg_img, caption="背景削除完了！")
                                    buf = BytesIO()
                                    no_bg_img.save(buf, format="PNG")
                                    st.download_button("📥 透過画像をダウンロード", buf.getvalue(), f"item_{j}.png", "image/png", key=f"dl_{j}")
                                else:
                                    st.warning("画像の取得・透過に失敗しました（サイト側で直リンクが禁止されている可能性があります）。")

                    # 構成案が表示されたら「保存ボタン」を出す
                    if f"plan_{j}" in st.session_state:
                        st.text_area("そのまま使える投稿案", st.session_state[f"plan_{j}"], height=250)
                        if st.button("💾 この記事を保存", key=f"save_{j}"):
                            article_data = {"title": entry.title, "plan": st.session_state[f"plan_{j}"], "link": entry.link}
                            # 重複保存を防ぐ
                            if article_data not in st.session_state["saved_articles"]:
                                st.session_state["saved_articles"].append(article_data)
                                st.toast("保存しました！")

    with tab_saved:
        st.header("📁 保存済みリスト")
        if not st.session_state["saved_articles"]:
            st.info("まだ保存された記事はありません。")
        for k, article in enumerate(st.session_state["saved_articles"]):
            with st.expander(f"✅ {article['title']}"):
                st.write(article['plan'])
                st.write(f"🔗 [元記事]({article['link']})")
                if st.button("🗑 削除", key=f"del_{k}"):
                    st.session_state["saved_articles"].pop(k)
                    st.rerun()
