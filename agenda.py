from __future__ import print_function
from ortools.sat.python import cp_model
import csv
import networkx as nx
from networkx.algorithms import clique

def intersects(i, j):
    return i[1] > j[0] and j[1] > i[0]

def minutesSinceMidnight(s):
    n = len(s)-3
    d1 = s[:n]
    d2 = s[n:]
    a = 0
    if(d2[1] == 'P'):
        a = a + 12*60

    s2 = d1.split(":")
    return a + (int(s2[0])%12)*60 + int(s2[1])

availability_per_person = []
# The answers are in 8 columns each day except the last day
answer_columns = []
for i in range(7):
    for j in range(4):
        answer_columns.append(13+i*10+2*j)


for j in range(2):
    answer_columns.append(83+2*j)

stot = 0
with open('formulario1.csv') as csv_file:
    csv_reader = csv.reader(csv_file, delimiter=',')
    line_count = 0
    for row in csv_reader:
        av_p = []
        if line_count > 0:
            for k in answer_columns:
                if(row[k] != "" and row[k+1] != ""):
                    aux_hour = [minutesSinceMidnight(row[k])+(k//10-1)*24*60, minutesSinceMidnight(row[k+1])+(k//10-1)*24*60]
                    if(len(av_p) > 0 and aux_hour[0] == av_p[len(av_p)-1][1]+1):
                        av_p[len(av_p)-1][1] = aux_hour[1]
                    else:
                        av_p.append(aux_hour)
                    dk = av_p[len(av_p)-1]
                    if(dk[1] < dk[0]):
                        stot = stot+1

            availability_per_person.append(av_p)
        line_count += 1

a = []
days = []
run_names = []
with open('Reparto.csv') as csv_file:
    csv_reader = csv.reader(csv_file, delimiter=',')
    line_count = 0
    for row in csv_reader:
        if line_count >=  1 and line_count%2 == 1:
            days.append(row[0])
            a.append(row[1])
            run_names.append(row[2])
        line_count += 1



a.append("2:00 AM")
run_names.append("")
days.append("Sunday")


minutes = [minutesSinceMidnight(a[0])]
for k in range(len(a)-1):
    if(days[k] == days[k+1]):
        m = minutes[len(minutes)-1]
        minutes.append(minutesSinceMidnight(a[k+1])-minutesSinceMidnight(a[k])+m)
    else:
        m = minutes[len(minutes)-1]
        minutes.append(minutesSinceMidnight(a[k+1])-minutesSinceMidnight(a[k])+m+60*24)



def availableAtThatHour(h1, h2, available_hours):
    found = False
    for i in available_hours:
        found = (h1 >= i[0]) and (h2 <= i[1])
        if(found):
            return True

    return False


roles_names = ["Comentarista 1", "Comentarista 2", "Monitor", "Supervisor", "Buscador de donaciones", "Moderador"]
roles = range(len(roles_names))

# Each row is the minutes of the schedule that there is a shift change in a specific role
hours_per_role = []
last = minutes[len(minutes)-1]
second_calend = []
for i in range(last//(1*60)+1):
    second_calend.append(i*1*60)

for r in range(2):
    hours_per_role.append(minutes)
for k in range(4):
    hours_per_role.append(second_calend)





# Each row is assigned to a person, and it tells the roles they can do
roles_per_person = []
people_names = []
with open('formulario1.csv') as csv_file:
    csv_reader = csv.reader(csv_file, delimiter=',')
    line_count = 0
    for row in csv_reader:
        r_person = []
        if line_count >=  1:
            people_names.append(row[1])
            ro = row[7]
            rs = ro.split(", ")
            if("Comentarista" in rs):
                r_person.append(0)
                r_person.append(1)
            #r_person.append(2)
            #r_person.append(3)
            for rp in range(len(roles_names)):
                if(roles_names[rp] in rs):
                    r_person.append(rp)
            roles_per_person.append(r_person)
        line_count += 1



# Each row is assigned to a person, and it tells the minutes they can do things
# availability_per_person = []
#for r in roles:
#    availability_per_person.append([[0,400]])

# The boolean variables will be of the form:
# (p, h1, h2, r)
# where p is the person id, [h1,h2] is the shift in minutes and r is the role
# If that variable is 1, they work at that shift in that role
# If it's 0, then they aren't working at that role in that shift

# Each element in this list is a particular shift already assigned, so it has to be 1 in the result
shifts_already_assigned = []
with open('AsignaRuns.csv') as csv_file:
    csv_reader = csv.reader(csv_file, delimiter=',')
    line_count = 0
    for row in csv_reader:
        r_person = []
        if line_count >=  1 and row[1] != "":
            p_id = people_names.index(row[1])
            run_id = run_names.index(row[0])
            r_id = 0
            shifts_already_assigned.append([p_id, minutes[run_id], minutes[run_id+1], r_id])
            if(not availableAtThatHour(minutes[run_id], minutes[run_id+1], availability_per_person[p_id])):
                jfkijf = 3
                #print("Me cago en ", row[1], " porque quiere la run ", row[0], " y no puede a las ", minutes[run_id], " - ", minutes[run_id+1])
            if(row[2] != ""):
                p_id = people_names.index(row[2])
                run_id = run_names.index(row[0])
                r_id = 1
                shifts_already_assigned.append([p_id, minutes[run_id], minutes[run_id+1], r_id])
                if(not availableAtThatHour(minutes[run_id], minutes[run_id+1], availability_per_person[p_id])):
                    jkshkdj = 3
                    #print("Me cago en ", row[1], " porque quiere la run ", row[0], " y no puede a las ", minutes[run_id], " - ", minutes[run_id+1])

        line_count += 1


# The ids of people working
people = range(len(roles_per_person))

def restInADay(work_hours, day):
    i = -1
    j = -1
    #print("REST IN A DAY")
    #print(work_hours)
    #print(day)
    for w in range(len(work_hours)):
        if(i == -1 and intersects(work_hours[w], day)):
            i = w
        if(j == -1 and i != -1 and (not intersects(work_hours[w], day))):
            j = w
        if(j != -1 and i != -1):
            break

    if(i == len(work_hours)-1):
        j = i+1
    #print("I Y J")
    #print(i, " ", j)
    #print("RESULT")

    if(i == -1 or j == -1):
        #print(day[1]-day[0])
        return day[1]-day[0]
    else:
        starting_rest = max(-day[0]+work_hours[i][0],0)
        ending_rest = max(day[1]-work_hours[j-1][1], 0)
        in_rest = max(starting_rest, ending_rest)
        for k in range(i,j-1):
            if(work_hours[k+1][0]-work_hours[k][1] > in_rest):
                in_rest = work_hours[k+1][0]-work_hours[k][1]
        #print(in_rest)
        return in_rest



def worstRestPerPerson(p,shifts):
    work_hours = []
    for r in roles_per_person[p]:
        for h in range(len(hours_per_role[r])-1):
            if(shifts[(p, hours_per_role[r][h], hours_per_role[r][h+1], r)] == 1):
                work_hours.append([hours_per_role[r][h], hours_per_role[r][h+1]])


    work_hours.sort()
    #print(work_hours)
    min_per_day = 60*24
    third_of_a_day = min_per_day//2
    days = [[0,min_per_day]]
    for i in range(7):
        for j in range(2):
            d = days[len(days)-1]
            days.append([d[0]+third_of_a_day, d[1]+third_of_a_day])

    m = -1
    for d in days:
        r = restInADay(work_hours, d)
        if(m == -1 or m > r):
            m = r

    return m

def worstRest(shifts):
    m = -1
    for p in people:
        w = worstRestPerPerson(p, shifts)
        if(m == -1 or w < m):
            m = w

    return m

# Creates the model.
model = cp_model.CpModel()

shifts = {}
for p in people:
    for r in roles:
        for h in range(len(hours_per_role[r])-1):
            shifts[(p, hours_per_role[r][h], hours_per_role[r][h+1], r)] = model.NewBoolVar('shift_p%ih%ij%ir%i' % (p, hours_per_role[r][h], hours_per_role[r][h+1], r))


# They have to be available when they work
for p in people:
    for r in roles_per_person[p]:
        for h in range(len(hours_per_role[r])-1):
            kjhf = 2
            model.AddImplication(shifts[(p,hours_per_role[r][h], hours_per_role[r][h+1], r)], availableAtThatHour(hours_per_role[r][h], hours_per_role[r][h+1], availability_per_person[p]))

# Each person has to be able to work of role r
# So the sum of shifts in roles not available has to be 0 for each person
for p in people:
    for r in roles:
        if(r not in roles_per_person[p]):
            fjf=2
            model.Add(sum(shifts[(p,hours_per_role[r][h], hours_per_role[r][h+1],r)] for h in range(len(hours_per_role[r])-1)) <= 0)


# The total number of people working at each role has to be exactly 1 in each shift
for r in roles:
    for h in range(len(hours_per_role[r])-1):
        ksfdjljf = 3
        model.Add(sum(shifts[(p,hours_per_role[r][h], hours_per_role[r][h+1],r)] for p in people) == 1)

def intervalToNode(i, j, nodesPerLine):
    return nodesPerLine[i]+j

def nodeToInterval(i, k):
    a = 0
    it = 0
    while(a + len(k[it])-1 <= i):
        a = a + len(k[it])-1
        it = it+1
    return [k[it][i-a], k[it][i-a+1], it]


k = hours_per_role

G = nx.Graph()

nodes = 0
nodesPerLine = []
for i in k:
    nodesPerLine.append(nodes)
    nodes = nodes + len(i)-1
G.add_nodes_from(range(nodes))

for i in range(len(k)):
    for i_2 in range(len(k[i])-1):
        for j in range(i+1,len(k)):
            for j_2 in range(len(k[j])-1):
                if(intersects([k[i][i_2], k[i][i_2+1]], [k[j][j_2], k[j][j_2+1]])):
                    n1 = intervalToNode(i, i_2, nodesPerLine)
                    n2 = intervalToNode(j, j_2, nodesPerLine)
                    G.add_edge(n1, n2)



a_clique = clique.find_cliques(G)

# The total number of shifts each person has at each moment has to be less than one

for a_it in a_clique:
    for p in people:
        ff = 2
        sum_in_cliques = sum(shifts[(p, nodeToInterval(n, k)[0], nodeToInterval(n,k)[1], nodeToInterval(n,k)[2])] for n in a_it)
        model.Add(sum_in_cliques <= 1)

for p in people:
    dfkjf = 2
    #model.Add(sum(shifts[(p,hours_per_role[r][h], hours_per_role[r][h+1],r)] for r in roles_per_person[p] for h in range(len(hours_per_role[r])-1)) >= 1)

# Assigned shifts

for p,h1,h2,r in shifts_already_assigned[:15]:
    kjfh=3
    model.Add(shifts[p,h1,h2,r] == 1)


#model.Maximize(worstRest(shifts))

#obj_var = model.NewIntVar(0, 24*60, 'worstRest')
#model.Add(obj_var <= worstRest(shifts))
#model.Maximize(obj_var)
solver = cp_model.CpSolver()
status = solver.Solve(model)
if(status == cp_model.FEASIBLE):
    print('Maximum of objective function: %i' % solver.ObjectiveValue())
    for r in roles:
        for h in range(len(hours_per_role[r])-1):
            for p in people:
                if(solver.BooleanValue(shifts[(p, hours_per_role[r][h], hours_per_role[r][h+1], r)])):
                    fk = 2
                    print("Person " + str(p) + " works at shift " + str(h) + " at role " + str(r) + "\n")
else:
    print("NO SE PUEDE HACERRRRR (eso cree)")

all_sols = []

def addZero(s):
    if(len(s) != 1):
        return s
    else:
        return "0"+s

def hoursFromMinutes(m1, m2):
    days_t = ["Domingo (primero)", "Lunes", "Martes", "Miércoles", "Jueves", "Viernes", "Sábado", "Domingo (segundo)"]
    k1 = m1 // (60*24)
    k2 = m2 // (60*24)
    md1 = m1 % (60*24)
    md2 = m2 % (60*24)
    end1 = ""
    end2 = ""
    if(md1 >= (60*12)):
        end1 = " PM"
    else:
        end1 = " AM"
    if(md2 >= (60*12)):
        end2 = " PM"
    else:
        end2 = " AM"
    st1 = str(md1 // 60) + ":" + addZero(str(md1%60)) + ":" + "00" + end1
    st2 = str(md2 // 60) + ":" + addZero(str(md2%60)) + ":" + "00" + end2
    return days_t[k1], days_t[k2], st1, st2

class NursesPartialSolutionPrinter(cp_model.CpSolverSolutionCallback):
    """Print intermediate solutions."""

    def __init__(self, shifts):
        cp_model.CpSolverSolutionCallback.__init__(self)
        self._shifts = shifts
        self._solution_count = 0

    def on_solution_callback(self):
        n_shf = {}
        for p in people:
            for r in roles:
                for h in range(len(hours_per_role[r])-1):
                    n_shf[(p, hours_per_role[r][h], hours_per_role[r][h+1], r)] = self.Value(self._shifts[(p, hours_per_role[r][h], hours_per_role[r][h+1], r)])

        wR = worstRest(n_shf)

        sol1 = [worstRestPerPerson(p, n_shf) for p in people]

        if(not (sol1 in all_sols)):
            print(sol1)
            print("Nueva solucion encontrada con ")
            print("VALOR ", wR)
            all_sols.append(sol1)
            f = open("HorarioNuevo.txt", 'w')
            comment1 = []
            comment2 = []
            hour_comm = []
            for r in roles:
                print("\nEn el rol ", roles_names[r], file=f)
                for h in range(len(hours_per_role[r])-1):
                    for p in people:
                        if(n_shf[(p, hours_per_role[r][h], hours_per_role[r][h+1], r)] == 1):
                            day_i, day_f, hour_i, hour_f = hoursFromMinutes(hours_per_role[r][h], hours_per_role[r][h+1])
                            if(r < 2):
                                if(r == 0):
                                    hour_comm.append(hour_i)
                                    comment1.append(people_names[p])
                                else:
                                    comment2.append(people_names[p])
                                print("Persona ", people_names[p], " como ", roles_names[r][:-2], " en el día ", day_i, " desde las ", hour_i, " hasta las ", hour_f, " del ", day_f, file=f)
                            else:
                                print(people_names[p], " como ", roles_names[r], " en el día ", day_i, " desde las ", hour_i, " hasta las ", hour_f, " del ", day_f, file=f)




            print(worstRest(n_shf))
            print(len(comment1), " ", len(comment2), " ", len(run_names), " ", len(hour_comm), " ")
            with open('Comentaristas.csv', mode='w', newline='') as comm_file:
                comm_writer = csv.writer(comm_file, delimiter=';', quotechar='"', quoting=csv.QUOTE_MINIMAL)
                for co_i in range(len(comment1)):
                    comm_writer.writerow([hour_comm[co_i], run_names[co_i], comment1[co_i], comment2[co_i]])
        self._solution_count += 1

    def solution_count(self):
        return self._solution_count

f = open("Monitores.txt", 'w')
for h in range(len(hours_per_role[2])-1):
    day_i, day_f, hour_i, hour_f = hoursFromMinutes(hours_per_role[2][h], hours_per_role[2][h+1])
    l_person = []
    for p in people:
        if(availableAtThatHour(hours_per_role[2][h], hours_per_role[2][h+1], availability_per_person[p]) and 2 in roles_per_person[p]):
            l_person.append(people_names[p])
    print("Día ", day_i, " ", hour_i, " - ", hour_f, ":", l_person, file=f)

f = open("Comentaristas.txt", 'w')
for h in range(len(hours_per_role[0])-1):
    day_i, day_f, hour_i, hour_f = hoursFromMinutes(hours_per_role[0][h], hours_per_role[0][h+1])
    l_person = []
    for p in people:
        if(availableAtThatHour(hours_per_role[0][h], hours_per_role[0][h+1], availability_per_person[p]) and 0 in roles_per_person[p]):
            l_person.append(people_names[p])
    print(hour_i, " - ", run_names[h], ":", l_person, file=f)

f = open("Supervisores.txt", 'w')
r = 3
for h in range(len(hours_per_role[r])-1):
    day_i, day_f, hour_i, hour_f = hoursFromMinutes(hours_per_role[r][h], hours_per_role[r][h+1])
    l_person = []
    for p in people:
        if(availableAtThatHour(hours_per_role[r][h], hours_per_role[r][h+1], availability_per_person[p]) and r in roles_per_person[p]):
            l_person.append(people_names[p])
    print("Día ", day_i, " ", hour_i, " - " ":", l_person, file=f)

f = open("Buscadores.txt", 'w')
r = 4
for h in range(len(hours_per_role[r])-1):
    day_i, day_f, hour_i, hour_f = hoursFromMinutes(hours_per_role[r][h], hours_per_role[r][h+1])
    l_person = []
    for p in people:
        if(availableAtThatHour(hours_per_role[r][h], hours_per_role[r][h+1], availability_per_person[p]) and r in roles_per_person[p]):
            l_person.append(people_names[p])
    print("Día ", day_i, " ", hour_i, " - " ":", l_person, file=f)

f = open("Moderadores.txt", 'w')
r = 5
for h in range(len(hours_per_role[r])-1):
    day_i, day_f, hour_i, hour_f = hoursFromMinutes(hours_per_role[r][h], hours_per_role[r][h+1])
    l_person = []
    for p in people:
        if(availableAtThatHour(hours_per_role[r][h], hours_per_role[r][h+1], availability_per_person[p]) and r in roles_per_person[p]):
            l_person.append(people_names[p])
    print("Día ", day_i, " ", hour_i, " - " ":", l_person, file=f)



solution_printer = NursesPartialSolutionPrinter(shifts)
status = solver.SearchForAllSolutions(model, solution_printer)





#todo wil seficompacto
