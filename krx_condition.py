def get_condition1(df):
    # 유동자산
    return (df.account_id == 'ifrs-full_CurrentAssets')  # 유동자산


def get_condition2(df):
    # 부채총계
    return (df.account_id == 'ifrs-full_Liabilities')  # 부채총계


def get_condition3(df):
    # 자본 총계
    return (df.account_id == 'ifrs-full_Equity')  # 자본총계


def get_condition4(df):
    # 매출액 부분
    return (df.account_id == 'ifrs-full_Revenue')


def get_condition5(df):
    # 매출총이익
    return (df.account_id == 'ifrs-full_GrossProfit')


def get_condition6(df):
    # 영업이익, 영업손실
    return ((df.account_id == 'dart_OperatingIncomeLoss') | (df.account_id == 'ifrs-full_ProfitLossFromContinuingOperations'))


def get_condition7(df):
    # 당기 순 이익
    return ((df.account_id == 'ifrs-full_ProfitLoss') | (df.account_id == 'dart_ProfitLossForStatementOfCashFlows'))


# 현금흐름표 부분
def get_condition8(df):
    ## 영업활동 현금흐름
    return ((df.account_id == 'ifrs-full_CashFlowsFromUsedInOperatingActivities') | (df.account_id == 'dart_ProfitLossForStatementOfCashFlows'))


def get_condition9(df):
    # 투자활동으로인한 현금흐름
    return (df.account_id == 'ifrs-full_CashFlowsFromUsedInInvestingActivities')


def get_condition10(df):
    # 자산총계
    return ((df.account_id == 'ifrs-full_Assets') | (df.account_id == 'ifrs-full_EquityAndLiabilities'))


def get_condition11(df):
    # 매출 원가
    return ((df.sj_nm == '손익계산서') | (df.sj_nm == '포괄손익계산서')) & (df.account_nm == '매출원가')


def get_condition12(df):
    # 순이익
    return (df.account_id == 'ifrs-full_ProfitLossBeforeTax')


def get_condition13(df):
    # 지출비용
    return ((df.sj_nm == '손익계산서') | (df.sj_nm == '포괄손익계산서')) & (df.account_nm == '법인세비용(혜택)')


def get_condition14(df):
    return ((df.sj_nm == '손익계산서') | (df.sj_nm == '포괄손익계산서')) & (df.account_nm == 'II.재료비')  # 008770 매출총이익 계산하기 위한 것
    
def get_condition15(df):
    return (df.account_id == 'ifrs-full_PurchaseOfPropertyPlantAndEquipmentClassifiedAsInvestingActivities')