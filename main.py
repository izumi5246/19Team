# ① ライブラリのインポート
import streamlit as st
import json
from search import search_pages, highlight_match 
import re

def save_to_json(url, title):
    # ① 現在のファイルを読み込む
    try:
        with open('pages.json', 'r', encoding='utf-8') as f:
            current_pages = json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        # ファイルがない、または空の場合のバックアップ
        current_pages = []

    # ② 新しいデータを作成
    # IDは現在の件数+1、キーワードなどは空のリストで初期化します
    new_data = {
        "id": len(current_pages) + 1,
        "url": url,
        "title": title,
        "description": "（新規登録されたページ）",
        "keywords": [],
        "author": "ユーザー投稿",
        "created_at": "2026-03-22", # 現在の日付
        "category": "未分類"
    }

    # ③ リストに追加して上書き保存
    current_pages.append(new_data)
    with open('pages.json', 'w', encoding='utf-8') as f:
        json.dump(current_pages, f, indent=2, ensure_ascii=False)

st.title('Tech0 Search v0.1')
st.caption('PROJECT ZERO-新世代テック検索エンジン')

tab1, tab2, tab3 = st.tabs(['検索', '登録', '一覧'])

with tab1:
    st.subheader('🔍 キーワード検索')

    # 1. データの読み込み
    with open('pages.json', 'r', encoding='utf-8') as f:
        pages = json.load(f)

    # 2. 検索入力
    query = st.text_input('🔑 キーワードを入力')

    if query:
        # search.pyの関数でフィルタリング
        results = search_pages(query, pages)
        
        # 3. 検索結果の件数表示
        st.write(f"**検索結果: {len(results)} 件**")
        st.write("") # スペース用

        if results:
            for page in results:
                # 4. タイトルをリンク付きで表示
                # [タイトル](URL) の形式でMarkdownを書くとリンクになります
                st.markdown(f"### [{page['title']}]({page['url']}) 🔗")
                
                # 5. 説明文（ハイライト付き）
                highlighted_text = highlight_match(page['description'], query)
                st.markdown(highlighted_text, unsafe_allow_html=True)
                
                # 6. キーワードをタグ風に表示
                # リストを「, 」で繋いで表示
                tags = ", ".join(page['keywords'])
                st.caption(f"📁 {tags}")
                
                st.write("") # 項目間の余白
        else:
            st.info('該当する記事が見つかりませんでした。')
with tab2:
    st.subheader('🚀 新規ページ登録')

    with st.form(key='registration_form'):
        new_url = st.text_input('URL', placeholder='https://example.com')
        new_title = st.text_input('タイトル', placeholder='ページのタイトルを入力')
        submit_button = st.form_submit_button(label='登録する')

    if submit_button:
        if not new_url:
            st.error('URLは必須です')
        elif not new_title:
            st.error('タイトルは必須です')
        else:
            # --- ここで保存関数を呼び出す ---
            save_to_json(new_url, new_title)
            
            st.success('登録成功！「一覧」や「検索」タブに反映されます。')
            st.balloons()

with tab3:
    st.subheader('登録済みページ一覧')

    # データの読み込み
    with open('pages.json', 'r', encoding='utf-8') as f:
        all_pages = json.load(f)

    st.write(f"現在、合計 {len(all_pages)} 件のページが登録されています。")
    st.divider()

    # ループですべてのデータを表示
    for page in all_pages:
        # タイトルとURL
        st.markdown(f"### [{page['title']}]({page['url']})")
        
        # 説明文
        st.write(page['description'])
        
        # カテゴリや作成日のメタ情報
        col1, col2 = st.columns(2)
        with col1:
            st.caption(f"👤 投稿者: {page['author']}")
        with col2:
            st.caption(f"📅 登録日: {page.get('created_at', '不明')}")
        
        st.divider()