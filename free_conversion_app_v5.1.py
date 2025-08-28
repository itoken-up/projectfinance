import streamlit as st
import pandas as pd
import zipfile, io, re, tempfile, gdown, calendar
from datetime import date, datetime
from dateutil.relativedelta import relativedelta
from st_aggrid import AgGrid, GridOptionsBuilder
from st_aggrid.shared import GridUpdateMode

# ──────────────────────────────────────────────
# 固定マッピング : RecordID (B列) ➜ DealID (C列)
# ──────────────────────────────────────────────
ID_MAP_FIXED = {
    'AKE202210_KEIEI_U': '9775650935',
    'AMA202211_SYSTEM_P': '13111634538',
    'AMA202304_2BREPO_P': '13111594792',
    'AMA202304_ECREPO_P': '13111634452',
    'AMA202304_ECSYST_P': '13111594849',
    'AMA202305_BILLIN_P': '13334264959',
    'AMA202306_SCMPMO_P': '13826848558',
    'AMA202307_ELSIGN_P': '13965251380',
    'AMA202307_MGTADV_U': '13906057056',
    'ARA202308_JIGYOU_P': '12746802825',
    'BRI202309_OTHERS_P': '12850387035',
    'BRI202310_PMOSUP_P': '16033621034',
    'CLE202304_CDMOTR_U': '13523440943',
    'DAI202309_OTHERS_P': '15098798720',
    'DEK202307_OTHERS_P': '12911619969',
    'DEK202308_OTHERS_U': '13964560773',
    'DEK202312_FASMAA_U': '16351470488',
    'DEK202312_OTHERS_U': '16037489190',
    'DEN202210_JIGYOU_P': '10172816231',
    'DEN202302_JIGYOU_U': '12030335245',
    'DEN202309_JIGYOU_P': '13909275047',
    'DEN202309_OTHERS_P': '14767850896',
    'ELN202303_VISASQ_U': '12602652171',
    'FAN202302_HOKUBE_U': '11770846345',
    'FUJ202302_JIGYOU_U': '12158729512',
    'FUT202308_DXSTRA_P': '14148089088',
    'HIR202211_ESSYST_P': '10362965791',
    'HIR202302_ESCONS_U': '12073670611',
    'HIR202302_JIGYOU_U': '12073670418',
    'HIR202302_JPSGAN_U': '12073670158',
    'HIR202303_JIGYOU_U': '12170849132',
    'HIR202304_JIGYOU_U': '12223160017',
    'HIR202305_JIGYOU_U': '12363647079',
    'HIR202306_JIGYOU_U': '12515803893',
    'HIR202307_JIGYOU_U': '13111138855',
    'HIR202308_OTHERS_U': '13739060018',
    'HIR202309_JIGYOU_U': '13964605132',
    'HIT202302_JIGYOU_U': '11934460122',
    'HIT202304_DXCONS_U': '12394681781',
    'HIT202305_OTHERS_P': '12394681487',
    'HIT202306_OTHERS_P': '12561539312',
    'HIT202307_OTHERS_P': '13111138884',
    'HIT202308_OTHERS_P': '13737542047',
    'HIT202309_OTHERS_P': '14767850830',
    'INM202307_DXCONS_P': '12747279127',
    'INM202309_DXCONS_P': '14767043959',
    'JDC202308_JIGYOU_U': '13739310719',
    'JDC202309_OTHERS_U': '14671654128',
    'KAK202303_DXMKTG_P': '12561292342',
    'KAK202304_SUSTAI_P': '12223160034',
    'KAK202306_OTHERS_P': '12665061861',
    'KAK202307_OTHERS_P': '12910901831',
    'KAK202308_OTHERS_P': '13739059963',
    'KAK202309_OTHERS_P': '14671654171',
    'KOK202306_OTHERS_P': '12910901839',
    'KOK202307_OTHERS_P': '12910901845',
    'KOK202308_OTHERS_P': '13737542079',
    'KOK202309_OTHERS_P': '14671654191',
    'KYO202210_MDTYPE_P': '10172816310',
    'KYO202303_OTHERS_P': '12561292366',
    'KYO202304_OTHERS_P': '12257979771',
    'LIF202308_OTHERS_P': '14148089119',
    'LIF202309_OTHERS_P': '15100050932',
    'MIK202308_OTHERS_P': '13737542093',
    'MON202210_TAXSPA_P': '10455428996',
    'MON202211_TAXSPA_P': '10455429076',
    'MON202301_TAXSPA_P': '11770846395',
    'MON202302_TAXSPA_P': '12158729536',
    'MON202303_OTHERS_P': '12456413016',
    'MON202304_OTHERS_P': '12223160047',
    'MON202306_TAXSPA_P': '12561539221',
    'MON202307_OTHERS_P': '12911619960',
    'MON202308_OTHERS_P': '13737542107',
    'MON202309_OTHERS_P': '15100050944',
    'NIT202210_OPMKTG_P': '10172590823',
    'NRI202210_DXCONS_P': '10172816325',
    'NSS202302_DXSTRA_P': '11770846424',
    'NSS202306_OTHERS_P': '12561539273',
    'NSS202307_OTHERS_P': '12911220631',
    'NSS202308_OTHERS_P': '13739060041',
    'NSS202309_OTHERS_P': '13964605170',
    'OKI202307_OTHERS_P': '12911619977',
    'OKI202308_OTHERS_P': '13739060051',
    'OKI202309_OTHERS_P': '14671654213',
    'RIC202309_OTHERS_P': '14767171462',
    'RYO202308_DXSTRA_P': '14148089146',
    'SHP202210_DXSTRA_P': '10455429113',
    'SHP202307_OTHERS_P': '12910901871',
    'SHP202308_OTHERS_P': '13737542123',
    'SHP202309_OTHERS_P': '14767850911',
    'SMB202210_JIGYOU_P': '10172816344',
    'SMB202302_JIGYOU_U': '11770846443',
    'SMB202304_JIGYOU_P': '12257979795',
    'SMB202306_JIGYOU_P': '12602652214',
    'SMB202307_JIGYOU_P': '12910901890',
    'SMB202308_JIGYOU_P': '13737542137',
    'SMB202309_JIGYOU_P': '14768031259',
    'SMT202210_SYSMIG_P': '10172816352',
    'SMT202210_SYSTUN_P': '10172816371',
    'SMT202212_JIGYOU_P': '10363337802',
    'SMT202303_JIGYOU_P': '12561292418',
    'SMT202304_JIGYOU_P': '12257979805',
    'SMT202305_OTHERS_P': '12394681563',
    'SMT202306_OTHERS_P': '12561539286',
    'SMT202307_OTHERS_P': '12911220662',
    'SMT202308_OTHERS_P': '13739060064',
    'SMT202309_OTHERS_P': '13964605187',
    'SNS202309_OTHERS_P': '13964605191',
    'TAX202210_OTHERS_P': '10455429145',
    'TAX202302_HOKUBE_U': '11770846459',
    'TSC202301_SYSTEM_P': '9739381018',
    'TTS202304_JIGRESEAC_P': '12783695123',
    'TTS202306_VISASQ_U': '13374247579',
    'UAC202308_OTHERS_P': '13963049397',
    'UAC202307_OTHERS_P': '13411248700',
    'YON202301_DXSTRA_P': '12456413034',
    'YON202308_OTHERS_U': '13737542160',
    'YON202309_DXSTRA_P': '14446752905',
    'YON202312_DXSTRA_P': '15481667376'
}

# ──────────────────────────────────────────────
# ページ設定
# ──────────────────────────────────────────────
st.set_page_config(page_title="プロジェクト収益 v7.2", layout="wide")

# ──────────────────────────────────────────────
# 共通ユーティリティ
# ──────────────────────────────────────────────
def detect_col(cols, patterns):
    for p in patterns:
        hits = [c for c in cols if re.sub(r"\s+", "", str(c)).casefold() == p]
        if hits:
            return hits[0]
    return None


def normalize_id(x):
    if pd.isna(x):
        return None
    s = str(x).strip()
    return None if s == "" or s.lower() in {"nan", "none"} else s


# ── CSV / ZIP ローダ ---------------------------------------------------------
def load_csv(uploaded):
    """① CSV ② ZIP 内 CSV を DataFrame で返す"""
    if uploaded is None:
        return None

    # ZIP
    if uploaded.name.lower().endswith(".zip"):
        try:
            with zipfile.ZipFile(uploaded) as zf:
                csv_files = [n for n in zf.namelist()
                             if n.lower().endswith(".csv") and not n.endswith("/")]
                if not csv_files:
                    st.error("ZIP に CSV が見つかりません。")
                    return None
                target = csv_files[0] if len(csv_files) == 1 else \
                         st.selectbox("ZIP 内 CSV を選択してください", csv_files)
                with zf.open(target) as fp:
                    for enc in ("utf-8-sig", "cp932", "utf-8"):
                        try:
                            txt = fp.read().decode(enc)
                            return pd.read_csv(io.StringIO(txt))
                        except Exception:
                            fp.seek(0)
        except zipfile.BadZipFile:
            st.error("ZIP ファイルが壊れています。")
            return None

    # 通常 CSV
    for enc in ("utf-8-sig", "cp932", "utf-8"):
        try:
            txt = uploaded.read().decode(enc)
            return pd.read_csv(io.StringIO(txt))
        except Exception:
            uploaded.seek(0)

    st.error("CSV の読み込みに失敗しました。文字コードを確認してください。")
    return None


# ── Google Drive 共有リンク ---------------------------------------------------
def read_gdrive_csv_gdown(url: str, **kw) -> pd.DataFrame:
    """共有リンク → gdown で DL → DataFrame"""
    with tempfile.NamedTemporaryFile(delete=False, suffix=".csv") as tmp:
        gdown.download(url=url, output=tmp.name, quiet=False, fuzzy=True)
        return pd.read_csv(tmp.name, **kw)

# ──────────────────────────────────────────────
# サイドバー : データ入力（Expander）
# ──────────────────────────────────────────────
with st.sidebar.expander("📂 データアップロード / 選択", expanded=True):
    # 仕訳帳
    tab_local, tab_drive = st.tabs(["ローカル CSV / ZIP", "Google Drive 共有リンク"])

    with tab_local:
        uploaded_file = st.file_uploader("仕訳帳 (CSV / ZIP), journal", type=["csv", "zip"])

    with tab_drive:
        gdrive_url = st.text_input("共有リンクを貼って Enter",
                                   placeholder="https://drive.google.com/file/d/…/view?usp=sharing")
        if gdrive_url and not gdrive_url.startswith("http"):
            st.warning("リンク形式が正しくありません。")
            gdrive_url = ""

    st.markdown("---")

    # 取引マスタ / 稼働コスト
    cost_file   = st.file_uploader("稼働コスト (CSV), utilization", type="csv")
    master_file = st.file_uploader("取引マスタ (CSV), transaction", type="csv")

# ──────────────────────────────────────────────
# ファイル未アップロード時のガイダンス表示
# ──────────────────────────────────────────────
guidance_condition = (
    (uploaded_file is None) and
    (cost_file is None) and
    (master_file is None) and
    (not gdrive_url)
)
if guidance_condition:
    st.markdown("## Read me: アップロードデータの取得方法")
    card_style = (
        "background-color:rgba(173,230,180,0.2);"
        "padding:32px;"
        "border-radius:8px;"
        "margin-bottom:16px;"
    )
    st.markdown(
        f"""
        <div style="{card_style}">
        <h4>仕訳帳（journal）</h4>
        <ol style="padding-left:16px; margin-top:0; margin-bottom:0;">
          <li>Freeeにて「会計帳簿」＞「仕訳帳」を開く</li>
          <li>取引日を任意の期間に設定</li>
          <li>「インポート・エクスポート」＞「CSV・PDFエクスポート」＞「（新）CSV」＞Shift_JIS＞出力でファイルダウンロード</li>
          <li>ファイル名を <strong>"journal"</strong> に変更</li>
        </ol>
        </div>
        """,
        unsafe_allow_html=True
    )
    st.markdown(
        f"""
        <div style="{card_style}">
        <h4>稼働コスト（utilization）</h4>
        <ol style="padding-left:16px; margin-top:0; margin-bottom:0;">
          <li>HubSpotより「UP社員/アサイン履歴」レポートをCSVエクスポート</li>
          <li>ファイル名を <strong>"utilization"</strong> に変更</li>
        </ol>
        </div>
        """,
        unsafe_allow_html=True
    )
    st.markdown(
        f"""
        <div style="{card_style}">
        <h4>取引マスタ（transaction）</h4>
        <ol style="padding-left:16px; margin-top:0; margin-bottom:0;">
          <li>HubSpotより「CRM」＞「取引」からすべての取引をCSVエクスポート</li>
          <li>ファイル名を <strong>"transaction"</strong> に変更</li>
        </ol>
        </div>
        """,
        unsafe_allow_html=True
    )

# ──────────────────────────────────────────────
# 仕訳帳読込
# ──────────────────────────────────────────────
df_src = None
if uploaded_file is not None:
    df_src = load_csv(uploaded_file)
elif gdrive_url:
    try:
        df_src = read_gdrive_csv_gdown(gdrive_url, encoding="cp932")
    except Exception as e:
        st.error(f"Google Drive 読み込み失敗: {e}")
if df_src is None:
    st.stop()
df_src["取引日"] = pd.to_datetime(df_src["取引日"], errors="coerce")

# ---------- RecordID → DealID 置換（固定マッピング） ----------
TARGET_COLS = ["貸方部門", "借方部門"]
for col in TARGET_COLS:
    if col in df_src.columns:
        df_src[col] = df_src[col].map(lambda x: ID_MAP_FIXED.get(normalize_id(x), x))

# 取引マスタ読込 -----------------------------------------------------
master_map = None
if master_file:
    df_master = load_csv(master_file)
    if df_master is not None:
        df_master.columns = df_master.columns.map(str.strip)
        id_col   = detect_col(df_master.columns, ["取引id","レコードid","recordid","dealid"])
        amt_col  = detect_col(df_master.columns, ["金額","売上金額","見積金額","amount"])
        if id_col and amt_col:
            df_master[id_col]  = df_master[id_col].map(normalize_id)
            df_master[amt_col] = pd.to_numeric(df_master[amt_col], errors="coerce").fillna(0)
            keep = {id_col:"取引コード", amt_col:"マスター金額"}
            for src, dst in [
                (["取引先","会社名","customer","client"],"マスター取引先"),
                (["取引名","案件名","dealname","title"],"取引名"),
                (["取引担当者","担当者","owner","sales"],"取引担当者"),
                (["industry","業界"],"Industry"),
                (["industry詳細","industrydetail","業界詳細"],"Industry詳細"),
                (["提案商材","proposal","product"],"提案商材")
            ]:
                c = detect_col(df_master.columns, src)
                if c: keep[c] = dst
            master_map = (df_master[list(keep)]
                          .dropna(subset=[id_col])
                          .rename(columns=keep)
                          .drop_duplicates(subset=["取引コード"]))

# 稼働コスト読込 -----------------------------------------------------
df_cost_raw = None
if cost_file:
    df_cost_raw = load_csv(cost_file)
    if df_cost_raw is not None:
        df_cost_raw.columns = df_cost_raw.columns.map(str.strip)

# -------------- 既存ロジックで daily を作成 (売上・費用・人件費) --------------
# 売上・費用整形
df_sales = df_src[df_src.get("貸方勘定科目") == "売上高"].copy()
df_sales_out = pd.DataFrame({
    "取引コード": df_sales["貸方部門"].astype(str).str.strip(),
    "取引先": df_sales["貸方取引先名"],
    "勘定科目": "売上高",
    "金額": pd.to_numeric(df_sales["貸方金額"], errors="coerce").fillna(0),
    "日付": df_sales["取引日"]
})

targets = ["外注費","交際費","旅費交通費"]
df_exp = df_src[df_src.get("借方勘定科目").isin(targets)].copy()
df_exp_out = pd.DataFrame({
    "取引コード": df_exp["借方部門"].astype(str).str.strip(),
    "取引先": df_exp["借方取引先名"],
    "勘定科目": df_exp["借方勘定科目"],
    "金額": pd.to_numeric(df_exp["借方金額"], errors="coerce").fillna(0),
    "日付": df_exp["取引日"]
})
combo = pd.concat([df_sales_out, df_exp_out], ignore_index=True)

# pivot
daily = (combo.pivot_table(index="取引コード", columns="勘定科目",
                           values="金額", aggfunc="sum",
                           fill_value=0)
         .reset_index())
meta = (combo.groupby("取引コード")
             .agg({"日付":["min","max"],"取引先":"first"}).reset_index())
meta.columns = ["取引コード","日付（最小）","日付（最大）","取引先"]
daily = daily.merge(meta, on="取引コード", how="left")
if "売上高" not in daily.columns:
    daily["売上高"] = 0

# 人件費 (稼働コスト CSV) ------------------------------------------------------
if df_cost_raw is not None:
    id_c   = detect_col(df_cost_raw.columns, ["取引id","レコードid","recordid"])
    cost_c = detect_col(df_cost_raw.columns, ["稼働コスト","人件費","cost"])
    name_c = detect_col(df_cost_raw.columns, ["会社名","取引先","client","customer"])
    if id_c and cost_c:
        df_cost_raw[id_c] = df_cost_raw[id_c].map(normalize_id)
        df_cost = df_cost_raw.dropna(subset=[id_c]).copy()
        df_cost["人件費"] = pd.to_numeric(df_cost[cost_c], errors="coerce").fillna(0)
        agg = {"人件費":"sum"}
        if name_c: agg[name_c] = "first"
        cost_info = (
            df_cost.groupby(id_c, as_index=False)
                   .agg(agg)
                   .rename(columns={
                        id_c:   "取引コード",
                        cost_c: "人件費",
                        **({name_c: "稼働取引先"} if name_c else {})
                   })
        )
        daily["取引コード"] = daily["取引コード"].map(normalize_id)
        daily = daily.merge(cost_info, on="取引コード", how="left")
    else:
        daily["人件費"] = 0
else:
    daily["人件費"] = 0

# マスタ補完 -----------------------------------------------------------
if master_map is not None:
    daily = daily.merge(master_map, on="取引コード", how="left")
    need_fix = daily["売上高"] == 0
    daily.loc[need_fix, "売上高"] = daily.loc[need_fix, "マスター金額"]
    has_cost_name = daily["稼働取引先"].notna()
    daily.loc[need_fix & has_cost_name, "取引先"] = \
        daily.loc[need_fix & has_cost_name, "稼働取引先"]

# 指標計算 -------------------------------------------------------------
for c in ["売上高","外注費","交際費","旅費交通費","人件費"]:
    daily[c] = pd.to_numeric(daily[c], errors="coerce").fillna(0)
daily["月数"] = daily.apply(
    lambda r: max((r["日付（最大）"].year - r["日付（最小）"].year)*12 +
                  (r["日付（最大）"].month - r["日付（最小）"].month) + 1, 1),
    axis=1)
daily["月次売上"] = daily.apply(
    lambda r: r["売上高"]/r["月数"] if r["月数"] else 0, axis=1)
daily["粗利"] = (daily["売上高"] - daily["外注費"] - daily["交際費"]
                 - daily["旅費交通費"] - daily["人件費"])
daily["粗利率"] = daily.apply(
    lambda r: (r["粗利"]/r["売上高"]*100) if r["売上高"]>0 else 0, axis=1)
daily.rename(columns={"取引コード":"レコードID"}, inplace=True)

# ──────────────────────────────────────────────
# フィルター UI
# ──────────────────────────────────────────────
st.sidebar.markdown("### 🔍 フィルター設定")
id_val = st.sidebar.text_input("取引ID（部分一致可）", "")
min_date = df_src["取引日"].min().date()
max_date = df_src["取引日"].max().date()
start_date, end_date = st.sidebar.date_input("期間範囲", [min_date, max_date])

owner_sel = ind_sel = ind_det_sel = []
if "取引担当者" in daily.columns:
    owner_sel = st.sidebar.multiselect("取引担当者",
                                       sorted(daily["取引担当者"].dropna().unique()))
if "Industry" in daily.columns:
    ind_sel = st.sidebar.multiselect("Industry",
                                     sorted(daily["Industry"].dropna().unique()))
if "Industry詳細" in daily.columns:
    ind_det_sel = st.sidebar.multiselect("Industry詳細",
                                         sorted(daily["Industry詳細"].dropna().unique()))

mask  = daily["レコードID"].str.contains(id_val, na=False)
mask &= daily["日付（最大）"].dt.date >= start_date
mask &= daily["日付（最小）"].dt.date <= end_date
if owner_sel:
    mask &= daily["取引担当者"].isin(owner_sel)
if ind_sel:
    mask &= daily["Industry"].isin(ind_sel)
if ind_det_sel:
    mask &= daily["Industry詳細"].isin(ind_det_sel)
df_filtered = daily[mask].copy()

# ──────────────────────────────────────────────
# 月次テーブル & 案件数（期間内のみ）
# ──────────────────────────────────────────────
records_sales, records_profit = [], []
for _, r in df_filtered.iterrows():
    for i in range(int(r["月数"])):
        dt_m = r["日付（最小）"] + relativedelta(months=i)
        if not (start_date <= dt_m.date() <= end_date):
            continue
        ym = dt_m.strftime("%y/%m")
        records_sales.append({"年月表示":ym,"レコードID":r["レコードID"],
                              "取引先":r["取引先"],
                              "月次売上":round(r["月次売上"])})
        records_profit.append({"年月表示":ym,"レコードID":r["レコードID"],
                               "取引先":r["取引先"],
                               "月次粗利":round(r["粗利"]/r["月数"]) if r["月数"] else 0})
df_ms = pd.DataFrame(records_sales)
df_mp = pd.DataFrame(records_profit)

df_sales_p  = (df_ms.pivot_table(index=["レコードID","取引先"],
                                 columns="年月表示",
                                 values="月次売上", fill_value=0).reset_index())
df_profit_p = (df_mp.pivot_table(index=["レコードID","取引先"],
                                 columns="年月表示",
                                 values="月次粗利", fill_value=0).reset_index())
time_cols = sorted(df_ms["年月表示"].unique().tolist())

for df_num in (df_sales_p, df_profit_p):
    for col in time_cols:
        df_num[col] = (df_num[col]
                       .astype(str)            # 念のため str に統一
                       .str.replace(",", "")   # カンマ除去
                       .astype(float)          # 数値化
                       .fillna(0))

summary_sales = pd.DataFrame({
    "レコードID":["",""], "取引先":["①月次売上合計","②平均売上単価"],
    **{c:[df_sales_p[c].sum(), df_sales_p[c].mean()] for c in time_cols}
})
summary_profit = pd.DataFrame({
    "レコードID":["",""], "取引先":["③月次粗利合計","④平均粗利単価"],
    **{c:[df_profit_p[c].sum(), df_profit_p[c].mean()] for c in time_cols}
})
for c in time_cols:
    summary_sales[c]  = summary_sales[c].map(lambda x:f"{int(x):,}")
    summary_profit[c] = summary_profit[c].map(lambda x:f"{int(x):,}")

count_series = (df_ms[df_ms["月次売上"]>0]
                .groupby("年月表示")["レコードID"].nunique()
                .reindex(time_cols, fill_value=0))

# ──────────────────────────────────────────────
# Utilization 計算
# ──────────────────────────────────────────────
util_hours_pivot = pd.DataFrame()
util_pct_pivot   = pd.DataFrame()
std_hours_row    = {}

if df_cost_raw is not None:
    # 対象列
    cons_c  = detect_col(df_cost_raw.columns, ["コンサルタント名","氏名","name"])
    hours_c = detect_col(df_cost_raw.columns, ["稼働時間","hours","workinghours","h"])
    date_c  = detect_col(df_cost_raw.columns, ["稼働月-月次","稼働月 - 月次","稼働日","date"])

    if cons_c and hours_c and date_c:
        dc = df_cost_raw[[cons_c, hours_c, date_c]].copy()

        # 稼働時間を数値化
        dc[hours_c] = (dc[hours_c].astype(str)
                                   .str.replace(r"[^\d\.]", "", regex=True)
                                   .replace("", "0")
                                   .astype(float))

        dc[date_c] = pd.to_datetime(dc[date_c], errors="coerce")
        dc = dc.dropna(subset=[date_c]) 
        dc["年月表示"] = dc[date_c].dt.strftime("%y/%m")

        # ---------- 期間フィルタ：24/01 以降 ----------
        util_time_cols = [c for c in sorted(dc["年月表示"].unique())
                          if c >= "24/01"]
        dc = dc[dc["年月表示"].isin(util_time_cols)]

        # 月次稼働時間
        util_hours = (dc.pivot_table(index=cons_c, columns="年月表示",
                                     values=hours_c, aggfunc="sum",
                                     fill_value=0)
                      .reindex(columns=util_time_cols, fill_value=0))
        util_hours_pivot = util_hours.reset_index()

        # 標準稼働時間
        for col in util_time_cols:
            y, m = 2000 + int(col[:2]), int(col[3:])
            _, last = calendar.monthrange(y, m)
            workdays = pd.date_range(f"{y}-{m:02d}-01",
                                     f"{y}-{m:02d}-{last}", freq="B").size
            std_hours_row[col] = workdays * 8

        # チャージャビリティ %
        util_pct = util_hours.copy()
        for col in util_time_cols:
            util_pct[col] = util_pct[col] / std_hours_row[col]
        util_pct_pivot = util_pct.reset_index()
    else:
        st.sidebar.warning("稼働コストに コンサル名 / 稼働時間 / 日付 列が見つかりません。")

# ──────────────────────────────────────────────
# 画面表示
# ──────────────────────────────────────────────
tab1, tab2, tab3 = st.tabs(["📊 Chart view","📋 Table view","📈 Utilization"])

# ----- Chart view ------------------------------------------------------------
with tab1:
    st.subheader("月次合計売上・粗利")
    st.line_chart(pd.DataFrame({
        "月次売上合計":[int(summary_sales.loc[0,c].replace(',','')) for c in time_cols],
        "月次粗利合計":[int(summary_profit.loc[0,c].replace(',','')) for c in time_cols]
    }, index=time_cols))
    st.subheader("月次平均売上・粗利")
    st.line_chart(pd.DataFrame({
        "平均売上単価":[int(summary_sales.loc[1,c].replace(',','')) for c in time_cols],
        "平均粗利単価":[int(summary_profit.loc[1,c].replace(',','')) for c in time_cols]
    }, index=time_cols))
    st.subheader("案件数")
    st.bar_chart(pd.DataFrame({"案件数":count_series}, index=time_cols))

# ----- Table view ------------------------------------------------------------
with tab2:
    st.subheader("📄 プロジェクト収益一覧")
    # 表示列を拡張：レコードIDの後に日付最小・最大（YY/MM）を挿入
    show_cols = [
        "レコードID","日付（最小）","日付（最大）","取引先","取引名","取引担当者",
        "Industry","Industry詳細","提案商材",
        "売上高","人件費","外注費","交際費","旅費交通費",
        "粗利","粗利率"
    ]
    st.write("df_filteredの列名:", df_filtered.columns.tolist()) # この行を追加してデバッグ
    df_disp = df_filtered[show_cols].copy()
    # 日付最小・最大をYY/MM形式で表示
    for c in ["日付（最小）","日付（最大）"]:
        df_disp[c] = pd.to_datetime(df_disp[c], errors="coerce").dt.strftime("%y/%m")
    # 数値をカンマ区切りでフォーマット
    num_cols = ["売上高","人件費","外注費","交際費","旅費交通費","粗利"]
    for c in num_cols:
        df_disp[c] = df_disp[c].map(lambda x: f"{int(x):,}")
    # 粗利率をパーセント表示
    df_disp["粗利率"] = df_disp["粗利率"].map(lambda x: f"{x:.1f}%")

    st.dataframe(df_disp, use_container_width=True)
    st.download_button(
        "💾 粗利集計CSV",
        data=df_filtered.to_csv(index=False, encoding="utf-8-sig"),
        file_name="粗利集計.csv"
    )

    # 月次売上
    st.subheader("📋 月次売上")
    def _format(df):
        for c in time_cols:
            df[c] = df[c].map(lambda x: f"{int(x):,}")
        return df
    st.dataframe(_format(df_sales_p.copy()), use_container_width=True)
    st.download_button("💾 月次売上一覧CSV",
        data=df_sales_p.to_csv(index=False, encoding="cp932"),
        file_name="月次売上一覧.csv")

    # 月次粗利
    st.subheader("📋 月次粗利")
    st.dataframe(_format(df_profit_p.copy()), use_container_width=True)
    st.download_button("💾 月次粗利一覧CSV",
                       data=df_profit_p.to_csv(index=False, encoding="cp932"),
                       file_name="月次粗利一覧.csv")    

# ----- Utilization view ------------------------------------------------------
# ----- Utilization view ------------------------------------------------------
with tab3:
    # ① 標準稼働時間
    st.subheader("標準稼働時間 / 月")
    if std_hours_row:
        with st.expander("標準稼働時間", expanded=False):
            st.caption("平日日数 × 8h")
            st.table(pd.DataFrame([std_hours_row], index=["標準稼働時間(h)"]))
    else:
        st.info("稼働コストファイルに稼働時間が無いため利用率を計算できません。")

    # ② 月次稼働時間とチャージャビリティ
    if not util_hours_pivot.empty:
        st.subheader("月次稼働時間 (h)")
        st.dataframe(util_hours_pivot, use_container_width=True)

        st.subheader("月次稼働率(%)")
        pct_df = util_pct_pivot.copy()
        for c in util_time_cols:
            pct_df[c] = pct_df[c].map(lambda x: f"{x:.0%}")
        st.dataframe(pct_df, use_container_width=True)

        # ──────────── ここから詳細セクション ────────────
        st.markdown("---")
        st.subheader("コンサルタント別稼働率推移と詳細データ")

        # プルダウンでコンサル選択
        cons_col = util_hours_pivot.columns[0]
        names    = sorted(util_hours_pivot[cons_col].unique())
        sel      = st.selectbox("コンサルタントを選択", names)

        # 折れ線グラフ：選択者のチャージャビリティ
        sel_pct = util_pct_pivot.set_index(cons_col).loc[sel, util_time_cols]
        df_chart = pd.DataFrame({"稼働率": sel_pct.values}, index=util_time_cols)
        import altair as alt
        chart = (
            alt.Chart(df_chart.reset_index().melt("index"))
               .mark_line(point=True)
               .encode(
                   x=alt.X("index:N", title="年月"),
                   y=alt.Y("value:Q", axis=alt.Axis(format=".0%", title="稼働率")),
                   color=alt.value("#1f77b4")
               )
               .properties(height=300)
        )
        st.altair_chart(chart, use_container_width=True)

        # 詳細テーブル：該当コンサル×全月
        df_detail = df_cost_raw.copy()
        df_detail[date_c] = pd.to_datetime(df_detail[date_c], errors="coerce")
        df_detail["稼働月-月次"] = df_detail[date_c].dt.strftime("%y/%m")

        assign_c = detect_col(df_detail.columns,
                              ["アサイン履歴名","assignhistory","history"])

        df_det = df_detail[
            (df_detail[cons_col] == sel) &
            (df_detail["稼働月-月次"].isin(util_time_cols))
        ].copy()

        # 数値化 & フォーマット
        df_det[hours_c] = pd.to_numeric(df_det[hours_c], errors="coerce").fillna(0)
        df_det[cost_c]  = pd.to_numeric(df_det[cost_c], errors="coerce").fillna(0)
        df_det["稼働時間"]   = df_det[hours_c].map(lambda x: f"{x:,}")
        df_det["稼働コスト"] = df_det[cost_c].map(lambda x: f"{int(x):,}")

        # 列順・ヘッダーを日本語化
        df_det = df_det[["稼働月-月次", id_c, name_c, assign_c, "稼働時間", "稼働コスト"]]
        df_det.columns = ["稼働月-月次","取引ID","会社名","アサイン履歴名","稼働時間","稼働コスト"]

        st.dataframe(df_det, use_container_width=True)
        # ──────────── 詳細セクション ここまで ────────────

    else:
        st.info("利用率を計算できるデータがありません。")

