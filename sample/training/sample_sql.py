#
# The bascis of SQL from a python perspective
#

import sqlite3
#
# Little utility to show the contents of a table in a database.
#
def show_person_table():
	
	print('')
	print('- - - - - - - -')
	print('')
	c.execute("""select * from person;""")

	for row in c:
		print (row, ' - name = ', row[1], ' -  salary  = ',row[2])

# --------- Part 1 -------------------

conn = sqlite3.connect('sample.db')

c = conn.cursor()

c.execute("""drop table if exists person""")

c.execute(""" create table person (
				id integer primary key autoincrement,
				name txt,
					salary  real)""")
				
c.execute("""insert into person (name, salary ) values ("Jill Long Name", 25.10);""")
c.execute("""insert into person (name, salary ) values("Bob Shorter Name", 15.25);""")
c.execute("""insert into person (name, salary ) values("Sally shortest name", 30.5);""")
c.execute("""insert into person (name, salary ) values("Joe just kidding name", 11.7);""")

show_person_table()

c.execute("""update person set salary=26.2 where id = 1;""")
show_person_table()

c.execute("""delete from person where id = 2;""")
show_person_table()


# ------- Part 2 ---------

c.execute("""drop table if exists monthlyhours""")

c.execute(""" create table monthlyhours (
				id integer primary key autoincrement,
				person_id integer,
				month integer,
				hours real);""")

c.execute("""insert into monthlyhours (person_id, month, hours ) values (1,201603,120);""")
c.execute("""insert into monthlyhours (person_id, month, hours ) values (2,201603,110);""")
c.execute("""insert into monthlyhours (person_id, month, hours ) values (3,201603,100);""")

c.execute("""select person.id, person.name, person.salary, mh.month, mh.hours from person, 
				monthlyhours mh where person.id = mh.person_id;""")

print('')
print('- - - - - - - -')
print('')

for row in c:
	print (row)

c.execute("""drop view if exists vsalary""")

c.execute("""create view vsalary as select person.id, person.name, person.salary, 
			mh.month, mh.hours from person, monthlyhours mh 
			where person.id = mh.person_id;""")

c.execute("""select * from vsalary;""")

print('')
print('- - - - - - - -')
print('')

for row in c:
	print (row)


conn.commit()

c.close()

print("That's if folks!")