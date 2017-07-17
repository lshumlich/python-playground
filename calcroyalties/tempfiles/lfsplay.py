import jinja2
import os
from itertools import groupby, tee
from datetime import datetime
import config
import pdfkit

def xtest_render():
    # not quite working. It gives an error for __call__
    # assume it is an unittest function
    context = {  # your variables to pass to template
        'test_var': 'test_value',
        'url_for': 'lfsloc',
        '__call__': 'lfscall'
    }
    # path = 'path/to/template/dir'
    path = os.path.join(os.path.dirname(os.getcwd()), "src/app/templates/worksheet")
    print(os.listdir(path))
    print('-- the path: ', path)
    filename  ='calc_worksheet.html'

    rendered = jinja2.Environment(
        loader=jinja2.FileSystemLoader(path)
    ).get_template(filename).render(context)

    # `rendered` is now a string with rendered template
    # do some asserts on `rendered` string
    # i.e.
    assert 'test_value' in rendered


def xtest_render2():
    from jinja2 import Environment, PackageLoader
    env_name = 'C:/code/python-playground/calcroyalties/src/app'
    print(os.listdir(env_name))
    env = Environment(
        loader=PackageLoader(env_name, 'templates'))

# loader = PackageLoader(os.path.join(os.path.dirname(os.getcwd()), "src/app"), 'templates'))

def xtest_dir():
    print(os.path.join(os.path.dirname(os.getcwd()), "src/app"))
    print(os.listdir(os.path.join(os.path.dirname(os.getcwd()), "src/app")))
    print(__name__)
    print(__file__)
    print(os.listdir('.'))
    print(os.getcwd())
    print(os.path.dirname(os.getcwd()))
    print(os.pardir)
    print(__file__)
    print(os.path.join(os.path.dirname(__file__), "files/"))

def play1():
    my_list = ['Hello', 'World', 'I', 'Love', 'You']
    print(' and '.join(my_list))

def get_calc_list():
    print("Hello Calc List")
    import config
    db = config.get_database()
    statement = """SELECT * from calc, wellroyaltymaster,monthly
        where calc.wellid = wellroyaltymaster.id and
        calc.wellid = monthly.wellid  and
        calc.ProdMonth = monthly.ProdMonth and
        calc.Product = monthly.Product
        order by calc.prodMonth, calc.LeaseID, calc.wellid
    """
    result = db.select_sql(statement)
    print('we have found: ', len(result))
    return result

def group_by_test(results):

    for key, group in groupby(results, lambda x: str(x.ProdMonth) + str(x.LeaseID) + str(x.WellID) + x.Product):
        group1, group2 = tee(group)
        x = next(group1)
        print('key: ', x.ProdMonth, x.LeaseID, x.WellID, x.Product)

        for r in group2:
            print(' data: ', r.ProdMonth, r.WellID, x.Product)

        print('sum', x.ProdMonth, x.WellID)

    # for r in results:
    #     print(r.ProdMonth, r.Product, r.WellID,r.LeaseID,r.ProdVol)

def func(x):
    # print('-- func', x)
    return str(x.ProdMonth)

def start_logging():
    import logging
    import sys
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


def add_some_logs():
    import logging
    import datetime
    t1 = datetime.datetime.now()
    logging.info('Batch started: ' + str(t1))

def play_with_logs():
    import logging
    logger = logging.getLogger()
    print(logger.handlers)
    if len(logger.handlers) > 0:
        print(logger.handlers[0])
        logger.handlers[0].close()


def print_timestamp():
    dt = datetime.now()
    print(dt.strftime('%Y-%m-%d %H:%M:%S'))

def find_calcs():
    db = config.get_database()

    vars = {}
    # vars['ID'] = 1
    vars['ExtractDate'] = 20150929

    calcs = db.select('Calc', **vars)
    print(len(calcs))


def parm_pass(p1, p2='default1'):
    print('p1=', p1, ' p2=',p2)


def pdf_play():
    path_wkthmltopdf = r'C:\Program Files (x86)\wkhtmltopdf\bin\wkhtmltopdf.exe'
    config = pdfkit.configuration(wkhtmltopdf=path_wkthmltopdf)
    pdfkit.from_string('Hello World', 'out.pdf', configuration=config)
    # pdfkit.from_url('http://localhost:5000/worksheet?LeaseID=9001', 'out.pdf', configuration=config)
    # pdfkit.from_url('http://localhost:5000/worksheet?ID=3', 'out1.pdf', configuration=config)
    # pdfkit.from_url('http://localhost:5000/worksheet?ID=82', 'out2.pdf', configuration=config)
    # pdfkit.from_url('google.ca','out3.pdf', configuration=config)
    # pdfkit.from_url(['http://localhost:5000/worksheet?ID=82', 'google.ca', 'http://localhost:5000/worksheet?ID=3', 'google.ca'], 'out.pdf', configuration=config)

    # pdf = open('outfile.pdf', mode='wb')
    # pdf = pdfkit.from_url('http://google.com', False, configuration=config)
    # newfile=open('outpdf.pdf', 'ab')
    # newfile.write(pdfkit.from_url('http://google.com', False, configuration=config))
    # newfile.write(pdfkit.from_url('http://google.com', False, configuration=config))
    # newfile.write(pdfkit.from_url('http://google.com', False, configuration=config))
    # newfile.close()
    # print(pdf)
    # pdfkit.from_url(['http://localhost:5000/play/math', 'http://localhost:5000/play/math', 'http://localhost:5000/play/math'], 'out.pdf', configuration=config)


pdf_play()

# parm_pass('x', 'xx')
# parm_pass('x')


# find_calcs()
# print_timestamp()
# play_with_logs()
# start_logging()
# add_some_logs()
# add_some_logs()
# add_some_logs()
# add_some_logs()
# add_some_logs()
# play_with_logs()
# add_some_logs()
# add_some_logs()
# play_with_logs()
# add_some_logs()
# add_some_logs()
# add_some_logs()
#

        # test_render()
# test_render2()
# test_dir()
# play1()

# results = get_calc_list()
# group_by_test(results)