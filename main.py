import datetime
import time

import filter_by_condition
from extract import Extract
from export_data import ExportToData

y = datetime.date.today().year
start = time.time()
extractor = Extract()
exporter = ExportToData()
kospi_kosdaq_data = extractor.get_data()

print("--------------")
extracted_data = extractor.extract_finance_data(
    [y,y-1,y-2],
    filter_by_condition.filtering_data_that_market_cap_under_thirty_percent(
        kospi_kosdaq_data
    ))
#extracted_data = filter_by_condition.filtering_data_that_market_cap_under_thirty_percent(kospi_kosdaq_data)

exporter.export_to_excel_with_many_sheets(
    "/Users/jaelee/invest_code/quantpython/investhere.xlsx",
    [
        filter_by_condition.filtering_low_per("ALL_DATA_저PER", kospi_kosdaq_data.copy()),
        filter_by_condition.filtering_low_per("소형주_저PER", extracted_data.copy()),
        filter_by_condition.filtering_low_pbr_and_per("ALL_DATA_저PBR_저PER", 1.0, 10, kospi_kosdaq_data.copy(), True),
        filter_by_condition.filtering_low_pbr_and_per("소형주_저PBR_저PER", 1.0, 10, extracted_data.copy()),
        filter_by_condition.filtering_high_div("고배당률_리스트", kospi_kosdaq_data.copy()),
        filter_by_condition.filtering_high_propensity_to_dividend("소형주 고배당성향", extracted_data.copy()),
        filter_by_condition.filtering_low_pfcr("소형주_저PFCR_시총잉여현금흐름", extracted_data.copy()),
        filter_by_condition.filtering_low_pbr_and_high_gpa("소형주_저PBR_고GPA", 0.8, extracted_data.copy()),
        filter_by_condition.filtering_high_ncav_cap_and_gpa("소형주_고NCAV_GPA_저부채비율", extracted_data.copy()),
        filter_by_condition.filtering_profit_momentum("소형주_모멘텀_전분기대비_영업이익순이익_전략", extracted_data.copy()),
        filter_by_condition.filtering_value_and_profit_momentum("소형주_밸류모멘텀_전략", extracted_data.copy()),
        filter_by_condition.filtering_value_factor("소형주_HIGH_SCORE_Four_value", extracted_data.copy()),
        filter_by_condition.filtering_value_factor_upgrade("소형주_강환국_슈퍼가치전략_업글", extracted_data.copy()),
        filter_by_condition.filtering_new_F_score_and_low_pbr("소형주_NEW F Score and Low PBR", extracted_data.copy()),

        ("Extracted_RAW_Data", extracted_data),
        ("RAW_Data", kospi_kosdaq_data)
    ]
)

end = time.time()
sec = (end - start)

result_list = str(datetime.timedelta(seconds=sec)).split(".")
print(f"Total extracting time : {result_list[0]} ---------------------")