import streamlit as st
import pandas as pd
import io

# 画面タイトルの設定
st.set_page_config(page_title="「こだわる」語義自動分類ツール", layout="centered")
st.title("🔍 「こだわる」用例 自動分類ツール")
st.write("BCCWJ等のコーパスデータから、「こだわる」の使われ方をA/B/C/Dに自動仕分けします。")

# --- 判定ロジック関数 ---
def classify_text_string(text, complement=""):
    # 欠損値対策と、「|（縦棒）」・全角半角スペースの完全除去
    clean_text = str(text).replace('|', '').replace(' ', ' ').strip() if pd.notna(text) else ""
    clean_comp = str(complement).replace('|', '').replace(' ', ' ').strip() if (complement and pd.notna(complement)) else ""
    
    # 検索対象文字列（本文＋補語）と、反転表記用の文字列を作成
    full_str = clean_text + " " + clean_comp
    reversed_str = full_str[::-1]
    search_target = full_str + " " + reversed_str

    # 【ステップ1】語義B：つかえる、障る（物理的・身体的障礙）
    b_keywords = ['鍔', '脇指', '横つ腹', '喉', 'ひっかかる', 'つかえる', 'かかる', '障る']
    if any(k in search_target for k in b_keywords):
        return 'B（つかえる・障る）', '物理的・身体的障礙に関するキーワードを検出', clean_text
        
    # 【ステップ2】語義A：わずかなことに理屈をつけて文句を言う
    a_keywords = ['理屈', '文句', 'なんくせ', '言いがかり', '埒明けず', '難癖']
    if any(k in search_target for k in a_keywords):
        return 'A（文句を言う）', '理屈や言いがかりに関するキーワードを検出', clean_text
        
    # 【ステップ3】語義D：現代的用法（ポジティブ・追求、および否定形の包括表現）
    # まず「こだわらない」「こだわらず」といった包括的用法をチェック
    if ('こだわらない' in clean_text or 'こだわらず' in clean_text or 'ないわだこ' in reversed_str or 'ずわだこ' in reversed_str):
        if any(k in search_target for k in ['ジャンル', 'ブランド', 'メーカー', '性別', '年齢', '国籍', '問わず', '関係なく', '一律']):
            return 'D（現代的用法・包括的）', '制限を設けない包括的・機能語的表現を検出', clean_text

    # ポジティブな追求・品質重視に関するキーワード（語義D）
    d_keywords = [
        '品質', '味', '素材', '本物', '住まい', 'デザイン', 'こだわりたい', 'こだわりを深め', 
        '追求', '厳選', '職人', '徹底', 'とことん', '美味し', 'おいし', '上質', '独自', '洗練'
    ]
    if any(k in search_target for k in d_keywords):
        return 'D（現代的用法・ポジティブ）', '肯定的な追求・品質重視に関するキーワードを検出', clean_text

    # 【ステップ4】語義C：近代的用法（ネガティブ・拘泥・囚われ）
    # 上記のDに該当せず、否定的な文脈や枠組み・執着を示すキーワードがある場合
    c_keywords = [
        '過去', '因習', '些細', '形式', '肩書', '立場', 'こだわりすぎ', '身動き', 
        '拘泥', '囚われ', '縛られ', '否定的', 'ばかり', 'つまらぬ', '不要な', '悪癖',
        '泥拘', 'われ囚'
    ]
    if any(k in search_target for k in c_keywords) or 'こだわっ' in clean_text:
        # 「こだわり」が単体で、特にポジティブ要素がない場合は基本C（ネガティブ・執着）へ寄せる
        return 'C（近代的用法・ネガティブ）', '否定的な執着や枠組み（因習・過去・形式・拘泥等）を検出', clean_text

    # どのキーワードにも引っかからない場合のみ手動確認
    return '要手動確認（C/D判別）', '明確なポジティブ・ネガティブの判定キーワードが不足しているため目視確認を推奨', clean_text


# --- タブの作成（① 直接入力、② ファイル一括処理） ---
tab1, tab2 = st.tabs(["✍️ 直接入力して判定", "📁 ファイル一括処理"])

# 【タブ1】直接入力モード
with tab1:
    st.subheader("文章を直接入力して検証する")
    user_text = st.text_area("「こだわる」を含む文例を入力してください:", placeholder="例：自我の力弱い人だとか、自分の否定的な面にばかりこだわっている、など")
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
            st.text(f"【確認用】整形済みテキスト: {cleaned}")

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
                df['整形済みテキスト'] = [r[2] for r in results]
                
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
