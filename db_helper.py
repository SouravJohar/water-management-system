import sqlite3
conn = sqlite3.connect('/Users/souravjohar/Documents/Code/WaterManage/water.db')
c = conn.cursor()
base = "dep"
count = 1

sex = ["M", "F"]
fnames = [u'Rick', u'Hugh', u'Ronan', u'Maci', u'Mylee', u'Vanessa', u'Leandro', u'Daisy', u'Alonso',
          u'Demarcus', u'Harley', u'Dominik', u'Louis', u'Aden', u'Alexandra', u'Elena', u'Jesse', u'Tyrion', u'Salazar', u'John', u'Ned', u'Paul', u'Sai', u'Shant', u'Poopy']
lnames = [u'Morty', u'Lawrence', u'Collins', u'Riggs', u'Mckee', u'Mullins', u'Hendricks',
          u'Arroyo', u'Bryan', u'Berger', u'Edwards', u'Vargas', u'Castillo', u'Schultz', u'Duarte', u'Khan', u'Rods', u'Lanni', u'Lolol', u'Wick', u'Stark', u'Pogba', u'KauKau', u'Bhurru', u'Butwhole'
          ]

designation = ['Area Manager', 'Sub-Ordinate', 'Accountant', 'Analyst', 'Assistant', 'Technician']
salary = range(30000, 150000, 10000)
depts = ["Supply", "Customer Service", "Qualtiy Control",
         "HR and Finance", "Research and Development", "Area Management", "Security"]
desc = ["Controls the supply of water in the city", "Handling the customer side queries and services", "Keeps track of the quality, purity of water",
        "Maintains the work environment in the company ; financial work", "Analysing the various data collected and striving for development", "Overall management of different areas in a city", "Protection and safety"]
bud = [1000000, 3000000, 1500000, 2000000, 3000000, 5000000, 300000]
# for i in range(0, 7):
#     print i
#     c.execute('insert into department values (?,?,?,?)',
#               (base + str(i + 1), depts[i],  bud[i], desc[i],))


f = open('/Users/souravjohar/Documents/Code/WaterManage/names.txt', 'r')
desig = ["Security Head"] + ["Assistant Security"] * 6
sals = [75000] + [30000] * 6
fnames = []
lnames = []
for i in range(120):
    a = f.readline().split()
    fnames.append(a[0])
    lnames.append(a[1])
fnames += ['Lionel']
lnames += ['Pessi']
import random
base = "em"
count = 114
for i in range(7):
    c.execute('insert into employee values (?,?,?,?,?,?,?,?)',
              (base + str(count), fnames[count], lnames[count], int(random.random() * 100000000000), "M", desig[i], "dep7", sals[i]))
    count += 1
conn.commit()
c.execute('select * from employee')
print c.fetchall()
