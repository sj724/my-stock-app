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
    "종목 코드를 입력하면 최근 1년간의 주가 흐름을 그래프로 보여드려요. "
    "예: 삼성전자는 `005930.KS`, 애플은 `AAPL` 이렇게 입력해보세요 :)"
)

# ---------------------------
# 종목 코드 입력창
# ---------------------------
ticker_input = st.text_input(
    "종목 코드를 입력하세요",
    value="AAPL",
    placeholder="예: 005930.KS (삼성전자), AAPL (애플)",
)

# 입력값 앞뒤 공백 제거 및 대문자로 변환 (티커는 보통 대문자를 사용)
ticker = ticker_input.strip().upper()

# ---------------------------
# 조회 버튼
# ---------------------------
search_clicked = st.button("조회하기", type="primary")

# 버튼을 누르거나, 이미 입력값이 있으면 실행
if search_clicked and ticker:
    # 로딩 중임을 알려주는 스피너
    with st.spinner(f"{ticker} 주가 정보를 불러오는 중이에요..."):
        try:
            # 최근 1년 기간 계산
            end_date = datetime.today()
            start_date = end_date - timedelta(days=365)

            # yfinance로 티커 객체 생성 후 과거 주가 데이터 가져오기
            stock = yf.Ticker(ticker)
            history = stock.history(start=start_date, end=end_date)

            # 데이터가 비어있으면 잘못된 종목 코드일 가능성이 큼
            if history.empty:
                st.error(
                    "주가 정보를 찾을 수 없어요. 종목 코드를 다시 확인해주세요. "
                    "(예: 005930.KS, AAPL)"
                )
            else:
                # ---------------------------
                # 현재가 및 1년 등락률 계산
                # ---------------------------
                start_price = history["Close"].iloc[0]   # 1년 전 종가
                current_price = history["Close"].iloc[-1]  # 가장 최근 종가
                change_percent = (current_price - start_price) / start_price * 100

                # 종목 이름 가져오기 (없으면 티커 코드로 대체)
                try:
                    company_name = stock.info.get("longName", ticker)
                except Exception:
                    company_name = ticker

                st.subheader(f"{company_name} ({ticker})")

                # ---------------------------
                # 지표 카드로 현재가, 등락률 보여주기
                # ---------------------------
                col1, col2 = st.columns(2)

                with col1:
                    st.metric(
                        label="현재가",
                        value=f"{current_price:,.2f}",
                    )

                with col2:
                    st.metric(
                        label="최근 1년 등락률",
                        value=f"{change_percent:,.2f}%",
                        delta=f"{change_percent:,.2f}%",
                    )

                # ---------------------------
                # Plotly 꺾은선 그래프 그리기
                # ---------------------------
                fig = go.Figure()

                fig.add_trace(
                    go.Scatter(
                        x=history.index,
                        y=history["Close"],
                        mode="lines",
                        name="종가",
                        line=dict(color="#E8A33D", width=2),  # 따뜻한 톤의 주황빛 선
                    )
                )

                fig.update_layout(
                    title="최근 1년 주가 흐름",
                    xaxis_title="날짜",
                    yaxis_title="가격",
                    template="plotly_white",
                    plot_bgcolor="#FFF8E7",   # 크림톤 배경
                    paper_bgcolor="#FFF8E7",
                    font=dict(color="#7A5C2E"),
                    hovermode="x unified",
                )

                st.plotly_chart(fig, use_container_width=True)

                # 원본 데이터를 보고 싶은 사람을 위한 표 (선택적으로 펼쳐보기)
                with st.expander("📋 원본 데이터 보기"):
                    st.dataframe(history[["Open", "High", "Low", "Close", "Volume"]])

        except Exception as e:
            # yfinance 호출 중 오류가 나면 사용자에게 친절하게 안내
            st.error(
                "주가 정보를 불러오는 중 문제가 발생했어요. "
                "잠시 후 다시 시도해주세요."
            )
            st.caption(f"오류 상세: {e}")

elif search_clicked and not ticker:
    # 종목 코드를 입력하지 않고 버튼을 눌렀을 때
    st.warning("종목 코드를 먼저 입력해주세요.")

# ---------------------------
# 하단 안내 문구
# ---------------------------
st.divider()
st.caption(
    "💡 데이터 출처: Yahoo Finance (yfinance 라이브러리). "
    "투자 판단의 참고용으로만 활용해주세요."
)
