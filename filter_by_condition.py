import pandas as pd
import requests
import datetime
import yaml

with open('/Users/jaelee/invest_code/quantpython/config.yaml', encoding='UTF-8') as f:
    _cfg = yaml.load(f, Loader=yaml.FullLoader)
DISCORD_WEBHOOK_URL = _cfg['DISCORD_WEBHOOK_URL']

def send_message(msg):
    """디스코드 메세지 전송"""
    now = datetime.datetime.now()
    message = {"content": f"[{now.strftime('%Y-%m-%d %H:%M:%S')}] {str(msg)}"}
    requests.post(DISCORD_WEBHOOK_URL, data=message)

def drop_column(df: pd.DataFrame):
    # 스팩 주식 드랍
    df.drop(
        df[df["종목명"].str.contains("스팩")].index,
        inplace=True
    )
    df.drop(
        df[df["종목명"].str.contains("제[\d]호")].index,
        inplace=True
    )
    # 우선주 드랍
    df.drop(
        df[df["종목명"].str.endswith(("우", "우B", "우C","우(전환)","투자증권","캐피탈","IB","인베스트먼트"))].index,
        inplace=True
    )

    # 지주사 드랍
    df.drop(
        df[df["종목명"].str.endswith(("홀딩스", "지주", "지주회사"))].index,
        inplace=True
    )

    # 직전 거래일의 거래량이 0인 경우는 어떠한 이유에서 거래정지가 되어있을 확률이 높음
    df = df[df["거래량"] > 0]


    return df

def filtering_data_that_market_cap_under_thirty_percent(data: pd.DataFrame):
    """
    코스피, 코스닥의 종목에서 시가총액 30%이하의 종목으로 필터함.
    이 때, 기업소재지가 외국, 스팩주, 우선주, 최신거래일에 거래량이 0인 종목은 제거함.
    :param data:
    :return: DataFrame
    """
    data = drop_column(data)
    data = data.sort_values(by=["시가총액"], ascending=True)
    return data.iloc[:int(len(data) * 0.3)]

def filtering_low_per(sheet_name, df_copied: pd.DataFrame):
    """
    전체 데이터중 조회시점을 기준으로 PER가 10 이하인 기업.
    :param data:
    :return:
    """

    df = drop_column(df_copied)

    return (sheet_name,
            df[df["PER"] <= 10.0])

def filtering_low_pbr_and_per(sheet_name, pbr: float, per: float, df: pd.DataFrame, all_data=False):
    """
    0.2 <= PBR < pbr
    0 < PER <= per
    :param pbr:
    :param per:
    :param df:
    :param all_data:
    :return:
    """

    df1 = df[df['PBR'].between(0.2, pbr)].copy()
    df2 = df1[df1['PER'].between(0.5, per)].copy()

    if all_data:
        df2["PBR rank"] = df2["PBR"].rank(ascending=True)
        df2["PER rank"] = df2["PER"].rank(ascending=True)
    else:
        df2["PBR rank"] = df2.groupby("연도")["PBR"].rank(ascending=True)
        df2["PER rank"] = df2.groupby("연도")["PER"].rank(ascending=True)

    df2["Total_rank"] = df2["PBR rank"] + df2["PER rank"]

    return (sheet_name,
            df2.sort_values(by=['Total_rank', '종목코드'], ascending=[True, True]).reset_index(
                drop=True)
            )

def filtering_high_div(sheet_name, df: pd.DataFrame):
    """
    전체 데이터중 조회 시점으로 배당률이 0제외한 기업들에서 내림차순으로 정렬한 데이터.
    :param df:
    :return:
    """

    df.drop(
        df[df["DIV"] <= 0].index,
        inplace=True
    )

    return (sheet_name,
            df.sort_values(by=["DIV"], ascending=False).reset_index(drop=True)
            )

def filtering_high_propensity_to_dividend(sheet_name, df: pd.DataFrame):
    """
    배당성향 30~75% 사이
    배당수익률이 가장 높은 주식
    :param data:
    :return:
    """

    dps_condition_1 = (df["DPS"] > 0)
    net_income_condition_1 = (df["당기순이익"] > 0)
    df1 = df[dps_condition_1 & net_income_condition_1].copy()

    df1["배당성향"] = ((df1["DPS"] * df1["상장주식수"]) / df1["당기순이익"]) * 100

    df2 = df1[(df1["배당성향"].between(30.0, 75.0))].copy()


    return (sheet_name,
            df2.sort_values(by=["DIV"], ascending=False).reset_index(drop=True)
            )

"""def filtering_low_pbr_and_high_gpa(sheet_name, pbr: float, df: pd.DataFrame):
    Profitable value. 저 PBR 고 GPA
    최근분기 데이터로 계산
    :param pbr:
    :param df:
    :return:
    gpa_condition = (df['GP/A'] > 0)

    df.drop(
        df[df["PER"] <= 0].index,
        inplace=True
    )

    df = df[df['PBR'].between(0.2, pbr)].copy()
    df2 = df[gpa_condition]
    df2["PBR rank"] = df2.groupby("연도")["PBR"].rank(ascending=True)
    df2["GP/A rank"] = df2.groupby("연도")["GP/A"].rank(ascending=False)

    df2["PBR and GP/A score"] = df2["PBR rank"] + df2["GP/A rank"]

    return (sheet_name,
            df2.sort_values(by=['연도', 'PBR and GP/A score'], ascending=[False, True]).reset_index(
                drop=True)
            )"""


def filtering_high_ncav_cap_and_gpa(sheet_name, df: pd.DataFrame):
    """
    청산가치/시가총액이 높고 GPA수치가 높은 기업들
    :param df:
    :return:
    """

    df.drop(
        df[df["당기순이익"] <= 0].index,
        inplace=True
    )

    df.drop(
        df[df["부채비율"] >= 200.0].index,
        inplace=True
    )

    df.drop(
        df[df["NCAV/MC"] <= 0.0].index,
        inplace=True
    )

    df["NCAV/MC rank"] = df.groupby("연도")["NCAV/MC"].rank(ascending=False)
    df["GP/A rank"] = df.groupby("연도")["GP/A"].rank(ascending=False)

    df["Total score"] = df["NCAV/MC rank"] + df["GP/A rank"]

    return (sheet_name,
            df.sort_values(by=['연도', "Total score"], ascending=[False, True]).reset_index(
                drop=True)
            )

def filtering_value_factor(sheet_name, df: pd.DataFrame):
    """
    PBR, PER, PCR, PSR의 합게 점수값이 낮은 순.
    분기 PER값을 사용
    :param df:
    :return:
    """

    df.drop(
        df[df["PER_quarterly"] <= 0].index,
        inplace=True
    )

    df["PBR rank"] = df["PBR"].rank(ascending=True)
    df["PER rank"] = df["PER_quarterly"].rank(ascending=True)
    df["PCR rank"] = df["PCR"].rank(ascending=True)
    df["PSR rank"] = df["PSR"].rank(ascending=True)

    df["4 Total Value score"] = df["PBR rank"] + df["PER rank"] + df["PCR rank"] + df["PSR rank"]

    return (sheet_name,
            df.sort_values(by=['연도', '4 Total Value score'], ascending=[False, True]).reset_index(
                drop=True)
            )

def filtering_value_factor_upgrade(sheet_name, df: pd.DataFrame):
    """
    강환국 소형주 오리지널 슈퍼 가치 전략 업그레이드버전
    - 분기 PER
    - PBR
    - 분기 PFCR
    - 분기 PSR을 계산
    :param df:
    :return:
    """
    df = df.sort_values(by=['연도'], ascending=[False])
    df = df.drop_duplicates(['종목코드'], keep = 'first')

    df.drop(
        df[df["PER_quarterly"] <= 0].index,
        inplace=True
    )
    df.drop(
        df[df["PFCR"] <= 0].index,
        inplace=True
    )

    df["PBR rank"] = df["PBR"].rank(ascending=True)
    df["PER rank"] = df["PER_quarterly"].rank(ascending=True)
    df["PFCR rank"] = df["PFCR"].rank(ascending=True)
    df["PSR rank"] = df["PSR"].rank(ascending=True)

    df["4 Total Value score"] = df["PBR rank"] + df["PER rank"] + df["PFCR rank"] + df["PSR rank"]
    
    df = df.sort_values(by=['4 Total Value score'], ascending=[True])

    print(df.iloc[:20,1])

    send_message(df.iloc[:25,1])


    return (sheet_name,
            df.sort_values(by=['4 Total Value score'], ascending=[True]).reset_index(
                drop=True)
            )

def filtering_new_F_score_and_low_pbr(sheet_name, df: pd.DataFrame):
    """
    PBR하위 25퍼센트 중
    최근 1년간 신규주식 발행을 안했으며 -> 네이버증권 등에서 확인해야함.
    최신분기 순이익이 0이상인 기업
    최신분기 영업활동현금흐름이 0 이상인 기업
    :param df:
    :return:
    """

    df.drop(
        df[df["PBR"] <= df["PBR"].quantile(q=0.25)].index,
        inplace=True
    )

    df["당기순이익 점수"] = 0
    df["영업활동현금흐름 점수"] = 0

    df.loc[df["당기순이익"] > 0, "당기순이익 점수"] = 1
    df.loc[df["영업활동현금흐름"] > 0, "영업활동현금흐름 점수"] = 1

    df["F Score"] = df["당기순이익 점수"] + df["영업활동현금흐름 점수"]

    return (sheet_name,
            df.sort_values(by=['연도', 'F Score', 'PBR'], ascending=[False, False, True]).reset_index(
                drop=True)
            )

def filtering_low_pfcr(sheet_name, df: pd.DataFrame):
    """
    PFCR. 시가총액 / 잉여현금흐름.
    작으면 주식이 저평가 되었다고 말할 수 있음.
    :param df:
    :return:
    """

    df = df[df["PFCR"] > 0]

    return (sheet_name,
            df.sort_values(by=['연도', 'PFCR'], ascending=[False, True]).reset_index(
                drop=True)
            )


def filtering_profit_momentum(sheet_name, df: pd.DataFrame):
    """
    전분기 대비 당기영업이익 성장률 랭크
    전분기 대비 당기순이익 성장률 랭크
    :param df:
    :return:
    """

    df["당기영업이익 성장률 순위"] = df.groupby("연도")["영업이익 증가율"].rank(method='min', ascending=False)
    df["당기순이익 성장률 순위"] = df.groupby("연도")["당기순이익 증가율"].rank(method='min', ascending=False)

    df["모멘텀 순위"] = df["당기영업이익 성장률 순위"] + df["당기순이익 성장률 순위"]

    return (sheet_name,
            df.sort_values(by=['연도', '모멘텀 순위'], ascending=[False, True]).reset_index(
                drop=True)
            )

def filtering_value_and_profit_momentum(sheet_name, df: pd.DataFrame):
    """
    전분기 대비 당기영업이익 성장률 랭크
    전분기 대비 당기순이익 성장률 랭크
    분기 PER,
    PBR,
    PFCR,
    PSR
    :param df:
    :return:
    """

    df.drop(
        df[df["PER_quarterly"] <= 0].index,
        inplace=True
    )

    df["당기영업이익 성장률 순위"] = df.groupby("연도")["영업이익 증가율"].rank(method='min', ascending=False)
    df["당기순이익 성장률 순위"] = df.groupby("연도")["당기순이익 증가율"].rank(method='min', ascending=False)

    df["PBR rank"] = df["PBR"].rank(ascending=True)
    df["PER rank"] = df["PER_quarterly"].rank(ascending=True)
    df["PFCR rank"] = df["PFCR"].rank(ascending=True)
    df["PSR rank"] = df["PSR"].rank(ascending=True)

    df["모멘텀 순위"] = (df["당기영업이익 성장률 순위"] + df["당기순이익 성장률 순위"] + df["PBR rank"] + df["PER rank"] + df["PFCR rank"] + df[
        "PSR rank"]) / 6

    return (sheet_name,
            df.sort_values(by=['연도', '모멘텀 순위'], ascending=[False, True]).reset_index(
                drop=True)
            )