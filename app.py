import streamlit as st
import pandas as pd
import io

# 画面タイトルの設定
st.set_page_config(page_title="「こだわる」語義自動分類ツール", layout="centered")
st.title("🔍 「こだわる」用例 自動分類ツール")
st.write("BCCWJ等のコーパスデータ（「|」区切り・反転表記対応）から、「こだわる」の使われ方をA/B/C/Dに自動仕分けします。")

# --- 判定ロジック関数（反転・整形対応版） ---
def classify_text_string(text, complement=""):
    # 確実に文字列に変換し、すべての「|（縦棒）」と空白を除去する
    clean_text = str(text).replace('|', '').replace(' ', ' ').strip() if pd.notna(text) else ""
    clean_comp = str(complement).replace('|', '').replace(' ', ' ').strip() if (complement and pd.notna(complement)) else ""
    
    # 通常の結合文字列
    full_str = clean_text + " " + clean_comp
    
    # 反転表記に対応するため、文字列全体を反転したものも用意
    reversed_text = full_str[::-1]
    
    # 検索対象（通常＋反転をすべて結合）
    combined_search_target = full_str + " " + reversed_text
    
    # 【ステップ1】語義B：つかえる、障る（物理的・身体的障礙）
    b_keywords = ['鍔', '脇指', '横つ腹', '喉', 'ひっかかる', 'つかえる', 'るかえつ']
    if any(k in combined_search_target for k in b_keywords):
        return 'B（つかえる・障る）', '物理的・身体的障礙に関するキーワードを検出', clean_text
        
    # 【ステップ2】語義A：わずかなことにつけて文句を言う
    a_keywords = ['理屈', '文句', 'なんくせ', '言いがかり', '埒明けず', 'つくい', 'くちり']
    if any(k in combined_search_target for k in a_keywords):
        return 'A（文句を言う）', '理屈や言いがかりに関するキーワードを検出', clean_text
        
    # 【ステップ3】語義C：近代的用法（ネガティブ・拘泥）
    c_keywords = [
        '過去', '因習', '些細', '形式', '肩書', '立場', 'こだわりすぎ', 'こだわりてい', 
        '身動き', '拘泥', '囚われ', '縛られ', '否定的', 'ばかり', 
        'うりてぎてい', 'ぎてい', 'いきてい', 'りばか', 'れらばし', 'れわらゆ'
    ]
    if any(k in combined_search_target for k in c_keywords):
        return 'C（近代的用法・ネガティブ）', '否定的な執着や枠組み（因習・過去・形式・否定的等）を検出', clean_text
        
    # 【ステップ4】語義D：現代的用法（ポジティブ・追求）
    d_keywords = [
        '品質', '味', '素材', '本物', '住まい', 'デザイン', 'こだわりたい', 'こだわりを深め', 
        '追求', '厳選', '職人', '徹底', 'とことん',
        'いいたいわだこ', 'め深をりわだこ'
    ]
    if any(k in combined_search_target for k in d_keywords):
        return 'D（現代的用法・ポジティブ）', '肯定的な追求・品質重視に関するキーワードを検出', clean_text
        
    # 否定形で機能語化・包括的な使われ方をしている場合
    neg_check = ['こだわらない', 'こだわらず', 'ないわだこ', 'ずわだこ']
    if any(n in combined_search_target for n in neg_check) and any(k in combined_search_target for k in ['ジャンル', 'ブランド', 'メーカー', '性別', '年齢', 'ルンジャ', 'ドナルブ', 'カーメ', '別性', '齢年']):
        return 'D（現代的用法・包括的）', '制限を設けない包括的・機能語的表現を検出', clean_text

    # 該当ルールがない場合
    return '要手動確認（C/D判別）', '文脈依存（伝統・方法等）のため目視確認を推奨', clean_text


# --- タブの作成（① 直接入力、② ファイル一括処理） ---
tab1, tab2 = st.tabs(["✍️ 直接入力して判定", "📁 ファイル一括処理"])

# 【タブ1】直接入力モード
with tab1:
    st.subheader("文章を直接入力して検証する")
    user_text = st.text_area("「こだわる」を含む文例を入力してください（反転や|付きもOK）:", placeholder="例：自我の力弱い人だとか、自分の否定的な面にばかりこだわっている、など")
    user_complement = st.text_input("補語や対象があれば入力してください（任意）:", placeholder="例：面")
    
    if st.button("判定する", key="direct_button"):
        if user_text.strip() == "":
            st.warning("テキストを入力してください。")
        else:
            res_result, res_reason, cleaned = classify_text_string(user_text, user_complement)
            
            st.markdown("### 📌 判定結果")
            if "A" in res_result:
                st.error(f"**判定:** {res_result}")
            elif "B" in res_result:
                st.warning(f"**判定:** {res_result}")
            elif "C" in res_result:
                st.info(f"**判定:** {res_result}")
            elif "D" in res_result:
                st.success(f"**判定:** {res_result}")
            else:
                st.info(f"**判定:** {res_result}")
                
            st.write(f"**理由・メモ:** {res_reason}")
            st.text(f"【確認用】修正済みテキスト(|除去): {cleaned}")

# 【タブ2】ファイル一括処理モード
with tab2:
    uploaded_file = st.file_uploader("エクセルまたはCSVファイルをアップロード", type=["xlsx", "xls", "csv"])

    if uploaded_file is not None:
        try:
            if uploaded_file.name.endswith('.csv'):
                df = pd.read_csv(uploaded_file)
            else:
                df = pd.read_excel(uploaded_file)
                
            st.success("ファイルを正常に読み込みました。")
            st.subheader("📋 データのプレビュー")
            st.dataframe(df.head(5), use_container_width=True)
            
            columns = df.columns.tolist()
            st.subheader("⚙️ 判定対象の列を指定")
            
            text_column = st.selectbox("抽出テキスト（本文）の列を選択", options=columns)
            complement_column = st.selectbox("補語（対象）の列を選択（なければなし）", options=["なし"] + columns)
                
            if st.button("🚀 一括自動分類を実行する", key="file_button"):
                results = []
                for idx, row in df.iterrows():
                    t_val = row[text_column]
                    c_val = row[complement_column] if complement_column != "なし" else ""
                    res = classify_text_string(t_val, c_val)
                    results.append(res)
                
                df['判定結果'] = [r[0] for r in results]
                df['判定理由・メモ'] = [r[1] for r in results]
                df['整形済みテキスト(|除去)'] = [r[2] for r in results]
                
                st.subheader("📊 分類結果の集計")
                summary = df['判定結果'].value_counts()
                st.bar_chart(summary)
                
                st.subheader("📝 判定結果一覧")
                st.dataframe(df, use_container_width=True)
                
                output = io.BytesIO()
                with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
                    df.to_excel(writer, index=False, sheet_name='分類結果')
                processed_data = output.getvalue()
                
                st.download_button(
                    label="📥 分類結果（Excel）をダウンロード",
                    data=processed_data,
                    file_name="kodawaru_classified_result.xlsx",
                    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
                )
                
        except Exception as e:
            st.error(f"エラーが発生しました: {e}")
