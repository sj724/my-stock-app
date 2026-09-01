import streamlit as st
import yfinance as yf
import plotly.graph_objects as go
from datetime import datetime, timedelta

# ---------------------------
# 페이지 기본 설정
# ---------------------------
st.set_page_config(
    page_title="주가 조회",
    page_icon="📈",
    layout="centered",
)

# ---------------------------
# 제목과 간단한 설명
# ---------------------------
st.title("📈 내 손안의 주가 그래프")
st.write(
    "종목 코드를 입력하면 주가 흐름을 그래프로 보여드려요. "
    "두 종목을 나란히 비교해볼 수도 있어요. "
    "예: 삼성전자는 `005930.KS`, 애플은 `AAPL` 이렇게 입력해보세요 :)"
)

# ---------------------------
# 종목 코드 입력창 2개 (나란히 배치)
# ---------------------------
input_col1, input_col2 = st.columns(2)

with input_col1:
    ticker_input_1 = st.text_input(
        "종목 1",
        value="AAPL",
        placeholder="예: AAPL (애플)",
    )

with input_col2:
    ticker_input_2 = st.text_input(
        "종목 2 (선택)",
        value="",
        placeholder="예: 005930.KS (삼성전자)",
    )

# 입력값 앞뒤 공백 제거 및 대문자로 변환 (티커는 보통 대문자를 사용)
ticker_1 = ticker_input_1.strip().upper()
ticker_2 = ticker_input_2.strip().upper()

# ---------------------------
# 기간 선택 버튼 (1개월 / 6개월 / 1년 / 5년)
# ---------------------------
st.write("**조회 기간을 선택하세요**")

# 화면에 보여줄 이름과 yfinance에 넘길 기간 코드를 짝지어 관리
period_options = {
    "1개월": "1mo",
    "6개월": "6mo",
    "1년": "1y",
    "5년": "5y",
}

# st.radio를 버튼처럼 가로로 보여줌 (기본값은 "1년")
selected_period_label = st.radio(
    "기간 선택",
    options=list(period_options.keys()),
    index=2,  # "1년"이 기본 선택
    horizontal=True,
    label_visibility="collapsed",
)
selected_period = period_options[selected_period_label]

# ---------------------------
# 조회 버튼
# ---------------------------
search_clicked = st.button("조회하기", type="primary")


def load_stock_data(ticker: str, period: str):
    """
    yfinance로 주가 데이터를 불러오는 함수.
    성공하면 (히스토리 데이터프레임, 회사 이름)을 반환하고,
    데이터가 없으면 (None, None)을 반환한다.
    """
    stock = yf.Ticker(ticker)
    history = stock.history(period=period)

    if history.empty:
        return None, None

    # 회사 이름을 가져오되, 실패하면 티커 코드로 대체
    try:
        company_name = stock.info.get("longName", ticker)
    except Exception:
        company_name = ticker

    return history, company_name


def show_metric_cards(ticker: str, company_name: str, history):
    """
    현재가, 기간 등락률, 최고가, 최저가, 평균가 카드를 보여주는 함수.
    """
    start_price = history["Close"].iloc[0]
    current_price = history["Close"].iloc[-1]
    change_percent = (current_price - start_price) / start_price * 100

    high_price = history["Close"].max()
    low_price = history["Close"].min()
    avg_price = history["Close"].mean()

    st.subheader(f"{company_name} ({ticker})")

    # 현재가, 등락률 카드
    col1, col2 = st.columns(2)
    with col1:
        st.metric(label="현재가", value=f"{current_price:,.2f}")
    with col2:
        st.metric(
            label=f"{selected_period_label} 등락률",
            value=f"{change_percent:,.2f}%",
            delta=f"{change_percent:,.2f}%",
        )

    # 최고가, 최저가, 평균가 카드
    col3, col4, col5 = st.columns(3)
    with col3:
        st.metric(label="최고가", value=f"{high_price:,.2f}")
    with col4:
        st.metric(label="최저가", value=f"{low_price:,.2f}")
    with col5:
        st.metric(label="평균가", value=f"{avg_price:,.2f}")


# 버튼을 누르고, 최소 하나의 종목이 입력되어 있으면 실행
if search_clicked and (ticker_1 or ticker_2):
    with st.spinner("주가 정보를 불러오는 중이에요..."):
        try:
            # 입력된 종목들만 리스트로 정리 (빈 칸은 제외)
            tickers_to_load = [t for t in [ticker_1, ticker_2] if t]

            results = {}  # 티커별 (history, company_name) 저장
            failed_tickers = []  # 조회에 실패한 티커 모음

            for t in tickers_to_load:
                history, company_name = load_stock_data(t, selected_period)
                if history is None:
                    failed_tickers.append(t)
                else:
                    results[t] = (history, company_name)

            # 조회에 실패한 종목이 있으면 안내
            if failed_tickers:
                st.error(
                    "다음 종목의 정보를 찾을 수 없어요: "
                    + ", ".join(failed_tickers)
                    + " (종목 코드를 다시 확인해주세요. 예: 005930.KS, AAPL)"
                )

            # 정상적으로 불러온 종목이 있으면 그래프와 카드 표시
            if results:
                # ---------------------------
                # Plotly 꺾은선 그래프 (두 종목 비교 가능)
                # ---------------------------
                fig = go.Figure()

                # 따뜻한 톤의 색상 2가지 (종목 1, 종목 2)
                line_colors = ["#E8A33D", "#7A9E7E"]

                for idx, (t, (history, company_name)) in enumerate(results.items()):
                    fig.add_trace(
                        go.Scatter(
                            x=history.index,
                            y=history["Close"],
                            mode="lines",
                            name=f"{company_name} ({t})",
                            line=dict(color=line_colors[idx % len(line_colors)], width=2),
                        )
                    )

                fig.update_layout(
                    title=f"{selected_period_label} 주가 흐름",
                    xaxis_title="날짜",
                    yaxis_title="가격",
                    template="plotly_white",
                    plot_bgcolor="#FFF8E7",   # 크림톤 배경
                    paper_bgcolor="#FFF8E7",
                    font=dict(color="#7A5C2E"),
                    hovermode="x unified",
                    legend=dict(orientation="h", yanchor="bottom", y=1.02),
                )

                st.plotly_chart(fig, use_container_width=True)

                # ---------------------------
                # 종목별 지표 카드 (현재가, 등락률, 최고/최저/평균가)
                # ---------------------------
                for t, (history, company_name) in results.items():
                    show_metric_cards(t, company_name, history)
                    st.divider()

                # 원본 데이터를 보고 싶은 사람을 위한 표 (선택적으로 펼쳐보기)
                with st.expander("📋 원본 데이터 보기"):
                    for t, (history, company_name) in results.items():
                        st.write(f"**{company_name} ({t})**")
                        st.dataframe(history[["Open", "High", "Low", "Close", "Volume"]])

        except Exception as e:
            # yfinance 호출 중 오류가 나면 사용자에게 친절하게 안내
            st.error(
                "주가 정보를 불러오는 중 문제가 발생했어요. "
                "잠시 후 다시 시도해주세요."
            )
            st.caption(f"오류 상세: {e}")

elif search_clicked and not (ticker_1 or ticker_2):
    # 종목을 하나도 입력하지 않고 버튼을 눌렀을 때
    st.warning("종목 코드를 최소 1개 이상 입력해주세요.")

# ---------------------------
# 하단 안내 문구
# ---------------------------
st.divider()
st.caption(
    "💡 데이터 출처: Yahoo Finance (yfinance 라이브러리). "
    "투자 판단의 참고용으로만 활용해주세요."
)
