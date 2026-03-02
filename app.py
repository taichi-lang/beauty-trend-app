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

# --- 余計なHTMLタグを綺麗に消す関数 ---
def clean_html(raw_html):
    cleanr = re.compile('<.*?>')
    return re.sub(cleanr, '', raw_html)

# --- ① インスタ画像＆フィード投稿用 ---
def generate_insta_plan(title_ja, summary_ja):
    plan = f"""
✨【インスタ画像 4枚構成案 ＆ キャプション】✨

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

📝【そのまま使えるキャプション（文章）】
海外の美容オタクの間で争奪戦になってるこれ、もうチェックした？👀
実はこれ、{summary_ja[:40]}...って言われていて、SNSでもバズりまくってるんです！
日本にはまだ本格上陸していないから、今のうちに保存してトレンドを先取りしてね✨

📌 ハッシュタグ
#海外コスメ #韓国コスメ #日本未上陸 #トレンド美容 #trend_beauty_lab
    """
    return plan

# --- ② ショート動画＆リール用 台本 ---
def generate_short_video_script(title_ja, summary_ja):
    script = f"""
🎬【ショート動画用 台本＆テロップ案】🎬

⏳ 0:00〜0:02【フック：強烈な共感・煽り】
[テロップ大] 「海外でバズり散らかしてるコレ、知ってる？」
[音声/セリフ] {title_ja}！今、海外のSNSでめちゃくちゃ話題になってるんです！

⏳ 0:02〜0:10【展開：課題と特徴】
[テロップ中] 「何がすごいの？」
[音声/セリフ] 実はこれ、{summary_ja[:40]}...って言われていて、美容オタクの間で争奪戦になってるらしい。

⏳ 0:10〜0:20【本題：成分やリアルな声】
[テロップ中] 「プロも大絶賛」
[音声/セリフ] {summary_ja[40:100]}...という感じで、テクスチャーも最高みたい。

⏳ 0:20〜0:30【CTA：オチと保存誘導】
[テロップ大] 「日本上陸前に保存して！」
[音声/セリフ] まだ日本には上陸してないから、今のうちに保存してトレンドを先取りしてね！
    """
    return script

# --- RSS取得（ブロック回避用） ---
def fetch_rss(url):
    try:
        headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'}
        res = requests.get(url, headers=headers, timeout=10)
        return feedparser.parse(res.content)
    except Exception:
        return feedparser.parse(url)

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
                clean_title = clean_html(entry.title)
                
                with st.expander(f"📌 {clean_title}"):
                    st.write(f"🔗 [元記事をブラウザで開く]({entry.link})")

                    # ボタンを横に2つ並べる
                    col1, col2 = st.columns(2)

                    with col1:
                        if st.button("📸 画像投稿用を作成", key=f"tr_ig_{j}"):
                            with st.spinner("インスタ用の構成とキャプションを作成中..."):
                                t_title = translate_text(clean_title, st.secrets["deepl_api_key"])
                                raw_text = entry.get('summary', '') or entry.get('description', '')
                                clean_summary = clean_html(raw_text)
                                t_body = translate_text(clean_summary[:500], st.secrets["deepl_api_key"])

                                st.success("インスタ投稿用の構成を作成しました！")
                                st.session_state[f"plan_{j}"] = generate_insta_plan(t_title, t_body)

                    with col2:
                        if st.button("🎥 ショート動画用を作成", key=f"tr_sv_{j}"):
                            with st.spinner("動画の台本・テロップを作成中..."):
                                t_title = translate_text(clean_title, st.secrets["deepl_api_key"])
                                raw_text = entry.get('summary', '') or entry.get('description', '')
                                clean_summary = clean_html(raw_text)
                                t_body = translate_text(clean_summary[:500], st.secrets["deepl_api_key"])

                                st.success("ショート動画用の台本を作成しました！")
                                st.session_state[f"plan_{j}"] = generate_short_video_script(t_title, t_body)

                    # 作成された構成案・台本を表示して保存ボタンを出す
                    if f"plan_{j}" in st.session_state:
                        st.text_area("そのままコピペして使えるメモ", st.session_state[f"plan_{j}"], height=350)
                        if st.button("💾 この内容を保存", key=f"save_{j}"):
                            article_data = {"title": clean_title, "plan": st.session_state[f"plan_{j}"], "link": entry.link}
                            if article_data not in st.session_state["saved_articles"]:
                                st.session_state["saved_articles"].append(article_data)
                                st.toast("保存リストに追加しました！")

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
