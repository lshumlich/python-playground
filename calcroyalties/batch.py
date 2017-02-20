#!/bin/env python3

# import subprocess
# import os
# import sys
# import logging
# import datetime
# from src.calc.calcroyalties import ProcessRoyalties
# from src.tool.sqlite_load_excel import load_sheet
# from src.database.database_create import DatabaseCreate
# from tests.database.sqlite_utilities_test import DatabaseUtilities
# import config


def process_royalties():
    from src.calc.calcroyalties import ProcessRoyalties
    pr = ProcessRoyalties()
    pr.process_all()


def browse_file():
    import os
    import subprocess
    import config
    print('os name is:', os.name)
    if os.name != "posix":
        subprocess.call(['notepad.exe', config.get_temp_dir() + 'log.txt'])

def drop_create_tables():
    from tests.database.sqlite_utilities_test import DatabaseUtilities
    dbu = DatabaseUtilities()
    dbu.delete_all_tables()
    create_tables()


def create_tables():
    from src.database.database_create import DatabaseCreate
    db_create = DatabaseCreate()
    db_create.create_all()


def drop_table(table_name):
    from tests.database.sqlite_utilities_test import DatabaseUtilities
    dbu = DatabaseUtilities()
    dbu.delete_table(table_name)

def load_sample_data():
    from tests.database.sqlite_utilities_test import DatabaseUtilities
    dbu = DatabaseUtilities()
    drop_create_tables()
    dbu.create_some_test_well_royalty_masters()
    dbu.create_some_test_leases()


def start_logging():
    import logging, sys
    import config

    logging.basicConfig(filename=config.get_temp_dir() + 'calc.log', filemode='w', level=logging.INFO)
    root = logging.getLogger()
    root.setLevel(logging.INFO)

    log = logging.getLogger('werkzeug')
    log.setLevel(logging.CRITICAL)

    ch = logging.StreamHandler(sys.stdout)
    ch.setLevel(logging.DEBUG)
    # formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    formatter = logging.Formatter('%(levelname)s - %(message)s')
    ch.setFormatter(formatter)
    root.addHandler(ch)


def run_code_coverage():
    import coverage
    import pytest

    cov = coverage.Coverage()
    cov.start()

    pytest.main("tests")

    cov.stop()
    cov.save()
    cov.html_report()


if __name__ == "__main__":
    run_code_coverage()
    # start_logging()
    # t1 = datetime.datetime.now()
    # logging.info('Batch started: ' + str(t1))

    # drop_create_tables()
    # drop_table("DataDictionary")
    # load_sheet(config.get_temp_dir() + "DataDictionary.xlsx")
    # load_sheet("K:\\lms\\Analysis and Design\\Sample Data Saved\\DataDictionary.xlsx")
    # load_sheet(config.get_temp_dir() + "sample_data.xlsx")
    # load_sheet("K:\\lms\\Analysis and Design\\Sample Data Saved\\sample_data 2016-10-17.xlsx")
    # process_royalties()

    # t2 = datetime.datetime.now()
    # logging.info('Ended: ' + str(t2))

    # t3 = t2 - t1
    # logging.info('Took: ' + str(t3))

# /Users/lshumlich/Documents/hanggliding/2016 Flights/2016-07-29_21-57.igc