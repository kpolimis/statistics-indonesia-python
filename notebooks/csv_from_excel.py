import os
import xlrd
import csv


def csv_from_excel(filename):
    """
    coverts .xls or .xlsx file into .csv file with same filename prefix
    """
    workbook = xlrd.open_workbook(filename)
    workbook_sheet_names = ''.join(workbook.sheet_names()).encode('utf-8')
    sheet = workbook.sheet_by_name(workbook_sheet_names)
    csv_filename = os.path.basename(filename).split(".")[0]+".csv"
    new_csv_file = open(csv_filename, 'wb')
    wr = csv.writer(new_csv_file, quoting=csv.QUOTE_ALL)

    for rownum in xrange(sheet.nrows):
        wr.writerow(sheet.row_values(rownum))

    new_csv_file.close()
    print("created %s" % csv_filename)
