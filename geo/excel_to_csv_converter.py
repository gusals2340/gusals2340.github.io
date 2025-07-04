import pandas as pd
import os

def convert_excel_to_csv(excel_file_path, output_dir):
    """
    엑셀 파일의 모든 시트를 개별 CSV 파일로 변환합니다.

    Args:
        excel_file_path (str): 변환할 엑셀 파일의 전체 경로.
        output_dir (str): CSV 파일이 저장될 디렉토리 경로.
    """
    if not os.path.exists(excel_file_path):
        print(f"오류: 엑셀 파일이 존재하지 않습니다 - {excel_file_path}")
        return

    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
        print(f"출력 디렉토리를 생성했습니다: {output_dir}")

    try:
        xls = pd.ExcelFile(excel_file_path)
        sheet_names = xls.sheet_names
        print(f"'{excel_file_path}' 파일에서 다음 시트를 찾았습니다: {sheet_names}")

        for sheet_name in sheet_names:
            df = pd.read_excel(excel_file_path, sheet_name=sheet_name)
            csv_file_name = f"{os.path.splitext(os.path.basename(excel_file_path))[0]}_{sheet_name}.csv"
            csv_file_path = os.path.join(output_dir, csv_file_name)
            df.to_csv(csv_file_path, index=False, encoding='utf-8-sig')
            print(f"'{sheet_name}' 시트를 '{csv_file_path}'로 변환했습니다.")
        print("모든 시트 변환 완료.")

    except Exception as e:
        print(f"엑셀 파일을 CSV로 변환하는 중 오류가 발생했습니다: {e}")

if __name__ == "__main__":
    # 사용 예시:
    excel_path = "D:/project/study/config/kt_config_backup_250106_hkmc_(대경선추가).xlsx"
    output_directory = "D:/project/study/config/csv_output"
    convert_excel_to_csv(excel_path, output_directory)

    print("사용법: 이 스크립트를 직접 실행하거나, 다른 Python 스크립트에서 'convert_excel_to_csv' 함수를 호출하여 사용하세요.")
    print("예시:")
    print("  excel_path = 'D:/project/study/config/kt_config_backup_250106_hkmc_(대경선추가).xlsx'")
    print("  output_directory = 'D:/project/study/config/csv_output'")
    print("  convert_excel_to_csv(excel_path, output_directory)")
