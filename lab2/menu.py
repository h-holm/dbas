#!/usr/bin/python
import pgdb
from sys import argv

class Program:
    def __init__(self): #PG-connection setup
        # local server:
        # params = {'host':'', 'user':'postgres', 'database':'', 'password':''}
        # kth server:
        params = {'host':'nestor2.csc.kth.se', 'user': 'yourkthusername', 'database':'', 'password':'yournestorpassword'}
        self.conn = pgdb.Connection(**params)
        self.conn.autocommit=False
        # specify the command line menu here
        self.actions = [self.population_query, self.exit]
        # menu text for each of the actions above
        self.menu = ["Population Query", "Exit"]
        self.cur = self.conn.cursor()
    def print_menu(self):
        """Prints a menu of all functions this program offers.  Returns the numerical correspondant of the choice made."""
        for i,x in enumerate(self.menu):
            print("%i. %s"%(i+1,x))
        return self.get_int()
    def get_int(self):
        """Retrieves an integer from the user.
        If the user fails to submit an integer, it will reprompt until an integer is submitted."""
        while True:
            try:
                choice = int(input("Choose: "))
                if 1 <= choice <= len(self.menu):
                    return choice
                print("Invalid choice.")
            except (NameError,ValueError, TypeError,SyntaxError):
                print("That was not a number, genious.... :(")
 
    def population_query(self):
        minpop = raw_input("min_population: ")
        maxpop = raw_input("max_population: ")
        query ="SELECT * FROM city WHERE population >=%s AND population <= %s" % (minpop, maxpop)
        print "Will execute: ", query

        self.cur.execute(query)
        self.print_answer()

    def exit(self):    
        self.cur.close()
        self.conn.close()
        exit()

    def print_answer(self):
        print("-----------------------------------")
        print("\n".join([", ".join([str(a) for a in x]) for x in self.cur.fetchall()]))
        print("-----------------------------------")

    def run(self):
        while True:
            try:
                self.actions[self.print_menu()-1]()
            except IndexError:
                print("Bad choice")
                continue

if __name__ == "__main__":
    db = Program()
    db.run()
