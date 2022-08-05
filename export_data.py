import array
import pandas as pd


class ExportToData:
    def __init__(self):
        self.pandas = pd

    def export_to_excel(self, file_path, file):
        print("Exporting result to excel file.....")
        writer = self.pandas.ExcelWriter(file_path, engine='openpyxl')
        file.to_excel(writer, sheet_name="test")

        writer.save()
    
    def export_to_excel_with_many_sheets(self, file_path, files: array):
    	# 진행상황 확인용 프린트문
        print("Exporting result to excel file.....")
        
        # 파일 생성용 객체 생성
        writer = self.pandas.ExcelWriter(file_path, engine='openpyxl')

        for sheet_name, file in files:
            file.to_excel(writer, sheet_name=sheet_name)

        writer.save()