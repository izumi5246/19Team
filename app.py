import streamlit as st
import json
from crawler import crawl_url
from search_fulltext import search_fulltext

# ---------------------------------------------------------
# ページ設定
# ---------------------------------------------------------
st.set_page_config(page_title="Tech0 Search v0.2", layout="wide")
st.title("PROJECT ZERO – 社内チャレンジ検索エンジン【全文検索対応】")

# ---------------------------------------------------------
# JSON 読み込み / 保存
# ---------------------------------------------------------
@st.cache_data
def load_pages():
    try:
        with open("pages.json", "r", encoding="utf-8") as f:
            return json.load(f)
    except:
        return []

def save_pages(pages):
    with open("pages.json", "w", encoding="utf-8") as f:
        json.dump(pages, f, ensure_ascii=False, indent=2)

pages = load_pages()

# ---------------------------------------------------------
# タブ
# ---------------------------------------------------------
tab1, tab2, tab3 = st.tabs(["🔎 全文検索", "🕷️ URLクロール", "📚 登録済みページ一覧"])

# =========================================================
# 🔎 ① 全文検索タブ
# =========================================================
with tab1:
    st.subheader("全文検索（タイトル・説明・本文・キーワード）")

    query = st.text_input("検索キーワードを入力")

    if query:
        results = search_fulltext(query, pages)
        st.write(f"検索結果：{len(results)} 件")

        for r in results:
            with st.container():
                st.markdown(f"### [{r['title']}]({r['url']})")
                st.write(f"**スコア**: {r['match_count']}")
                st.write(f"**プレビュー**: {r['preview']}")
                st.markdown("---")

# =========================================================
# 🕷️ ② URLクロールタブ（単体 & 一括）
# =========================================================
with tab2:
    st.subheader("単体クロール")

    url = st.text_input("URL を入力してください")

    if st.button("クロールを実行"):
        result = crawl_url(url)

        if result["crawl_status"] == "success":
            st.success("クロール成功！")
            st.write("### タイトル")
            st.write(result["title"])

            st.write("### 説明")
            st.write(result["description"])

            st.write("### 本文（先頭500文字）")
            st.write(result["full_text"][:500])

            st.write("### リンク一覧")
            st.write(result["links"])

            # 保存
            pages.append(result)
            save_pages(pages)
            st.cache_data.clear()
            st.info("pages.json に保存しました。")
        else:
            st.error(f"クロール失敗: {result.get('error')}")

    # -------------------------
    # 一括クロール
    # -------------------------
    st.subheader("一括クロール")

    urls_text = st.text_area("複数URLを改行で入力してください")

    if st.button("一括クロールを実行"):
        urls = [u.strip() for u in urls_text.split("\n") if u.strip()]
        results = []

        for u in urls:
            r = crawl_url(u)
            results.append(r)

            # 成功したものだけ保存
            if r["crawl_status"] == "success":
                pages.append(r)

        save_pages(pages)
        st.cache_data.clear()

        st.success("一括クロール完了！")
        st.table([
            {"URL": r["url"], "ステータス": r["crawl_status"], "タイトル": r.get("title", "")}
            for r in results
        ])

# =========================================================
# 📚 ③ 登録済みページ一覧
# =========================================================
with tab3:
    st.subheader("登録済みページ一覧")

    if len(pages) == 0:
        st.info("まだ登録されたページはありません。")
    else:
        for p in pages:
            with st.expander(p["title"]):
                st.write(f"**URL**: {p['url']}")
                st.write(f"**説明**: {p['description']}")
                st.write(f"**キーワード**: {', '.join(p['keywords'])}")
                st.write(f"**文字数**: {p.get('word_count', 'N/A')}")
                st.write(f"**クロール日時**: {p.get('crawled_at', 'N/A')}")