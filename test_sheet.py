import app
from openpyxl import Workbook

# create dummy data
cls = {'name':'Test','rows':5,'assignments':[{'name':'A1','weight':20},{'name':'A2','weight':80}]}
wb=Workbook()
wb.remove(wb.active)
app.create_class_sheet(wb, cls)
wb.save('test.xlsx')
print('saved test.xlsx')
