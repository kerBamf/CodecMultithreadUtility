from os import environ
from dotenv import load_dotenv
import openpyxl

# Loading envionment variable
load_dotenv()

# Creating openpyxl output logic


def excel_output(codecs, filename):
    # Creating new Excel file
    new_wb = openpyxl.Workbook()
    new_ws = new_wb.active
    new_ws.title = "Multithreader_Result"
    ft = openpyxl.styles.Font(bold=True)

    for row in codecs:
        new_ws.append(row)

    for row in new_ws["A1:C1"]:
        for cell in row:
            cell.font = ft

    new_wb.save(f"../output_files/{filename}")
    return "Excel File Saved"


if __name__ == "__main__":
    codecs = [["dummy_name", "999.999.999.999", "Test successful"]]
    excel_output(codecs, "test_output.xlsx")
