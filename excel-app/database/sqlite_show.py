#!/bin/env python3

import config

class Shower(object):
    
    def __init__(self):
        print('Shower.__init__', self)

    def connect(self,dbName):
        self.dbi = config.get_database_instance(dbName)
        
    def check_linktab(self):
        None
        
    
    def insert_link(self, tabName, attName, linkName, baseTab, showAttrs):
        """ 
        create table linktab (TabName text, AttrName text, LinkName text, BaseTab boolean, ShowAttrs text);
        insert into linktab values ("BATable", "ID", "BA", 1, "ID,BAName");
        """
        stmt = 'insert into linktab values("' + tabName + '", "' + attName + '", "' + linkName + ', "' + baseTab + ',"' + showAttrs+ '")'
        self.dbi.execute(stmt)
        self.dbi.commit()
        
    def close(self):
        self.dbi.close()

    def show_table(self,tableName,attr=None,key=None):
        stmt = 'select * from ' + tableName
        if key:
            ctype = self.columnType(tableName, attr)
            where = ''
            if ctype == 'int':
                where = attr + "=" + key
            elif ctype =='text':
                where = attr + "='" + key + "'"
            else:
                print('***** Type not delt with:', type,tableName,attr)
            
            stmt = stmt + " where " + where
        elif attr:
            stmt = stmt + " order by " + attr
        print('SQL:', stmt)
        values = self.dbi.execute(stmt)
        table_rows = []
        for row in values:
            table_rows.append(row)
        return table_rows
        
    def show_tables(self):
        stmt = 'select tbl_name from sqlite_master'
        values = self.dbi.execute(stmt)
        tables = []
        for row in values:
            tables.append(row[0])
        return(tables)

    def show_columns(self,tableName):
        stmt = 'pragma table_info(' + tableName + ')'
        values = self.dbi.execute(stmt)
        columns = []
        for row in values:
            columns.append(row[1])
        return(columns)
    
    def column_type(self,table,column):
        stmt = 'pragma table_info(' + table + ')'
        values = self.dbi.execute(stmt)
        for row in values:
            if row[1] == column:
                return row[2]
        return(None)


def show_table(dbName, tableName):
    shower = Shower()
    shower.connect(dbName)
    header = shower.showColumns(tableName)
    print(header)
    rows = shower.showTable(tableName,'Prov','SK')
    for row in rows:
        print(row)


if __name__ == '__main__':
    dbName = 'testload.db'
    tableName = 'Well'
    show_table(dbName, tableName)