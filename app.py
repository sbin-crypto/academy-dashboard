import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import re
import numpy as np

# ─── Page Config ────────────────────────────────────────────────
st.set_page_config(
    page_title="학원 등록 현황 대시보드",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded",
)

st.markdown("""
<style>
    .metric-card {
        padding: 18px; border-radius: 12px; color: white;
        text-align: center; box-shadow: 0 4px 6px rgba(0,0,0,0.1);
    }
    .metric-card h3 { margin: 0; font-size: 13px; opacity: 0.9; }
    .metric-card h1 { margin: 4px 0; font-size: 28px; }
    .metric-card p  { margin: 0; font-size: 11px; opacity: 0.8; }
    .metric-blue   { background: linear-gradient(135deg,#2196F3,#1976D2); }
    .metric-green  { background: linear-gradient(135deg,#43A047,#2E7D32); }
    .metric-orange { background: linear-gradient(135deg,#FB8C00,#EF6C00); }
    .metric-purple { background: linear-gradient(135deg,#7B1FA2,#4A148C); }
    .metric-red    { background: linear-gradient(135deg,#E53935,#C62828); }
    .metric-teal   { background: linear-gradient(135deg,#00897B,#00695C); }
    div[data-testid="stSidebar"] { background-color: #f8f9fa; }
    .block-container { padding-top: 1rem; }
</style>
""", unsafe_allow_html=True)


# ─── School → Region / Gender mapping ──────────────────────────
SCHOOL_REGION = {
    '가락고':'서울','강동고':'서울','강일고':'서울','개포고':'서울',
    '건대부고':'서울','경복고':'서울','경희여고':'서울','고덕중':'서울',
    '광문고':'서울','광희중':'서울','길음중':'서울','누원고':'서울',
    '능동고':'서울','당곡고':'서울','대방중':'서울','대원고':'서울',
    '대원여고':'서울','대원외고':'서울','대일고':'서울','대일외고':'서울',
    '대진고':'서울','대진여고':'서울','덕수고':'서울','덕원고':'서울',
    '덕원여고':'서울','동대부고':'서울','동덕여고':'서울','동방고':'서울',
    '동북고':'서울','동작고':'서울','면목고':'서울','명덕고':'서울',
    '명덕여고':'서울','명덕외고':'서울','명지고':'서울','목동고':'서울',
    '목운중':'서울','문원중':'서울','문정고':'서울','반포고':'서울',
    '방산고':'서울','배명고':'서울','배제고':'서울','백신고':'서울',
    '보문고':'서울','보성고':'서울','봉은중':'서울','복자여고':'서울',
    '삼육고':'서울','삼육중':'서울','상명고':'서울','상명여고':'서울',
    '상암고':'서울','상일여고':'서울','상지여고':'서울','서울고':'서울',
    '서울여중':'서울','서일고':'서울','선일고':'서울','선일여고':'서울',
    '선정고':'서울','설화고':'서울','설현고':'서울','성광고':'서울',
    '성심여고':'서울','세일고':'서울','세화고':'서울','세화여고':'서울',
    '송곡여고':'서울','수도여고':'서울','숙명여고':'서울','숭실고':'서울',
    '숭의여고':'서울','쌘뽈여고':'서울','신길중':'서울','신동중':'서울',
    '신목고':'서울','양재고':'서울','양천고':'서울','양현고':'서울',
    '언주중':'서울','여의도여고':'서울','영동일고':'서울','영복여고':'서울',
    '영복여중':'서울','영신여고':'서울','영파여고':'서울','영훈고':'서울',
    '영락고':'서울','예당중':'서울','오금중':'서울','오성중':'서울',
    '외대부고':'서울','용강중':'서울','용문고':'서울','용산고':'서울',
    '은광여고':'서울','은성중':'서울','이대부고':'서울','이화여고':'서울',
    '이화여자외국어고':'서울','인명여고':'서울','재현고':'서울',
    '정광고':'서울','제일여고':'서울','중산고':'서울','중앙고':'서울',
    '중앙여고':'서울','진관고':'서울','진명여고':'서울','진선여고':'서울',
    '진선여중':'서울','창덕여고':'서울','창동중':'서울','청량중':'서울',
    '충암고':'서울','충훈고':'서울','교화고':'서울','태릉고':'서울',
    '하나고':'서울','한대부고':'서울','한빛고':'서울','한성고':'서울',
    '한영외고':'서울','한영중':'서울','해성여고':'서울','현대고':'서울',
    '혜성여고':'서울','홍대부여고':'서울','홍익사대부여고':'서울',
    '홍익여고':'서울','휘경여고':'서울','휘문고':'서울','효자고':'서울',
    '동일여고':'서울','비전중':'서울','관동중':'서울','위례고':'서울',
    '위례한빛고':'서울',
    '가좌고':'경기','감일고':'경기','경기외고':'경기','경문고':'경기',
    '계남고':'경기','고양국제고':'경기','고양외고':'경기','고촌고':'경기',
    '광덕고':'경기','구현고':'경기','김포외고':'경기','다정고':'경기',
    '대영고':'경기','도래울고':'경기','돌마고':'경기','동남고':'경기',
    '동백중':'경기','동패고':'경기','동화고':'경기','매원고':'경기',
    '매탄고':'경기','명신고':'경기','미사고':'경기','반송고':'경기',
    '백암고':'경기','백영고':'경기','백현고':'경기','보정고':'경기',
    '보평고':'경기','비봉고':'경기','산본고':'경기','삼괴고':'경기',
    '샛별중':'경기','서령고':'경기','서창고':'경기','서현고':'경기',
    '성남외고':'경기','성보고':'경기','성복고':'경기','성일여고':'경기',
    '세광고':'경기','송호고':'경기','수내고':'경기','신도고':'경기',
    '신봉고':'경기','신장고':'경기','양곡고':'경기','양명고':'경기',
    '양명여고':'경기','양정고':'경기','양지고':'경기','야탑고':'경기',
    '어정중':'경기','언남고':'경기','업성고':'경기','연송고':'경기',
    '운산고':'경기','운중고':'경기','은행고':'경기','자운고':'경기',
    '장기고':'경기','즉전고':'경기','증촌고':'경기','청석고':'경기',
    '청수고':'경기','청심국제고':'경기','태전고':'경기','하남풍산고':'경기',
    '한솔고':'경기','행신고':'경기','호계고':'경기','흥덕고':'경기',
    '남한고':'경기','능인고':'경기','사우고':'경기','안곡고':'경기',
    '금곡고':'부산','남강고':'부산','대동고':'부산','대연고':'부산',
    '덕계고':'부산','부광여고':'부산','부명고':'부산','부일외고':'부산',
    '부흥고':'부산','복성고':'부산','사직고':'부산','센텀고':'부산',
    '신서고':'부산','해강고':'부산','해동고':'부산','해운대고':'부산',
    '경구고':'대구','경명여고':'대구','경상여고':'대구','경신고':'대구',
    '경북고':'대구','경북사대부고':'대구','계성고':'대구','남산고':'대구',
    '대건고':'대구','대광중':'대구','대륜고':'대구','달성고':'대구',
    '범어고':'대구','성도고':'대구','시지고':'대구','영일고':'대구',
    '효성고':'대구',
    '미추홀외고':'인천','선인국제중':'인천','송도고':'인천',
    '연수여고':'인천','옥련여고':'인천',
    '광남고':'광주','광동고':'광주','금옥여고':'광주','금호고':'광주',
    '동성고':'광주','동신여고':'광주','문정여고':'광주','빛고을고':'광주',
    '상무고':'광주','선덕고':'광주','서문여고':'광주','서연고':'광주',
    '숭일고':'광주','송원여고':'광주','유일여고':'광주','진흥고':'광주',
    '비아고':'광주','조선대학교여자고등학교':'광주',
    '괴정고':'대전','대덕고':'대전','대신고':'대전','도개고':'대전',
    '만년고':'대전','반석고':'대전','서대전고':'대전','종촌고':'대전',
    '호수돈여고':'대전',
    '남목고':'울산',
    '서원고':'충북',
    '군북고':'충남','주성고':'충남','북일고':'충남','충남삼성고':'충남',
    '우성고':'충남',
    '기전여고':'전북','상산고':'전북','한일고':'전북',
    '경북외고':'경북','영진고':'경북',
    '경남외고':'경남','거창고':'경남','거창아림고':'경남','신광여고':'경남',
    '문성고':'강원','황지고':'강원',
    '한민고':'제주',
    '링컨중고':'해외','싱가폴화종국제학교':'해외','웨이하이':'해외',
}

CITY_REGION = {
    '서울':'서울','부산':'부산','대구':'대구','인천':'인천',
    '광주':'광주','대전':'대전','울산':'울산','세종':'세종',
    '경기':'경기','강원':'강원','충북':'충북','충남':'충남',
    '전북':'전북','전남':'전남','경북':'경북','경남':'경남','제주':'제주',
    '수원':'경기','성남':'경기','분당':'경기','용인':'경기','수지':'경기',
    '안양':'경기','안산':'경기','고양':'경기','일산':'경기','파주':'경기',
    '김포':'경기','의왕':'경기','과천':'경기','군포':'경기','시흥':'경기',
    '부천':'경기','하남':'경기','남양주':'경기','양주':'경기','오산':'경기',
    '화성':'경기','여주':'경기','동탄':'경기','곤지암':'경기','미사':'경기',
    '위례':'경기','세교':'경기','운정':'경기','금촌':'경기','평내':'경기',
    '신갈':'경기','안성':'경기',
    '강릉':'강원','원주':'강원','춘천':'강원','홍천':'강원','양구':'강원',
    '인제':'강원','치악':'강원','진부':'강원',
    '청주':'충북','충주':'충북','제천':'충북','옥천':'충북',
    '천안':'충남','아산':'충남','서산':'충남','공주':'충남',
    '예산':'충남','태안':'충남','서천':'충남','온양':'충남','배방':'충남',
    '전주':'전북','익산':'전북','군산':'전북','순창':'전북','이리':'전북',
    '목포':'전남','여수':'전남','순천':'전남','광양':'전남',
    '해남':'전남','장성':'전남','능주':'전남','창평':'전남',
    '포항':'경북','구미':'경북','안동':'경북','김천':'경북',
    '상주':'경북','영주':'경북','영덕':'경북',
    '창원':'경남','마산':'경남','진주':'경남','김해':'경남',
    '거제':'경남','양산':'경남','함안':'경남','함양':'경남',
    '합천':'경남','물금':'경남','연초':'경남','거창':'경남',
    '서귀포':'제주',
}


def _extract_region(s):
    if pd.isna(s):
        return '미분류'
    s = str(s).strip()
    for k, v in SCHOOL_REGION.items():
        if k in s:
            return v
    for k, v in CITY_REGION.items():
        if s.startswith(k) or f' {k}' in s:
            return v
    for k, v in CITY_REGION.items():
        if k in s:
            return v
    return '미분류'


def _extract_gender(s):
    if pd.notna(s):
        s = str(s)
        if '여고' in s or '여중' in s or '여자' in s:
            return '여'
    return '미분류'


# ─── Data Loading ───────────────────────────────────────────────
@st.cache_data
def load_data():
    import os
    data_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'data.csv')
    df = pd.read_csv(data_path, encoding='utf-8')
    df.columns = [
        '담당자','학원','학생명','학교_학년','커리큘럼',
        '정규여부','등록결제여부','등록일','종강일','등록금액',
        '특이사항','학부모연락처','학생연락처','현금영수증번호',
        '발급여부','비고_참고자료','선생님배정여부','자료수령',
        '첫수업일','팀채팅','수업시작여부','비고','참고자료전달'
    ]

    # Date
    def parse_date(d):
        if pd.isna(d): return pd.NaT
        m = re.match(r'(\d{4})\.\s*(\d{1,2})\.\s*(\d{1,2})', str(d).strip())
        if m:
            try: return pd.Timestamp(int(m.group(1)), int(m.group(2)), int(m.group(3)))
            except: return pd.NaT
        return pd.NaT
    df['등록일_parsed'] = df['등록일'].apply(parse_date)

    # Amount
    def parse_amount(a):
        if pd.isna(a): return 0
        try: return int(float(str(a).replace(',','')))
        except: return 0
    df['등록금액_parsed'] = df['등록금액'].apply(parse_amount)

    # Grade
    def extract_grade(v):
        if pd.isna(v): return '미분류'
        v = str(v)
        m = re.search(r'(고[123])', v)
        if m: return m.group(1)
        m = re.search(r'(중[123])', v)
        if m: return m.group(1)
        if '졸업' in v: return '졸업생'
        if '재수' in v or 'N수' in v or 'n수' in v: return 'N수생'
        if '반수' in v: return '반수생'
        if '예비' in v: return '예비'
        return '미분류'
    df['학년'] = df['학교_학년'].apply(extract_grade)

    # Time
    df['연도'] = df['등록일_parsed'].dt.year
    df['월']  = df['등록일_parsed'].dt.month
    df['연월'] = df['등록일_parsed'].dt.to_period('M').astype(str)

    def get_season(m):
        if pd.isna(m): return '미분류'
        m = int(m)
        if m in (3,4,5):   return '봄 (3-5월)'
        if m in (6,7,8):   return '여름 (6-8월)'
        if m in (9,10,11): return '가을 (9-11월)'
        if m in (12,1,2):  return '겨울 (12-2월)'
        return '미분류'
    df['시즌'] = df['월'].apply(get_season)

    def get_semester(row):
        if pd.isna(row['월']) or pd.isna(row['연도']): return '미분류'
        m, y = int(row['월']), int(row['연도'])
        if m in (3,4,5,6,7): return f'{y} 1학기'
        if m == 8:           return f'{y} 여름방학'
        if m in (9,10,11,12):return f'{y} 2학기'
        if m in (1,2):       return f'{y} 겨울방학'
        return '미분류'
    df['학기'] = df.apply(get_semester, axis=1)

    # Program
    def norm(c):
        if pd.isna(c): return '미분류'
        c = str(c).strip()
        if c == '세특 특강 패키지 패키지': return '세특 특강 패키지'
        if c in ('-','학년'): return '미분류'
        return c
    df['프로그램'] = df['커리큘럼'].apply(norm)

    def prog_cat(p):
        if '정규' in p and '메디컬' in p: return '정규(메디컬)'
        if '정규' in p and ('인문' in p or '이공' in p): return '정규(인문/이공)'
        if '정규' in p: return '정규(기타)'
        if '대입' in p and '면접' in p: return '대입(면접)'
        if '대입' in p and '자소서' in p: return '대입(자소서)'
        if '고입' in p and '자소서' in p: return '고입(자소서)'
        if '고입' in p and '면접' in p: return '고입(면접)'
        if '고입' in p and '정규' in p: return '고입(정규)'
        if '고입' in p: return '고입(기타)'
        if '수시' in p: return '수시컨설팅'
        if '정시' in p: return '정시컨설팅'
        if '합진' in p: return '합격진단컨설팅'
        if '로드맵' in p: return '로드맵 특강'
        if '세특' in p: return '세특 특강'
        if '보고서' in p: return '보고서'
        if '재등록' in p: return '재등록'
        if '추가등록' in p: return '추가등록'
        if '윈터' in p: return '윈터스쿨'
        if '추석' in p: return '특강(기타)'
        if '1회' in p: return '1회 특강'
        return '기타'
    df['프로그램_카테고리'] = df['프로그램'].apply(prog_cat)

    # Region & Gender
    df['지역'] = df['학교_학년'].apply(_extract_region)
    df['성별'] = df['학교_학년'].apply(_extract_gender)

    # 광역 그룹
    def region_group(r):
        if r in ('서울','경기','인천'): return '수도권'
        if r in ('부산','대구','울산','경북','경남'): return '영남권'
        if r in ('광주','전북','전남'): return '호남권'
        if r in ('대전','충북','충남','세종'): return '충청권'
        if r == '강원': return '강원권'
        if r == '제주': return '제주'
        if r == '해외': return '해외'
        return '미분류'
    df['권역'] = df['지역'].apply(region_group)

    return df

df_all = load_data()
df = df_all[df_all['등록일_parsed'].notna()].copy()


# ─── Sidebar Filters ───────────────────────────────────────────
st.sidebar.markdown("## 🔍 필터")

available_years = sorted(df['연도'].dropna().unique().astype(int))
selected_years = st.sidebar.multiselect("연도", available_years, default=available_years)

available_seasons = ['봄 (3-5월)','여름 (6-8월)','가을 (9-11월)','겨울 (12-2월)']
selected_seasons = st.sidebar.multiselect("시즌", available_seasons, default=available_seasons)

available_academies = sorted(df['학원'].dropna().unique())
selected_academies = st.sidebar.multiselect(
    "학원", available_academies,
    default=[a for a in available_academies if a != '환불']
)

available_programs = sorted(df['프로그램_카테고리'].unique())
selected_programs = st.sidebar.multiselect("프로그램", available_programs, default=available_programs)

grade_order = ['중2','중3','고1','고2','고3','졸업생','N수생','반수생','예비','미분류']
available_grades = [g for g in grade_order if g in df['학년'].unique()]
selected_grades = st.sidebar.multiselect("학년", available_grades, default=available_grades)

# Region filter
available_regions = sorted([r for r in df['지역'].unique() if r != '미분류'])
available_regions.append('미분류')
selected_regions = st.sidebar.multiselect("지역", available_regions, default=available_regions)

exclude_refund = st.sidebar.checkbox("환불 제외", value=True)

mask = (
    df['연도'].isin(selected_years) &
    df['시즌'].isin(selected_seasons) &
    df['학원'].isin(selected_academies) &
    df['프로그램_카테고리'].isin(selected_programs) &
    df['학년'].isin(selected_grades) &
    df['지역'].isin(selected_regions)
)
if exclude_refund:
    mask = mask & (df['학원'] != '환불')
filtered = df[mask].copy()


# ─── Title & KPI ────────────────────────────────────────────────
st.markdown("# 📊 학원 프로그램 등록 현황 대시보드")
st.markdown(
    f"**데이터 기간**: {df['등록일_parsed'].min().strftime('%Y.%m.%d')} ~ "
    f"{df['등록일_parsed'].max().strftime('%Y.%m.%d')} | "
    f"**필터 적용**: {len(filtered):,}건"
)

c1, c2, c3, c4, c5, c6 = st.columns(6)
total_reg = len(filtered)
total_rev = filtered['등록금액_parsed'].sum()
avg_rev   = filtered['등록금액_parsed'].mean() if total_reg else 0
uniq_stu  = filtered['학생명'].nunique()
cur_m     = pd.Timestamp.now().to_period('M')
this_m    = filtered[filtered['등록일_parsed'].dt.to_period('M') == cur_m]
region_ct = filtered[filtered['지역'] != '미분류']['지역'].nunique()

for col, cls, title, val, sub in [
    (c1,'metric-blue',  '총 등록',    f'{total_reg:,}건',            '전체 기간'),
    (c2,'metric-green', '총 매출',    f'{total_rev/10000:,.0f}만원', '등록금 합계'),
    (c3,'metric-orange','평균 등록금', f'{avg_rev/10000:,.1f}만원',  '건당 평균'),
    (c4,'metric-purple','고유 학생',   f'{uniq_stu:,}명',           '중복 제거'),
    (c5,'metric-red',   '이번 달',    f'{len(this_m):,}건',         str(cur_m)),
    (c6,'metric-teal',  '지역 수',    f'{region_ct}개',             '분류 완료'),
]:
    with col:
        st.markdown(
            f'<div class="metric-card {cls}"><h3>{title}</h3>'
            f'<h1>{val}</h1><p>{sub}</p></div>',
            unsafe_allow_html=True
        )

st.markdown("---")


# ─── Tabs ───────────────────────────────────────────────────────
tab1, tab2, tab3, tab4, tab5, tab6, tab7, tab8 = st.tabs([
    "📈 시계열 추이", "📊 프로그램 분석", "🎓 학년 분석",
    "🏫 학원별 분석", "💰 매출 분석",
    "🗺️ 지역별 분석", "👫 성별 분석", "📋 상세 데이터"
])


# ════════════ TAB 1: Time Series ═════════════════════════════════
with tab1:
    st.markdown("### 월별 등록 추이")
    monthly = filtered.groupby('연월').size().reset_index(name='등록수').sort_values('연월')
    fig = px.bar(monthly, x='연월', y='등록수', text='등록수',
                 color_discrete_sequence=['#2196F3'])
    fig.update_traces(textposition='outside', textfont_size=10)
    fig.update_layout(height=400, xaxis_title='', yaxis_title='등록 건수',
                      xaxis=dict(tickangle=-45), margin=dict(t=20))
    st.plotly_chart(fig, use_container_width=True)

    st.markdown("### 연도별 월간 등록 비교 (YoY)")
    ca, cb = st.columns([3,1])
    with ca:
        yoy = filtered.groupby(['연도','월']).size().reset_index(name='등록수')
        yoy['연도'] = yoy['연도'].astype(int).astype(str)
        fig2 = px.line(yoy, x='월', y='등록수', color='연도',
                       markers=True, line_shape='spline',
                       color_discrete_sequence=px.colors.qualitative.Set1)
        fig2.update_layout(height=400,
            xaxis=dict(tickmode='array', tickvals=list(range(1,13)),
                       ticktext=[f'{m}월' for m in range(1,13)], title=''),
            yaxis_title='등록 건수', legend_title='연도', margin=dict(t=20))
        st.plotly_chart(fig2, use_container_width=True)
    with cb:
        ys = filtered.groupby('연도').agg(
            등록수=('학생명','count'), 매출=('등록금액_parsed','sum'),
            평균=('등록금액_parsed','mean')).reset_index()
        ys['연도'] = ys['연도'].astype(int)
        ys['매출'] = (ys['매출']/10000).round(0).astype(int).astype(str)+'만'
        ys['평균'] = (ys['평균']/10000).round(1).astype(str)+'만'
        st.markdown("**연도별 요약**")
        st.dataframe(ys, hide_index=True, use_container_width=True)

    st.markdown("### 누적 등록 추이")
    daily = filtered.groupby('등록일_parsed').size().reset_index(name='n').sort_values('등록일_parsed')
    daily['누적'] = daily['n'].cumsum()
    fig3 = px.area(daily, x='등록일_parsed', y='누적', color_discrete_sequence=['#7B1FA2'])
    fig3.update_layout(height=350, xaxis_title='', yaxis_title='누적', margin=dict(t=20))
    st.plotly_chart(fig3, use_container_width=True)

    st.markdown("### 연도 × 월 히트맵")
    hm = filtered.groupby(['연도','월']).size().reset_index(name='n')
    hmp = hm.pivot(index='연도', columns='월', values='n').fillna(0)
    hmp.columns = [f'{int(c)}월' for c in hmp.columns]
    hmp.index = hmp.index.astype(int)
    fig4 = px.imshow(hmp.values, x=hmp.columns.tolist(), y=hmp.index.tolist(),
                     labels=dict(color="등록수"), color_continuous_scale='YlOrRd',
                     text_auto=True, aspect='auto')
    fig4.update_layout(height=300, margin=dict(t=20))
    st.plotly_chart(fig4, use_container_width=True)


# ════════════ TAB 2: Program ═════════════════════════════════════
with tab2:
    st.markdown("### 프로그램별 등록 현황")
    cp1, cp2 = st.columns(2)
    pc = filtered['프로그램_카테고리'].value_counts().reset_index()
    pc.columns = ['프로그램','등록수']
    with cp1:
        fig = px.bar(pc, x='등록수', y='프로그램', orientation='h', text='등록수',
                     color='프로그램', color_discrete_sequence=px.colors.qualitative.Plotly)
        fig.update_traces(textposition='outside')
        fig.update_layout(height=500, showlegend=False,
                          yaxis=dict(categoryorder='total ascending'),
                          xaxis_title='등록 건수', yaxis_title='', margin=dict(t=20,l=10))
        st.plotly_chart(fig, use_container_width=True)
    with cp2:
        fig = px.pie(pc, values='등록수', names='프로그램', hole=.4,
                     color_discrete_sequence=px.colors.qualitative.Plotly)
        fig.update_traces(textposition='inside', textinfo='percent+label')
        fig.update_layout(height=500, margin=dict(t=20))
        st.plotly_chart(fig, use_container_width=True)

    st.markdown("### 프로그램별 월별 등록 추이")
    top8 = filtered['프로그램_카테고리'].value_counts().head(8).index.tolist()
    pm = filtered[filtered['프로그램_카테고리'].isin(top8)].groupby(
        ['연월','프로그램_카테고리']).size().reset_index(name='n').sort_values('연월')
    fig = px.line(pm, x='연월', y='n', color='프로그램_카테고리', markers=True,
                  color_discrete_sequence=px.colors.qualitative.Plotly)
    fig.update_layout(height=450, xaxis=dict(tickangle=-45, title=''),
                      yaxis_title='등록 건수', legend_title='프로그램', margin=dict(t=20))
    st.plotly_chart(fig, use_container_width=True)

    st.markdown("### 프로그램 × 연도 매트릭스")
    py = filtered.groupby(['프로그램_카테고리','연도']).size().reset_index(name='n')
    pyp = py.pivot(index='프로그램_카테고리', columns='연도', values='n').fillna(0)
    pyp.columns = [str(int(c)) for c in pyp.columns]
    pyp['합계'] = pyp.sum(axis=1)
    pyp = pyp.sort_values('합계', ascending=False)
    st.dataframe(pyp.style.format('{:.0f}').background_gradient(cmap='Blues', axis=None),
                 use_container_width=True, height=450)


# ════════════ TAB 3: Grade ═══════════════════════════════════════
with tab3:
    st.markdown("### 학년별 등록 분포")
    gdo = ['중2','중3','고1','고2','고3','졸업생','N수생','반수생','미분류']
    cg1, cg2 = st.columns(2)
    gc = filtered['학년'].value_counts().reset_index(); gc.columns=['학년','등록수']
    gc['o'] = gc['학년'].apply(lambda x: gdo.index(x) if x in gdo else 99)
    gc = gc.sort_values('o')
    with cg1:
        fig = px.bar(gc, x='학년', y='등록수', text='등록수', color='학년',
                     color_discrete_sequence=px.colors.qualitative.Pastel)
        fig.update_traces(textposition='outside')
        fig.update_layout(height=400, showlegend=False, xaxis_title='', yaxis_title='', margin=dict(t=20))
        st.plotly_chart(fig, use_container_width=True)
    with cg2:
        fig = px.pie(gc, values='등록수', names='학년', hole=.4,
                     color_discrete_sequence=px.colors.qualitative.Pastel)
        fig.update_traces(textposition='inside', textinfo='percent+label')
        fig.update_layout(height=400, margin=dict(t=20))
        st.plotly_chart(fig, use_container_width=True)

    st.markdown("### 학년 × 프로그램 교차 분석")
    gp = filtered.groupby(['학년','프로그램_카테고리']).size().reset_index(name='n')
    fig = px.bar(gp, x='학년', y='n', color='프로그램_카테고리', barmode='stack',
                 color_discrete_sequence=px.colors.qualitative.Plotly,
                 category_orders={'학년': gdo})
    fig.update_layout(height=450, xaxis_title='', yaxis_title='등록 건수',
                      legend_title='프로그램', margin=dict(t=20))
    st.plotly_chart(fig, use_container_width=True)

    st.markdown("### 학년별 연도 추이")
    gy = filtered.groupby(['연도','학년']).size().reset_index(name='n')
    gy['연도'] = gy['연도'].astype(int).astype(str)
    mg = ['고1','고2','고3','중3']
    fig = px.bar(gy[gy['학년'].isin(mg)], x='연도', y='n', color='학년',
                 barmode='group', color_discrete_sequence=px.colors.qualitative.Safe,
                 category_orders={'학년': mg})
    fig.update_layout(height=400, xaxis_title='', yaxis_title='등록 건수', margin=dict(t=20))
    st.plotly_chart(fig, use_container_width=True)


# ════════════ TAB 4: Academy ═════════════════════════════════════
with tab4:
    st.markdown("### 학원(브랜드)별 분석")
    ca1, ca2 = st.columns(2)
    ac = filtered['학원'].value_counts().reset_index(); ac.columns=['학원','등록수']
    acad_colors = ['#2196F3','#4CAF50','#FF9800','#E91E63']
    with ca1:
        fig = px.bar(ac, x='학원', y='등록수', text='등록수', color='학원',
                     color_discrete_sequence=acad_colors)
        fig.update_traces(textposition='outside')
        fig.update_layout(height=400, showlegend=False, xaxis_title='', yaxis_title='', margin=dict(t=20))
        st.plotly_chart(fig, use_container_width=True)
    with ca2:
        ar = filtered.groupby('학원')['등록금액_parsed'].sum().reset_index()
        ar.columns=['학원','매출']; ar['만'] = ar['매출']/10000
        fig = px.bar(ar, x='학원', y='만', text=ar['만'].apply(lambda x: f'{x:,.0f}만'),
                     color='학원', color_discrete_sequence=acad_colors)
        fig.update_traces(textposition='outside')
        fig.update_layout(height=400, showlegend=False, xaxis_title='', yaxis_title='매출(만원)', margin=dict(t=20))
        st.plotly_chart(fig, use_container_width=True)

    st.markdown("### 학원별 프로그램 구성")
    ap = filtered.groupby(['학원','프로그램_카테고리']).size().reset_index(name='n')
    fig = px.bar(ap, x='학원', y='n', color='프로그램_카테고리', barmode='stack',
                 color_discrete_sequence=px.colors.qualitative.Plotly)
    fig.update_layout(height=450, xaxis_title='', yaxis_title='', legend_title='프로그램', margin=dict(t=20))
    st.plotly_chart(fig, use_container_width=True)

    st.markdown("### 학원별 월간 등록 추이")
    am = filtered.groupby(['연월','학원']).size().reset_index(name='n').sort_values('연월')
    fig = px.line(am, x='연월', y='n', color='학원', markers=True,
                  color_discrete_sequence=acad_colors)
    fig.update_layout(height=400, xaxis=dict(tickangle=-45, title=''),
                      yaxis_title='', margin=dict(t=20))
    st.plotly_chart(fig, use_container_width=True)


# ════════════ TAB 5: Revenue ═════════════════════════════════════
with tab5:
    st.markdown("### 월별 매출 추이")
    mr = filtered.groupby('연월')['등록금액_parsed'].sum().reset_index()
    mr.columns=['연월','매출']; mr=mr.sort_values('연월'); mr['만']=mr['매출']/10000
    fig = px.bar(mr, x='연월', y='만', text=mr['만'].apply(lambda x: f'{x:,.0f}'),
                 color_discrete_sequence=['#43A047'])
    fig.update_traces(textposition='outside', textfont_size=9)
    fig.update_layout(height=400, xaxis=dict(tickangle=-45, title=''),
                      yaxis_title='매출(만원)', margin=dict(t=20))
    st.plotly_chart(fig, use_container_width=True)

    st.markdown("### 연도별 월간 매출 비교")
    ry = filtered.groupby(['연도','월'])['등록금액_parsed'].sum().reset_index()
    ry['만']=ry['등록금액_parsed']/10000; ry['연도']=ry['연도'].astype(int).astype(str)
    fig = px.line(ry, x='월', y='만', color='연도', markers=True, line_shape='spline',
                  color_discrete_sequence=px.colors.qualitative.Set1)
    fig.update_layout(height=400,
        xaxis=dict(tickmode='array', tickvals=list(range(1,13)),
                   ticktext=[f'{m}월' for m in range(1,13)], title=''),
        yaxis_title='매출(만원)', legend_title='연도', margin=dict(t=20))
    st.plotly_chart(fig, use_container_width=True)

    cr1, cr2 = st.columns(2)
    with cr1:
        st.markdown("### 프로그램별 매출")
        pr = filtered.groupby('프로그램_카테고리')['등록금액_parsed'].sum().reset_index()
        pr.columns=['프로그램','매출']; pr['만']=pr['매출']/10000; pr=pr.sort_values('만')
        fig = px.bar(pr, x='만', y='프로그램', orientation='h',
                     text=pr['만'].apply(lambda x: f'{x:,.0f}만'),
                     color_discrete_sequence=['#FB8C00'])
        fig.update_traces(textposition='outside')
        fig.update_layout(height=500, xaxis_title='매출(만원)', yaxis_title='', margin=dict(t=20,l=10))
        st.plotly_chart(fig, use_container_width=True)
    with cr2:
        st.markdown("### 프로그램별 평균 등록금")
        pa = filtered.groupby('프로그램_카테고리')['등록금액_parsed'].mean().reset_index()
        pa.columns=['프로그램','평균']; pa['만']=pa['평균']/10000; pa=pa.sort_values('만')
        fig = px.bar(pa, x='만', y='프로그램', orientation='h',
                     text=pa['만'].apply(lambda x: f'{x:,.1f}만'),
                     color_discrete_sequence=['#7B1FA2'])
        fig.update_traces(textposition='outside')
        fig.update_layout(height=500, xaxis_title='평균(만원)', yaxis_title='', margin=dict(t=20,l=10))
        st.plotly_chart(fig, use_container_width=True)


# ════════════ TAB 6: Region ══════════════════════════════════════
with tab6:
    st.markdown("### 지역별 등록 분석")
    region_data = filtered[filtered['지역'] != '미분류']
    st.caption(f"지역 분류 완료: {len(region_data):,}건 / 전체 {len(filtered):,}건 "
               f"({len(region_data)/len(filtered)*100:.1f}%)")

    cr1, cr2 = st.columns(2)
    with cr1:
        rc = region_data['지역'].value_counts().reset_index(); rc.columns=['지역','등록수']
        fig = px.bar(rc, x='등록수', y='지역', orientation='h', text='등록수',
                     color='지역', color_discrete_sequence=px.colors.qualitative.Plotly)
        fig.update_traces(textposition='outside')
        fig.update_layout(height=550, showlegend=False,
                          yaxis=dict(categoryorder='total ascending'),
                          xaxis_title='등록 건수', yaxis_title='', margin=dict(t=20,l=10))
        st.plotly_chart(fig, use_container_width=True)
    with cr2:
        rg = region_data['권역'].value_counts().reset_index(); rg.columns=['권역','등록수']
        fig = px.pie(rg, values='등록수', names='권역', hole=.4,
                     color_discrete_sequence=px.colors.qualitative.Bold)
        fig.update_traces(textposition='inside', textinfo='percent+label')
        fig.update_layout(height=550, margin=dict(t=20))
        st.plotly_chart(fig, use_container_width=True)

    st.markdown("### 지역별 연도 추이")
    top_regions = region_data['지역'].value_counts().head(8).index.tolist()
    ry = region_data[region_data['지역'].isin(top_regions)].groupby(
        ['연월','지역']).size().reset_index(name='n').sort_values('연월')
    fig = px.line(ry, x='연월', y='n', color='지역', markers=True,
                  color_discrete_sequence=px.colors.qualitative.Plotly)
    fig.update_layout(height=400, xaxis=dict(tickangle=-45, title=''),
                      yaxis_title='등록 건수', legend_title='지역', margin=dict(t=20))
    st.plotly_chart(fig, use_container_width=True)

    st.markdown("### 지역 × 프로그램 교차 분석")
    rp = region_data.groupby(['지역','프로그램_카테고리']).size().reset_index(name='n')
    top5r = region_data['지역'].value_counts().head(7).index.tolist()
    rp5 = rp[rp['지역'].isin(top5r)]
    fig = px.bar(rp5, x='지역', y='n', color='프로그램_카테고리', barmode='stack',
                 color_discrete_sequence=px.colors.qualitative.Plotly)
    fig.update_layout(height=450, xaxis_title='', yaxis_title='등록 건수',
                      legend_title='프로그램', margin=dict(t=20))
    st.plotly_chart(fig, use_container_width=True)

    st.markdown("### 지역 × 학년 교차 분석")
    rg2 = region_data.groupby(['지역','학년']).size().reset_index(name='n')
    rg2_top = rg2[rg2['지역'].isin(top5r)]
    fig = px.bar(rg2_top, x='지역', y='n', color='학년', barmode='group',
                 color_discrete_sequence=px.colors.qualitative.Safe,
                 category_orders={'학년': ['고1','고2','고3','중3']})
    fig.update_layout(height=400, xaxis_title='', yaxis_title='등록 건수', margin=dict(t=20))
    st.plotly_chart(fig, use_container_width=True)

    st.markdown("### 지역 × 연도 매트릭스")
    ry_mat = region_data.groupby(['지역','연도']).size().reset_index(name='n')
    ry_piv = ry_mat.pivot(index='지역', columns='연도', values='n').fillna(0)
    ry_piv.columns = [str(int(c)) for c in ry_piv.columns]
    ry_piv['합계'] = ry_piv.sum(axis=1)
    ry_piv = ry_piv.sort_values('합계', ascending=False)
    st.dataframe(ry_piv.style.format('{:.0f}').background_gradient(cmap='YlGn', axis=None),
                 use_container_width=True, height=500)


# ════════════ TAB 7: Gender ══════════════════════════════════════
with tab7:
    st.markdown("### 성별 분석")
    st.caption("⚠️ 성별은 학교명(여고/여중)으로만 자동 추출되어, '여' 외에는 미분류입니다. "
               "정확한 분석을 위해 원본 데이터에 성별 컬럼을 직접 추가하시는 것을 권장합니다.")

    female = filtered[filtered['성별'] == '여']
    st.markdown(f"**여학생 확인**: {len(female):,}건 / 전체 {len(filtered):,}건")

    if len(female) > 0:
        cg1, cg2 = st.columns(2)
        with cg1:
            st.markdown("### 여학생 프로그램 분포")
            fp = female['프로그램_카테고리'].value_counts().reset_index()
            fp.columns = ['프로그램','등록수']
            fig = px.bar(fp, x='등록수', y='프로그램', orientation='h', text='등록수',
                         color_discrete_sequence=['#E91E63'])
            fig.update_traces(textposition='outside')
            fig.update_layout(height=400, showlegend=False,
                              yaxis=dict(categoryorder='total ascending'),
                              xaxis_title='', yaxis_title='', margin=dict(t=20,l=10))
            st.plotly_chart(fig, use_container_width=True)
        with cg2:
            st.markdown("### 여학생 학년 분포")
            fg = female['학년'].value_counts().reset_index(); fg.columns=['학년','등록수']
            fig = px.pie(fg, values='등록수', names='학년', hole=.4,
                         color_discrete_sequence=px.colors.qualitative.Pastel1)
            fig.update_traces(textposition='inside', textinfo='percent+label')
            fig.update_layout(height=400, margin=dict(t=20))
            st.plotly_chart(fig, use_container_width=True)

        st.markdown("### 여학생 월별 등록 추이")
        fm = female.groupby('연월').size().reset_index(name='n').sort_values('연월')
        fig = px.bar(fm, x='연월', y='n', text='n', color_discrete_sequence=['#E91E63'])
        fig.update_traces(textposition='outside', textfont_size=9)
        fig.update_layout(height=350, xaxis=dict(tickangle=-45, title=''),
                          yaxis_title='등록 건수', margin=dict(t=20))
        st.plotly_chart(fig, use_container_width=True)

        st.markdown("### 여학생 지역 분포")
        fr = female[female['지역']!='미분류']['지역'].value_counts().reset_index()
        fr.columns=['지역','등록수']
        fig = px.bar(fr, x='지역', y='등록수', text='등록수',
                     color_discrete_sequence=['#E91E63'])
        fig.update_traces(textposition='outside')
        fig.update_layout(height=350, xaxis_title='', yaxis_title='', margin=dict(t=20))
        st.plotly_chart(fig, use_container_width=True)


# ════════════ TAB 8: Detail ══════════════════════════════════════
with tab8:
    st.markdown("### 필터링된 상세 데이터")
    dcols = ['등록일','학원','학년','프로그램_카테고리','프로그램',
             '등록금액','지역','권역','성별','학기','시즌','담당자']
    st.dataframe(
        filtered[dcols].sort_values('등록일_parsed', ascending=False),
        use_container_width=True, height=600
    )
    csv = filtered[dcols].to_csv(index=False).encode('utf-8-sig')
    st.download_button("📥 CSV 다운로드", csv, "filtered_data.csv", "text/csv")


# ─── Footer ─────────────────────────────────────────────────────
st.markdown("---")
st.markdown(
    '<div style="text-align:center;color:#999;font-size:12px;">'
    '학원 프로그램 등록 현황 대시보드 | 데이터 기반 의사결정을 위한 분석 도구</div>',
    unsafe_allow_html=True
)
