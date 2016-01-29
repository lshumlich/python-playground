
#
# Attributes and data structures in python
#

k = 'Konstantin'
a = 'Adrienne'

n1 = k
n2 = a

n1 = 'Larry'
n2 = 'Larry'
#??? What will this print ?
print('--- Attributes')
print('k:',k,'a:',a,'n1',n1,'n2',n2)
print('-')

i1 = 1
i2 = 2

i3 = i1
i3 = 3
print('i1:', i1, 'i2:', i2, 'i3:', i3)

#
# objects
#

class Person(object):
    def __init__(self,n,a):
        self.name = n
        self.age = a
    def __str__(self):
        return self.name + ' is ' + str(self.age) + ' years old.'
    
kobj = Person(k,30)

print('--- objects')
print('kobj.name:', kobj.name)
print('kobj:', kobj)

xxx = kobj
xxx.name = 'Larry'
      
#??? What will this print ? Why?
print('kobj.name:', kobj.name)
print('kobj:',kobj)
print('xxx:',xxx)      

#
# Lists, Queues, Stacks 
#

people = []

people.append(Person(k,30))
people.append(Person(a,30))
people.append(Person(n1,30))

print('--- Lists')

print('people[0]',people[0])

for p in people:
    print('List -->',p)

#
# dictionary
#
print('--- dictionary ')

peps = dict()

peps['KL'] = Person(k,30)
peps['AS'] = Person(a,30)
peps['LS'] = Person(n1,30)

print("peps['KL']",peps['KL'])
for p in people:
    print('dict:',p)

#
# Ranges
#
print('--- ranges')
for x in range(3):
    print('range:',x)

print('--- ranges')
for x in range(7,10):
    print('--- range',x)

