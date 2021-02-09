import psycopg2
from github import Github
from pathlib import Path
from datetime import datetime
from time import sleep
import pandas as pd
import pytz

IST = pytz.timezone('Asia/Kolkata')

# df1 = pd.read_csv("status.csv", delimiter=',')
ID_Stat = []#df1['ID'].values.tolist()
Calendar = []#df1['Date'].values.tolist()
# Name_Stat = df1['Name'].values.tolist()





def showStatDB():
    global ID_Stat, Calendar

    mydb2 = psycopg2.connect(
        host="HOST",
        database="DATABASE",
        user="USER",
        password="PASSWORD"
    )

    mycursor2 = mydb2.cursor()

    SQL = "SELECT * FROM status ORDER BY ID ASC"
    mycursor2.execute(SQL)
    out = mycursor2.fetchall()
    for row in out:
        ID_Stat.append(row[0])
        Calendar.append(row[1])

    ID_Stat = (-1, 0) + tuple(ID_Stat)
    print(ID_Stat)


def saveStatDB(ID, DATE_STAT, QNAME):

    mydb2 = psycopg2.connect(
        host="HOST",
        database="DATABASE",
        user="USER",
        password="PASSWORD"
    )

    mycursor2 = mydb2.cursor()

    sql2 = "INSERT INTO status(ID, DATE_STAT, NAME) VALUES  (" + str(ID) + ", '" + str(DATE_STAT) + "', " + str(QNAME) + ");"
    print(sql2)
    mycursor2.execute(sql2)
    mydb2.commit()


def mergeCode(Qno, Qname, Qdesc, Session, Code):
    # Qname = Qname.replace(" ", "")
    # Session = Session.replace(" ", "")
    Qdesc = Qdesc.replace("<br>", "\n#")

    Qname = Qname.replace('\\"', '"')
    Qname = Qname.replace("“", "'")

    Qdesc = Qdesc.replace('\\"', '"')
    Qdesc = Qdesc.replace("“", "'")

    Code = Code.replace('\\"', '"')
    Code = Code.replace("“", "'")

    Qno = Qno[1:-1]
    Qname = Qname[1:-1]
    Qdesc = Qdesc[1:-1]
    Session = Session[1:-1]
    Code = Code[1:-1]




    parseAns = "#" + Qno + '\n\n' \
               "#" + Qname + "(" + Session + ")" + '\n\n' + "#" + Qdesc + "\n\n\n" + Code
    return parseAns


def ConnectGB(Code, Name):
    g = Github(ACCESS_TOKEN)

    repo = g.get_repo("Abhijith14/PythonElab")

    contents = repo.get_contents("")

    i = 0
    Name = Name[1:-1]
    Name = Name.replace(" ", "")
    destination = Name + ".py"
    Names = []

    while contents:
        file_content = contents.pop(0)
        Names.append(file_content.name)

    restart = True

    while restart:
        for name_val in range(len(Names)):
            restart = False
            if Names[name_val] == destination:
                i = i + 1
                destination = Name + "(" + str(i) + ").py"
                restart = True
                break

    repo.create_file(destination, "Commit", Code, branch="main")


def ConnectDB():

    showStatDB()

    mydb = psycopg2.connect(
        host="HOST",
        database="DATABASE",
        user="USER",
        password="PASSWORD"
    )

    mycursor = mydb.cursor()

    print("CONNECTED TO DB")
    print("----------------------------------------------------------")

    t = tuple(ID_Stat)

    SQL = "SELECT * FROM elabdata WHERE id NOT IN {} ORDER BY ID ASC".format(t)

    mycursor.execute(SQL)

    ans = mycursor.fetchall()
    count = ID_Stat[-1]

    for row in ans:

        today = datetime.now(IST)  # date.today()
        today = today.strftime('%Y-%m-%d')

        print()
        print("******************************")
        print(str(today))
        print(str(Calendar))
        print("******************************")
        print()

        while str(today) in str(Calendar):
            today = datetime.now(IST)  # date.today()
            today = today.strftime('%Y-%m-%d')
            print()
            print("Waiting for Next Day ...")
            print("Date Stored : ")
            print(Calendar)
            print(str(count) + " Questions out of " + str(len(ans)) + " (" + str(len(ans) - count) + " remaining).")
            print()
            sleep(5)

        Calendar.append(str(today))

        count = count + 1
        ID = row[0]
        Session = row[1]
        QNo = row[2]
        Qname = row[3]
        QDesc = row[4]
        Code = row[5]

        parsed_Code = mergeCode(QNo, Qname, QDesc, Session, Code)

        print("Typing Question - " + str(Qname.replace(" ", "")) + " --------- #" + str(ID) + " -------> " + str(
            count) + "/" + str(len(ans)) + " (" + str(len(ans) - count) + " remaining).")

        ConnectGB(parsed_Code, Qname)
        #Create_local_File(parsed_Code, Qname)

        # new_row = [{'ID': ID, 'Date': str(today), 'Name': Qname.replace(" ", "")}]
        # new_data = df1.append(new_row)
        # new_data.to_csv("status.csv", index=False)

        saveStatDB(ID, str(today), Qname.replace(" ", ""))


        print("Finished!!!")
        sleep(5)


def Create_local_File(Data, Name):
    i = 0
    Name = Name.replace(" ", "")
    Name = Name[1:-1]
    destination = "Python/" + Name + ".py"

    while Path(destination).is_file():
        i = i + 1
        destination = "Python/" + Name + "(" + str(i) + ").py"

    f = open(destination, "w+")
    f.write(Data)
    f.close()


ConnectDB()