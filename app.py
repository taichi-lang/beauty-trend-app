import streamlit as st
import feedparser
import requests

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

# --- RSS取得（ブロック回避用：iPhoneからのアクセスを偽装） ---
def fetch_rss(url):
    headers = {
        'User-Agent': 'Mozilla/5.0 (iPhone; CPU iPhone OS 16_0 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/16.0 Mobile/15E148 Safari/604.1'
    }
    try:
        res = requests.get(url, headers=headers, timeout=10)
        return feedparser.parse(res.content)
    except Exception:
        return None

# --- 美容記事の「徹底」フィルタリング ---
def is_beauty_article(entry):
    text = (entry.title + " " + entry.get('summary', '')).lower()
    
    # ❌ 絶対に弾くNGキーワード（エンタメ、恋愛、政治、単なるファッションなど）
    ng_words = [
        "movie", "music", "politics", "sports", "film", "k-pop", "runway", "sneaker", "relationship", "dating",
        "映画", "音楽", "政治", "スポーツ", "スニーカー", "エンタメ", "ドラマ", "熱愛", "結婚", "インタビュー", "俳優", "女優"
    ]
    for word in ng_words:
        if word in text:
            return False # 1つでも入っていれば即除外
            
    # ⭕️ 必須の美容キーワード（これが1つも入っていなければ美容記事ではないとみなして弾く）
    ok_words = [
        "beauty", "makeup", "skincare", "cosmetics", "hair", "skin", "lip", "nail",
        "fragrance", "perfume", "serum", "lotion", "moisturizer", "anti-aging", "sunscreen", "cleanser",
        "美容", "メイク", "スキンケア", "コスメ", "ヘアケア", "肌", "リップ", "ネイル",
        "香水", "美容液", "化粧水", "保湿", "エイジングケア", "化粧品", "日焼け止め", "洗顔"
    ]
    for word in ok_words:
        if word in text:
            return True # 美容用語が入っていれば合格
            
    return False # 美容用語が見当たらなければ除外

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

        # 読み込めないURLの修正と代替メディアの追加
        sources = {
            "🇰🇷 韓国": {
                "Soompi (Style & Beauty)": "https://www.soompi.com/category/style/feed",
                "K-pop Herald (Beauty)": "http://www.koreaherald.com/common/rss_xml.php?ct=1001"
            },
            "🇯🇵 日本": {
                "PR TIMES (美容・コスメ専用)": "https://prtimes.jp/tv/14/rss.xml",
                "WWDJAPAN (Beauty)": "https://www.wwdjapan.com/category/beauty/feed"
            },
            "🌍 それ以外（海外）": {
                "Allure (全米No.1美容誌)": "https://www.allure.com/feed/rss",
                "Vogue Beauty (US)": "https://www.vogue.com/feed/beauty/rss",
                "Byrdie (成分/トレンド)": "https://www.byrdie.com/rss"
            }
        }

        for i, region in enumerate(sources.keys()):
            with region_tabs[i]:
                selected_source = st.selectbox(f"{region}の情報源を選択", list(sources[region].keys()), key=f"source_{i}")
                
                if st.button(f"📰 {selected_source} の最新記事を取得", key=f"btn_{i}"):
                    with st.spinner("記事を読み込み、不要な情報を排除中..."):
                        # ブロック回避関数でRSSを取得
                        feed = fetch_rss(sources[region][selected_source])
                        
                        if feed and feed.entries:
                            # 取得した記事を、先ほどの強力なフィルターにかける
                            filtered_entries = [e for e in feed.entries if is_beauty_article(e)]
                            
                            if filtered_entries:
                                st.session_state["current_entries"] = filtered_entries[:15]
                                st.success(f"純粋な美容記事だけを {len(filtered_entries)} 件抽出しました！👇")
                            else:
                                st.warning("取得した中に、純粋な美容関連記事が見つかりませんでした（エンタメ等を除外したため）。")
                        else:
                            st.error("サイト側でアクセスがブロックされているか、記事がありません。")

        st.divider()

        if "current_entries" in st.session_state:
            st.subheader("📋 厳選された美容記事一覧")
            for j, entry in enumerate(st.session_state["current_entries"]):
                with st.expander(f"📌 {entry.title}"):
                    st.write(f"🔗 [元記事をブラウザで開く]({entry.link})")

                    if st.button("🇯🇵 日本語解析＆台本作成", key=f"tr_{j}"):
                        with st.spinner("翻訳＆構成案を作成中..."):
                            t_title = translate_text(entry.title, st.secrets["deepl_api_key"])
                            raw_text = entry.get('summary', '') or entry.get('description', '')
                            t_body = translate_text(raw_text[:500], st.secrets["deepl_api_key"])

                            st.success(t_title)
                            st.session_state[f"plan_{j}"] = generate_insta_plan(t_title, t_body)

                    if f"plan_{j}" in st.session_state:
                        st.text_area("そのまま使える投稿案", st.session_state[f"plan_{j}"], height=250)
                        if st.button("💾 この記事を保存", key=f"save_{j}"):
                            article_data = {"title": entry.title, "plan": st.session_state[f"plan_{j}"], "link": entry.link}
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
