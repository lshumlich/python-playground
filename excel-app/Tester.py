from openpyxl import load_workbook
from openpyxl import Workbook


print ('Hello World')
wb = load_workbook('database.xlsx')
tabName = 'ProducingEntity'
ws = wb[tabName]
print ("rows is:", len(ws.rows))
print ("cols is:", len(ws.rows[0]))

#             headerRow = None
#             for row in ws.rows:
#                 if headerRow == None:
#                     headerRow = row
#                 else:
#                     recordNo = recordNo +1
#                     ds = DataStructure()
#                     stack.append(ds)
#                     i = 0
#                     for cell in headerRow:
#                         setattr(ds, cell.value, row[i].value)
#                         i = i + 1
#                     setattr(ds, 'RecordNumber', recordNo)
