import pandas as pd
import os
import tkinter as tk
from tkinter import filedialog, messagebox

def convert_excel_to_csv(excel_file_path, output_dir, status_callback=None):
    """
    엑셀 파일의 모든 시트를 개별 CSV 파일로 변환합니다.
    UI에 상태를 업데이트하기 위한 status_callback을 추가했습니다.
    """
    if status_callback:
        status_callback("변환 시작: '{}'".format(excel_file_path))

    if not os.path.exists(excel_file_path):
        if status_callback:
            status_callback("오류: 엑셀 파일이 존재하지 않습니다 - {}".format(excel_file_path))
        return False

    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
        if status_callback:
            status_callback("출력 디렉토리를 생성했습니다: {}".format(output_dir))

    try:
        xls = pd.ExcelFile(excel_file_path)
        sheet_names = xls.sheet_names
        if status_callback:
            status_callback("'{}' 파일에서 다음 시트를 찾았습니다: {}".format(excel_file_path, sheet_names))

        for sheet_name in sheet_names:
            df = pd.read_excel(excel_file_path, sheet_name=sheet_name)
            # 엑셀 파일 이름에서 확장자를 제거하고 시트 이름을 추가하여 CSV 파일 이름 생성
            base_excel_name = os.path.splitext(os.path.basename(excel_file_path))[0]
            csv_file_name = "{}_{}.csv".format(base_excel_name, sheet_name)
            csv_file_path = os.path.join(output_dir, csv_file_name)
            df.to_csv(csv_file_path, index=False, encoding='utf-8-sig')
            if status_callback:
                status_callback("'{0}' 시트를 '{1}'로 변환했습니다.".format(sheet_name, csv_file_path))
        
        if status_callback:
            status_callback("모든 시트 변환 완료.")
        return True

    except Exception as e:
        if status_callback:
            status_callback("엑셀 파일을 CSV로 변환하는 중 오류가 발생했습니다: {}".format(e))
        return False

class ExcelToCsvConverterApp:
    def __init__(self, master):
        self.master = master
        master.title("엑셀 to CSV 변환기")

        self.excel_file_path = tk.StringVar()
        self.output_dir_path = tk.StringVar()

        # Excel File Selection
        tk.Label(master, text="엑셀 파일:").grid(row=0, column=0, sticky="w", padx=5, pady=5)
        tk.Entry(master, textvariable=self.excel_file_path, width=50, state="readonly").grid(row=0, column=1, padx=5, pady=5)
        tk.Button(master, text="찾아보기", command=self.browse_excel_file).grid(row=0, column=2, padx=5, pady=5)

        # Output Directory Selection
        tk.Label(master, text="출력 폴더:").grid(row=1, column=0, sticky="w", padx=5, pady=5)
        tk.Entry(master, textvariable=self.output_dir_path, width=50, state="readonly").grid(row=1, column=1, padx=5, pady=5)
        tk.Button(master, text="찾아보기", command=self.browse_output_dir).grid(row=1, column=2, padx=5, pady=5)

        # Convert Button
        tk.Button(master, text="CSV로 변환", command=self.convert_files).grid(row=2, column=0, columnspan=3, pady=10)

        # Status Log
        tk.Label(master, text="상태:").grid(row=3, column=0, sticky="nw", padx=5, pady=5)
        self.status_text = tk.Text(master, height=10, width=70, state="disabled")
        self.status_text.grid(row=3, column=1, columnspan=2, padx=5, pady=5)
        
        # Scrollbar for status log
        self.scrollbar = tk.Scrollbar(master, command=self.status_text.yview)
        self.scrollbar.grid(row=3, column=3, sticky="ns", pady=5)
        self.status_text.config(yscrollcommand=self.scrollbar.set)

    def browse_excel_file(self):
        file_path = filedialog.askopenfilename(
            filetypes=[("Excel files", "*.xlsx *.xls")],
            title="엑셀 파일 선택"
        )
        if file_path:
            self.excel_file_path.set(file_path)
            self.update_status("엑셀 파일 선택됨: {}".format(file_path))

    def browse_output_dir(self):
        dir_path = filedialog.askdirectory(title="CSV 파일 저장 폴더 선택")
        if dir_path:
            self.output_dir_path.set(dir_path)
            self.update_status("출력 폴더 선택됨: {}".format(dir_path))

    def update_status(self, message):
        self.status_text.config(state="normal")
        self.status_text.insert(tk.END, message + "\n")
        self.status_text.see(tk.END) # Scroll to the end
        self.status_text.config(state="disabled")
        self.master.update_idletasks() # Update GUI immediately

    def convert_files(self):
        excel_path = self.excel_file_path.get()
        output_dir = self.output_dir_path.get()

        if not excel_path:
            messagebox.showwarning("경고", "엑셀 파일을 선택해주세요.")
            return
        if not output_dir:
            messagebox.showwarning("경고", "출력 폴더를 선택해주세요.")
            return

        self.update_status("변환 시작...")
        success = convert_excel_to_csv(excel_path, output_dir, self.update_status)
        if success:
            messagebox.showinfo("완료", "엑셀 파일이 성공적으로 CSV로 변환되었습니다!")
        else:
            messagebox.showerror("오류", "파일 변환 중 오류가 발생했습니다. 상태 로그를 확인하세요.")

if __name__ == "__main__":
    # 필요한 라이브러리 설치 안내
    try:
        import pandas as pd
    except ImportError:
        messagebox.showerror("오류", "pandas 라이브러리가 설치되어 있지 않습니다.\n'pip install pandas openpyxl' 명령어로 설치해주세요.")
        exit()

    root = tk.Tk()
    app = ExcelToCsvConverterApp(root)
    root.mainloop()