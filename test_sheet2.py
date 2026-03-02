import app
from openpyxl import Workbook

cls={'name':'Test','rows':3,'assignments':[{'name':'Quiz','weight':20,'count':4},{'name':'HW','weight':20,'count':2}]}
wb=Workbook()
try:
    wb.remove(wb.active)
except Exception:
    pass
app.create_class_sheet(wb,cls)
wb.save('test2.xlsx')
print('saved test2.xlsx')
