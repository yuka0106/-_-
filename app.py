import streamlit as st
import pandas as pd
import io

# 画面タイトルの設定
st.set_page_config(page_title="「こだわる」語義自動分類ツール", layout="centered")
st.title("🔍 「こだわる」用例 自動分類ツール")
st.write("BCCWJ等のコーパスデータから、「こだわる」の使われ方をA/B/C/Dに自動・手動で仕分けします。")

# --- 判定ロジック関数 ---
def classify_text_string(combined_text):
    clean_text = str(combined_text).replace('|', '').replace(' ', ' ').strip() if pd.notna(combined_text) else ""
    reversed_str = clean_text[::-1]
    search_target = clean_text + " " + reversed_str

    # 【ステップ1】語義B：つかえる、障る（物理的・身体的障礙）
    b_keywords = [
        '鍔', '脇指', '横つ腹', '喉', 'ひっかかる', 'つかえる', 'かかる', '障る',
        '引っかかる', '引っ掛かる', '支障'
    ]
    if any(k in search_target for k in b_keywords):
        return 'B（つかえる・障る）', '物理的・身体的障礙に関するキーワードを検出', clean_text

    # 【ステップ2】語義A：わずかなことに理屈をつけて文句を言う
    a_keywords = [
        '理屈', '文句', 'なんくせ', '言いがかり', '埒明けず', '難癖', '不平', '不満', '愚痴', '小言'
    ]
    if any(k in search_target for k in a_keywords):
        return 'A（文句を言う）', '理屈や言いがかりに関するキーワードを検出', clean_text

    # 【ステップ3】語義D：現代的用法（ポジティブ・追求、および否定形の包括表現）
    if ('こだわらない' in clean_text or 'こだわらず' in clean_text or 'ないわだこ' in reversed_str or 'ずわだこ' in reversed_str):
        if any(k in search_target for k in [
            'ジャンル', 'ブランド', 'メーカー', '性別', '年齢', '国籍', '問わず',
            '関係なく', '一律', '種類', '形式', '方法', '場所', '時間'
        ]):
            return 'D（現代的用法・包括的）', '制限を設けない包括的・機能語的表現を検出', clean_text

    d_keywords = [
        '品質', '味', '素材', '食材', '本物', '住まい', 'デザイン', 'こだわりたい', 'こだわりを深め',
        '追求', '追及', '厳選', '職人', '徹底', 'とことん', '美味し', 'おいし', '上質', '独自',
        '洗練', '絶品', '料理', '自家製', '手作り', 'プロ', '作る', '仕上げ', '表現', '演出',
        '空間', '音', '色', '香り', '流儀', 'スタイル', '姿勢', '基準', 'ルール', '手間', '工夫',
        '魅力', '人気', 'おすすめ', '注目', '本格'
    ]
    if any(k in search_target for k in d_keywords):
        return 'D（現代的用法・ポジティブ）', '肯定的な追求・品質・表現重視に関するキーワードを検出', clean_text

    # 【ステップ4】語義C：近代的用法（ネガティブ・拘泥・囚われ）
    c_keywords = [
        '過去', '因習', '些細', '形式', '肩書', '立場', 'こだわりすぎ', '身動き',
        '拘泥', '囚われ', '縛られ', '否定的', 'ばかり', 'つまらぬ', '不要な', '悪癖',
        '泥拘', 'われ囚', '古い', '昔', '慣習', '常識', '体裁', '見栄', 'プライド',
        '意地', '執着', '固執', '偏見', '思い込み', '単なる', 'ただの', 'とらわれ', 'しばられ'
    ]
    if any(k in search_target for k in c_keywords):
        return 'C（近代的用法・ネガティブ）', '否定的な執着や枠組み（因習・過去・形式・拘泥等）を検出', clean_text

    if any(w in search_target for w in ['こだわ', 'わだこ']):
        return '要手動確認（C/D判別）', '「こだわる」関連表現はあるが、C/Dを決める手がかりが弱いため目視確認を推奨', clean_text

    return '要手動確認（C/D判別）', '判定キーワードが不足しているため目視確認を推奨', clean_text


# --- ファイル読み込み共通関数 ---
def load_uploaded_dataframe(uploaded_file):
    if uploaded_file.name.endswith('.csv'):
        encodings_to_try = [
            'utf-8-sig', 'utf-8', 'cp932', 'shift_jis',
            'euc-jp', 'utf-16', 'utf-16le', 'utf-16be'
        ]
        df = None
        for enc in encodings_to_try:
            try:
                uploaded_file.seek(0)
                df = pd.read_csv(uploaded_file, encoding=enc)
                break
            except Exception:
                continue

        if df is None:
            uploaded_file.seek(0)
            raw_bytes = uploaded_file.read()
            decoded_text = raw_bytes.decode('utf-8', errors='replace')
            df = pd.read_csv(io.StringIO(decoded_text))
        return df
    else:
        return pd.read_excel(uploaded_file)


# --- タブの作成（3タブ構成） ---
tab1, tab2, tab3 = st.tabs([
    "✍️ 直接入力して判定",
    "📁 ファイル一括処理",
    "👆 手動分類（1件ずつボタン判定）"
])

# 【タブ1】直接入力モード
with tab1:
    st.subheader("文章を直接入力して検証する")
    user_text = st.text_area("「こだわる」を含む文例を入力してください:", placeholder="例：プロが食材にこだわって作った絶品チャーハン")
    user_complement = st.text_input("補語や対象があれば入力してください（任意）:", placeholder="例：食材")

    if st.button("判定する", key="direct_button"):
        if user_text.strip() == "":
            st.warning("テキストを入力してください。")
        else:
            combined_input = user_text + " " + user_complement
            res_result, res_reason, cleaned = classify_text_string(combined_input)

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
    uploaded_file = st.file_uploader("エクセルまたはCSVファイルをアップロード", type=["xlsx", "xls", "csv"], key="batch_uploader")

    if uploaded_file is not None:
        try:
            df = load_uploaded_dataframe(uploaded_file)

            st.success("ファイルを正常に読み込みました。")
            st.subheader("📋 データのプレビュー")
            st.dataframe(df.head(5), use_container_width=True)

            columns = df.columns.tolist()
            st.subheader("⚙️ 判定対象の列を 3つ まで指定")
            st.write("※使用しない列がある場合は「なし」を選択してください。")

            col_options = ["なし"] + columns
            col_a = st.selectbox("判定対象の列 [1]", options=col_options, index=0)
            col_b = st.selectbox("判定対象の列 [2]", options=col_options, index=0)
            col_c = st.selectbox("判定対象の列 [3]", options=col_options, index=0)

            if st.button("🚀 一括自動分類を実行する", key="file_button"):
                results = []
                for idx, row in df.iterrows():
                    texts_to_combine = []
                    for c in [col_a, col_b, col_c]:
                        if c != "なし" and pd.notna(row[c]):
                            texts_to_combine.append(str(row[c]))

                    combined_row_text = " ".join(texts_to_combine)
                    res = classify_text_string(combined_row_text)
                    results.append(res)

                df['判定結果'] = [r[0] for r in results]
                df['判定理由・メモ'] = [r[1] for r in results]
                df['結合・整形済みテキスト'] = [r[2] for r in results]

                # 手動分類タブでもそのまま引き継げるようにセッションに保存
                st.session_state['manual_df'] = df.copy()
                st.session_state['manual_file_id'] = f"batch_{uploaded_file.name}"
                st.session_state['manual_pos'] = 0

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


# 【タブ3】手動分類（1件ずつボタン判定）モード
with tab3:
    st.subheader("👆 要手動確認の用例をボタンで素早く分類")
    st.write("自動分類後のExcelファイル（`こだわる_語彙素_BCCWJ_1117_意味分類後.xlsx` など）を読み込むと、「要手動確認」の行だけを1件ずつ表示します。")

    manual_file = st.file_uploader(
        "分類結果のExcelまたはCSVをアップロード（続きから再開も可能）",
        type=["xlsx", "xls", "csv"],
        key="manual_uploader"
    )

    if manual_file is not None:
        file_token = f"{manual_file.name}_{manual_file.size}"
        if st.session_state.get('manual_file_id') != file_token:
            try:
                loaded_df = load_uploaded_dataframe(manual_file)
                if '判定結果' not in loaded_df.columns:
                    loaded_df['判定結果'] = '要手動確認（C/D判別）'
                if '判定理由・メモ' not in loaded_df.columns:
                    loaded_df['判定理由・メモ'] = ''
                st.session_state['manual_df'] = loaded_df
                st.session_state['manual_file_id'] = file_token
                st.session_state['manual_pos'] = 0
            except Exception as e:
                st.error(f"ファイル読み込みエラー: {e}")

    if 'manual_df' in st.session_state:
        mdf = st.session_state['manual_df']
        all_cols = mdf.columns.tolist()

        # 表示するテキスト列の選択（デフォルトで「結合・整形済みテキスト」があれば優先）
        default_text_idx = 0
        if '結合・整形済みテキスト' in all_cols:
            default_text_idx = all_cols.index('結合・整形済みテキスト')

        with st.expander("⚙️ 表示する文章の列を設定（必要な場合のみ変更）", expanded=('結合・整形済みテキスト' not in all_cols)):
            disp_cols = st.multiselect(
                "画面に表示して読みたい列を選んでください（複数選択可）",
                options=all_cols,
                default=[all_cols[default_text_idx]] if all_cols else []
            )

        # 「要手動確認」を含む行のインデックスを取得
        target_indices = mdf[mdf['判定結果'].astype(str).str.contains('要手動確認', na=True)].index.tolist()
        total_rows = len(mdf)
        remaining_count = len(target_indices)
        done_count = total_rows - remaining_count

        st.markdown(f"**進捗状況：** 全 {total_rows} 件中 **{done_count} 件完了** ／ 残り要手動確認 **{remaining_count} 件**")
        st.progress(done_count / total_rows if total_rows > 0 else 1.0)

        if remaining_count == 0:
            st.success("🎉 すべての用例の分類が完了しました！下のボタンからExcelをダウンロードしてください。")
        else:
            pos = st.session_state.get('manual_pos', 0)
            if pos >= remaining_count:
                pos = 0
                st.session_state['manual_pos'] = 0

            current_row_idx = target_indices[pos]
            row_data = mdf.loc[current_row_idx]

            st.markdown(f"#### 📝 現在の用例（残り {remaining_count} 件中の {pos + 1} 件目 ／ 元データ {current_row_idx + 1} 行目）")

            # 用例テキストをカード風に大きく見やすく表示
            display_blocks = []
            for col_name in disp_cols:
                val = str(row_data[col_name]).replace('|', '') if pd.notna(row_data[col_name]) else ""
                if val.strip():
                    display_blocks.append(f"**【{col_name}】**\n{val}")

            if display_blocks:
                st.info("\n\n".join(display_blocks))
            else:
                st.info("（表示列が選択されていません。上の設定から文章の列を選択してください）")

            # A / B / C / D 判定ボタン
            st.write("▼ この用例の語義を選択してください（押すと自動で次へ進みます）：")
            b1, b2 = st.columns(2)
            b3, b4 = st.columns(2)

            def apply_manual_label(label_text):
                st.session_state['manual_df'].at[current_row_idx, '判定結果'] = label_text
                st.session_state['manual_df'].at[current_row_idx, '判定理由・メモ'] = '手動分類'
                # 分類すると対象リストから1件減るため、posはそのまま（次の要素が繰り上がる）
                st.rerun()

            with b1:
                if st.button("🅰️ A：文句を言う・理屈", use_container_width=True, key=f"btn_a_{current_row_idx}"):
                    apply_manual_label('A（文句を言う）')
            with b2:
                if st.button("🅱️ B：つかえる・障る", use_container_width=True, key=f"btn_b_{current_row_idx}"):
                    apply_manual_label('B（つかえる・障る）')
            with b3:
                if st.button("🇨 C：近代的・ネガティブ（拘泥）", use_container_width=True, key=f"btn_c_{current_row_idx}"):
                    apply_manual_label('C（近代的用法・ネガティブ）')
            with b4:
                if st.button("🇩 D：現代的・ポジティブ（追求）", use_container_width=True, key=f"btn_d_{current_row_idx}"):
                    apply_manual_label('D（現代的用法・ポジティブ）')

            # スキップ・戻る操作
            nav1, nav2, _ = st.columns([1, 1, 2])
            with nav1:
                if st.button("⬅️ 1つ前を見る", use_container_width=True, key="btn_prev"):
                    st.session_state['manual_pos'] = (pos - 1) % remaining_count
                    st.rerun()
            with nav2:
                if st.button("⏭️ 後回し（スキップ）", use_container_width=True, key="btn_skip"):
                    st.session_state['manual_pos'] = (pos + 1) % remaining_count
                    st.rerun()

        st.divider()
        # いつでも途中経過をダウンロード可能にする
        manual_output = io.BytesIO()
        with pd.ExcelWriter(manual_output, engine='xlsxwriter') as writer:
            st.session_state['manual_df'].to_excel(writer, index=False, sheet_name='分類結果')
        manual_excel_data = manual_output.getvalue()

        st.download_button(
            label="📥 ここまでの分類結果（Excel）を保存・ダウンロード",
            data=manual_excel_data,
            file_name="kodawaru_manual_classified.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            use_container_width=True
        )
