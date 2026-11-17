import io
import pandas as pd
import streamlit as st

st.set_page_config(page_title="「こだわる」語義自動分類ツール", layout="centered")
st.title("🔍 「こだわる」用例 自動分類ツール")
st.write("BCCWJ等のコーパスデータから、「こだわる」の使われ方をA/B/C/Dに自動・手動で仕分けします。")


def normalize_for_search(s: str) -> str:
    if not s:
        return ""
    t = s.replace("|", "").replace(" ", "").replace(" ", "").strip()
    kana_fixed = (
        t.replace("こだはつ", "こだわっ")
        .replace("こだはら", "こだわら")
        .replace("こだはり", "こだわり")
        .replace("こだはる", "こだわる")
        .replace("こだはれ", "こだわれば")
        .replace("拘はる", "こだわる")
        .replace("ゐ", "い")
        .replace("ゑ", "え")
        .replace("觀念", "観念")
        .replace("體裁", "体裁")
    )
    return f"{t} {kana_fixed}"


def classify_text_string(combined_text):
    clean_text = (
        str(combined_text).replace("|", "").replace(" ", " ").strip()
        if pd.notna(combined_text)
        else ""
    )
    norm_str = normalize_for_search(clean_text)
    reversed_str = norm_str[::-1]
    search_target = f"{clean_text} {norm_str} {reversed_str}"

    # 【ステップ1】語義B：つかえる、障る（物理的・身体的・心内的な引っかかりや障り）
    b_keywords = [
        "鍔", "脇指", "横つ腹", "喉", "ひっかかる", "つかえる", "かかる", "障る",
        "引っかかる", "引っ掛かる", "支障",
        "心にこだわる", "心に こだわる", "こだわるものがある", "こだはるものがある",
        "憂欝な気持",
    ]
    if any(k in search_target for k in b_keywords):
        return "B（つかえる・障る）", "物理的・身体的・心内的な引っかかりや障りに関するキーワードを検出", clean_text

    # 【ステップ2】語義A：わずかなことに理屈をつけて文句を言う
    a_keywords = [
        "理屈", "文句", "なんくせ", "言いがかり", "埒明けず", "難癖",
        "不平", "不満", "愚痴", "小言",
    ]
    if any(k in search_target for k in a_keywords):
        return "A（文句を言う）", "理屈や言いがかりに関するキーワードを検出", clean_text

    # 【ステップ3】語義D：現代的用法（ポジティブ・追求、および否定形の包括表現）
    if (
        "こだわらない" in norm_str
        or "こだわらず" in norm_str
        or "ないわだこ" in reversed_str
        or "ずわだこ" in reversed_str
    ):
        if any(
            k in search_target
            for k in [
                "ジャンル", "ブランド", "メーカー", "性別", "年齢", "国籍", "問わず",
                "関係なく", "一律", "種類", "形式", "方法", "場所", "時間",
            ]
        ):
            return "D（現代的用法・包括的）", "制限を設けない包括的・機能語的表現を検出", clean_text

    d_keywords = [
        "品質", "味", "素材", "食材", "本物", "住まい", "デザイン", "こだわりたい",
        "こだわりを深め", "追求", "追及", "厳選", "職人", "徹底", "とことん",
        "美味し", "おいし", "上質", "独自", "洗練", "絶品", "料理", "自家製",
        "手作り", "プロ", "作る", "仕上げ", "表現", "演出", "空間", "音", "色",
        "香り", "流儀", "スタイル", "姿勢", "基準", "ルール", "手間", "工夫",
        "魅力", "人気", "おすすめ", "注目", "本格",
    ]
    if any(k in search_target for k in d_keywords):
        return "D（現代的用法・ポジティブ）", "肯定的な追求・品質・表現重視に関するキーワードを検出", clean_text

    # 【ステップ4】語義C：近代的用法（ネガティブ・拘泥・囚われ・枠組みへの批判や無頓着）
    c_keywords = [
        "過去", "因習", "些細", "形式", "肩書", "立場", "こだわりすぎ", "身動き",
        "拘泥", "囚われ", "縛られ", "否定的", "ばかり", "つまらぬ", "不要な", "悪癖",
        "泥拘", "われ囚", "古い", "昔", "慣習", "常識", "体裁", "體裁", "見栄", "プライド",
        "意地", "執着", "固執", "偏見", "思い込み", "単なる", "ただの", "とらわれ",
        "しばられ", "観念", "ていられない", "られないほど", "すら", "さえ",
        "べきではない", "べきじゃない", "べきではないか", "こだわっているべき",
        "はずかしい", "はづかしい", "恥ずかしい", "恥じ", "後ろめたい", "みっともない", "情けない",
        "こだわらぬ", "こだわらず", "融通", "機会主義", "機會主義",
        "引いてしまう", "引いてしまふ", "嘗て", "かつて",
        "民主的でない", "民主的ではない", "ぢやない", "じゃない",
        "こだわらなかつた", "こだわらなかった", "こだわらなかつたから", "こだわらなかったから",
        "無事にすんだ", "無事に済んだ", "無事にすむ", "無事に済む",
        "無事に納まった", "無事に収まった", "無事に治まった", "無事にをさまつた",
        "事なきを得た", "事なきを得て", "穏便に",
        "幾度も", "何度も", "度々", "たびたび",
        "こだわるようである", "こだわるようだが",
        "がつかりした", "がっかりした", "ゆえんである", "もち出された",
        "こだわらなくてもよかつた", "こだわらなくてもよかった",
        "こだわらなくてもよい", "こだわらなくてもいい",
        "強くこだわら", "あまりこだわら", "さほどこだわら",
        "それほどこだわら", "一向にこだわら",
        "こだわらない方", "こだわらないのだ", "こだわらないのです",
        "こだわつ たことがないし", "こだわったことがないし", "それほどこだわつ",
        "腹の立つ", "腹が立つ",
        "文体", "荒削り", "すなおに", "素直に",
    ]
    if any(k in search_target for k in c_keywords):
        return "C（近代的用法・ネガティブ）", "否定的な執着や枠組み・拘泥・評価表現を検出", clean_text

    if any(neg in norm_str for neg in ["こだわらな", "こだわらず", "こだわらぬ"]):
        if any(calm in search_target for calm in ["無事", "事なき", "穏便", "もめず", "揉めず"]):
            return "C（近代的用法・ネガティブ）", "こだわらなかったことによる波風回避・無事の文脈を検出", clean_text

    if any(w in search_target for w in ["こだわ", "わだこ"]):
        return "要手動確認（C/D判別）", "「こだわる」関連表現はあるが、C/Dを決める手がかりが弱いため目視確認を推奨", clean_text

    return "要手動確認（C/D判別）", "判定キーワードが不足しているため目視確認を推奨", clean_text


def load_uploaded_dataframe(uploaded_file):
    if uploaded_file.name.endswith(".csv"):
        encodings_to_try = [
            "utf-8-sig", "utf-8", "cp932", "shift_jis",
            "euc-jp", "utf-16", "utf-16le", "utf-16be",
        ]
        for enc in encodings_to_try:
            try:
                uploaded_file.seek(0)
                return pd.read_csv(uploaded_file, encoding=enc)
            except Exception:
                continue
        uploaded_file.seek(0)
        raw_bytes = uploaded_file.read()
        decoded_text = raw_bytes.decode("utf-8", errors="replace")
        return pd.read_csv(io.StringIO(decoded_text))
    uploaded_file.seek(0)
    return pd.read_excel(uploaded_file, sheet_name=0)


tab1, tab2, tab3 = st.tabs([
    "✍️ 直接入力して判定",
    "📁 ファイル一括処理",
    "👆 手動分類（1件ずつボタン判定）",
])

with tab1:
    st.subheader("文章を直接入力して検証する")
    user_text = st.text_area(
        "「こだわる」を含む文例を入力してください:",
        placeholder="例：私は心に こだわる ものがあるので、自分の満足はえられなかつた。",
    )
    user_complement = st.text_input("補語や対象があれば入力してください（任意）:", placeholder="例：心に")

    if st.button("判定する", key="direct_button"):
        if not user_text.strip():
            st.warning("テキストを入力してください。")
        else:
            combined_input = f"{user_text} {user_complement}"
            res_result, res_reason, cleaned = classify_text_string(combined_input)

            st.markdown("### 📌 判定結果")
            if "A" in res_result:
                st.error(f"**判定:** {res_result}")
            elif "B" in res_result:
                st.warning(f"**判定:** {res_result}")
            elif "D" in res_result:
                st.success(f"**判定:** {res_result}")
            else:
                st.info(f"**判定:** {res_result}")

            st.write(f"**理由・メモ:** {res_reason}")
            st.text(f"【確認用】整形済みテキスト: {cleaned}")

with tab2:
    uploaded_file = st.file_uploader(
        "エクセルまたはCSVファイルをアップロード",
        type=["xlsx", "xls", "csv"],
        key="batch_uploader",
    )

    if uploaded_file is not None:
        try:
            df = load_uploaded_dataframe(uploaded_file)
            st.success("ファイルを正常に読み込みました。")
            st.subheader("📋 データのプレビュー")
            st.dataframe(df.head(5), use_container_width=True)

            columns = df.columns.tolist()
            col_options = ["なし"] + columns
            st.subheader("⚙️ 判定対象の列を 3つ まで指定")
            col_a = st.selectbox("判定対象の列 [1]", options=col_options, index=0)
            col_b = st.selectbox("判定対象の列 [2]", options=col_options, index=0)
            col_c = st.selectbox("判定対象の列 [3]", options=col_options, index=0)

            if st.button("🚀 一括自動分類を実行する", key="file_button"):
                results = []
                for _, row in df.iterrows():
                    parts = [
                        str(row[c])
                        for c in [col_a, col_b, col_c]
                        if c != "なし" and pd.notna(row[c])
                    ]
                    results.append(classify_text_string(" ".join(parts)))

                df["判定結果"] = [r[0] for r in results]
                df["判定理由・メモ"] = [r[1] for r in results]
                df["結合・整形済みテキスト"] = [r[2] for r in results]

                st.session_state["manual_df"] = df.copy()
                st.session_state["manual_file_id"] = f"batch_{uploaded_file.name}"
                st.session_state["manual_pos"] = 0

                st.subheader("📊 分類結果の集計")
                st.bar_chart(df["判定結果"].value_counts())

                st.subheader("📝 判定結果一覧")
                st.dataframe(df, use_container_width=True)

                output = io.BytesIO()
                with pd.ExcelWriter(output, engine="xlsxwriter") as writer:
                    df.to_excel(writer, index=False, sheet_name="分類結果")

                st.download_button(
                    label="📥 分類結果（Excel）をダウンロード",
                    data=output.getvalue(),
                    file_name="kodawaru_classified_result.xlsx",
                    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                )
        except Exception as e:
            st.error(f"エラーが発生しました: {e}")

with tab3:
    st.subheader("👆 要手動確認の用例をボタンで素早く分類")
    st.write("自動分類後のExcelファイルを読み込むと、「要手動確認」の行だけを1件ずつ表示します。")

    manual_file = st.file_uploader(
        "分類結果のExcelまたはCSVをアップロード（続きから再開も可能）",
        type=["xlsx", "xls", "csv"],
        key="manual_uploader",
    )

    if manual_file is not None:
        file_token = f"{manual_file.name}_{manual_file.size}"
        if st.session_state.get("manual_file_id") != file_token:
            with st.spinner("ファイルを読み込んでいます..."):
                try:
                    loaded_df = load_uploaded_dataframe(manual_file)
                    if "判定結果" not in loaded_df.columns:
                        loaded_df["判定結果"] = "要手動確認（C/D判別）"
                    if "判定理由・メモ" not in loaded_df.columns:
                        loaded_df["判定理由・メモ"] = ""

                    st.session_state["manual_df"] = loaded_df
                    st.session_state["manual_file_id"] = file_token
                    st.session_state["manual_pos"] = 0
                except Exception as e:
                    st.error(f"ファイル読み込みエラー: {e}")
                    st.stop()

    if "manual_df" in st.session_state:
        mdf = st.session_state["manual_df"]
        all_cols = mdf.columns.tolist()

        default_col = (
            ["結合・整形済みテキスト"]
            if "結合・整形済みテキスト" in all_cols
            else (all_cols[:1] if all_cols else [])
        )

        with st.expander(
            "⚙️ 表示する文章の列を設定（必要な場合のみ変更）",
            expanded=("結合・整形済みテキスト" not in all_cols),
        ):
            disp_cols = st.multiselect(
                "画面に表示して読みたい列を選んでください（複数選択可）",
                options=all_cols,
                default=default_col,
                key="manual_disp_cols",
            )

        target_indices = mdf[
            mdf["判定結果"].astype(str).str.contains("要手動確認", na=True)
        ].index.tolist()
        total_rows = len(mdf)
        remaining_count = len(target_indices)
        done_count = total_rows - remaining_count

        st.markdown(
            f"**進捗状況：** 全 {total_rows} 件中 **{done_count} 件完了** ／ 残り要手動確認 **{remaining_count} 件**"
        )
        st.progress(done_count / total_rows if total_rows > 0 else 1.0)

        if remaining_count == 0:
            st.success("🎉 すべての用例の分類が完了しました！下のボタンからExcelをダウンロードしてください。")
        else:
            pos = st.session_state.get("manual_pos", 0)
            if pos >= remaining_count:
                pos = 0
                st.session_state["manual_pos"] = 0

            current_row_idx = target_indices[pos]
            row_data = mdf.loc[current_row_idx]

            st.markdown(
                f"#### 📝 現在の用例（残り {remaining_count} 件中の {pos + 1} 件目 ／ 元データ {current_row_idx + 1} 行目）"
            )

            display_blocks = []
            for col_name in disp_cols:
                val = str(row_data[col_name]).replace("|", "") if pd.notna(row_data[col_name]) else ""
                if val.strip():
                    display_blocks.append(f"【{col_name}】 {val}")

            if display_blocks:
                for blk in display_blocks:
                    st.info(blk)
            else:
                st.info("（表示列が選択されていません。上の設定から文章の列を選択してください）")

            st.write("▼ この用例の語義を選択してください（押すと自動で次へ進みます）：")
            b1, b2 = st.columns(2)
            b3, b4 = st.columns(2)

            def apply_manual_label(label_text):
                st.session_state["manual_df"].at[current_row_idx, "判定結果"] = label_text
                st.session_state["manual_df"].at[current_row_idx, "判定理由・メモ"] = "手動分類"
                st.rerun()

            with b1:
                if st.button("🅰️ A：文句を言う・理屈", use_container_width=True, key=f"btn_a_{current_row_idx}"):
                    apply_manual_label("A（文句を言う）")
            with b2:
                if st.button("🅱️ B：つかえる・障る", use_container_width=True, key=f"btn_b_{current_row_idx}"):
                    apply_manual_label("B（つかえる・障る）")
            with b3:
                if st.button("🇨 C：近代的・ネガティブ（拘泥）", use_container_width=True, key=f"btn_c_{current_row_idx}"):
                    apply_manual_label("C（近代的用法・ネガティブ）")
            with b4:
                if st.button("🇩 D：現代的・ポジティブ（追求）", use_container_width=True, key=f"btn_d_{current_row_idx}"):
                    apply_manual_label("D（現代的用法・ポジティブ）")

            nav1, nav2, _ = st.columns([1, 1, 2])
            with nav1:
                if st.button("⬅️ 1つ前を見る", use_container_width=True, key="btn_prev"):
                    st.session_state["manual_pos"] = (pos - 1) % remaining_count
                    st.rerun()
            with nav2:
                if st.button("⏭️ 後回し（スキップ）", use_container_width=True, key="btn_skip"):
                    st.session_state["manual_pos"] = (pos + 1) % remaining_count
                    st.rerun()

        st.divider()
        manual_output = io.BytesIO()
        with pd.ExcelWriter(manual_output, engine="xlsxwriter") as writer:
            st.session_state["manual_df"].to_excel(writer, index=False, sheet_name="分類結果")

        st.download_button(
            label="📥 ここまでの分類結果（Excel）を保存・ダウンロード",
            data=manual_output.getvalue(),
            file_name="kodawaru_manual_classified.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            use_container_width=True,
        )
