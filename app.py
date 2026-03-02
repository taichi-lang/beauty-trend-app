import streamlit as st
import feedparser
import requests
import re

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

# --- インスタ構成案作成 ---
def generate_insta_plan(title_ja, summary_ja):
    plan = f"""
✨【インスタ4枚構成案】✨

■1枚目（表紙：悩みに刺す！）
「海外でバズり散らかしてる〇〇が凄すぎた...」

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

# --- RSS取得（一般的なブラウザからのアクセスに偽装） ---
def fetch_rss(url):
    try:
        headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'}
        res = requests.get(url, headers=headers, timeout=10)
        return feedparser.parse(res.content)
    except Exception:
        return feedparser.parse(url)

# --- 余計なHTMLタグ（<br>や<b>など）を綺麗に消す関数 ---
def clean_html(raw_html):
    cleanr = re.compile('<.*?>')
    return re.sub(cleanr, '', raw_html)

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

    tab_main, tab_saved = st.tabs(["🔍 最新トレンド検索", "📁 保存済み・投稿案"])

    with tab_main:
        region_tabs = st.tabs(["🇰🇷 韓国", "🇯🇵 日本", "🌍 それ以外（海外）"])

        # 🚀【超安定版】Google News RSSを活用した最強のソースリスト
        sources = {
            "🇰🇷 韓国": {
                "韓国コスメトレンド速報": "https://news.google.com/rss/search?q=韓国コスメ+OR+K-Beauty+OR+韓国美容+when:7d&hl=ja&gl=JP&ceid=JP:ja",
                "Soompi (Beauty & Style)": "https://www.soompi.com/category/style/feed"
            },
            "🇯🇵 日本": {
                "PR TIMES (美容・コスメ新商品)": "https://news.google.com/rss/search?q=site:prtimes.jp+コスメ+OR+スキンケア+OR+美容液+when:7d&hl=ja&gl=JP&ceid=JP:ja",
                "WWDJAPAN (Beauty)": "https://www.wwdjapan.com/category/beauty/feed"
            },
            "🌍 それ以外（海外）": {
                "Allure (全米No.1美容誌)": "https://www.allure.com/feed/rss",
                "海外美容誌まとめ (Byrdie / Cosmo)": "https://news.google.com/rss/search?q=skincare+OR+makeup+OR+cosmetics+site:byrdie.com+OR+site:cosmopolitan.com+when:7d&hl=en-US&gl=US&ceid=US:en",
                "海外SNSトレンド (TikTok / Sephora)": "https://news.google.com/rss/search?q=Sephora+OR+beautytok+OR+makeup+trend+when:7d&hl=en-US&gl=US&ceid=US:en"
            }
        }

        for i, region in enumerate(sources.keys()):
            with region_tabs[i]:
                selected_source = st.selectbox(f"{region}の情報源を選択", list(sources[region].keys()), key=f"source_{i}")
                
                if st.button(f"📰 {selected_source} の最新記事を取得", key=f"btn_{i}"):
                    with st.spinner("安全なルートで記事を読み込み中..."):
                        feed = fetch_rss(sources[region][selected_source])
                        
                        if feed and feed.entries:
                            st.session_state["current_entries"] = feed.entries[:15]
                            st.success(f"最新の美容記事を {len(st.session_state['current_entries'])} 件取得しました！👇")
                        else:
                            st.error("サイト側でアクセスがブロックされているか、記事がありません。")

        st.divider()

        if "current_entries" in st.session_state:
            st.subheader("📋 取得した美容記事一覧")
            for j, entry in enumerate(st.session_state["current_entries"]):
                # タイトルを綺麗にして表示
                clean_title = clean_html(entry.title)
                
                with st.expander(f"📌 {clean_title}"):
                    st.write(f"🔗 [元記事をブラウザで開く]({entry.link})")

                    if st.button("🇯🇵 日本語解析＆台本作成", key=f"tr_{j}"):
                        with st.spinner("翻訳＆構成案を作成中..."):
                            t_title = translate_text(clean_title, st.secrets["deepl_api_key"])
                            
                            raw_text = entry.get('summary', '') or entry.get('description', '')
                            clean_summary = clean_html(raw_text)
                            t_body = translate_text(clean_summary[:500], st.secrets["deepl_api_key"])

                            st.success(t_title)
                            st.session_state[f"plan_{j}"] = generate_insta_plan(t_title, t_body)

                    if f"plan_{j}" in st.session_state:
                        st.text_area("そのまま使える投稿案", st.session_state[f"plan_{j}"], height=250)
                        if st.button("💾 この記事を保存", key=f"save_{j}"):
                            article_data = {"title": clean_title, "plan": st.session_state[f"plan_{j}"], "link": entry.link}
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
