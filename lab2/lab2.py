#!/usr/bin/python
import pgdb
import matplotlib
import matplotlib.pyplot as plt
from sys import argv


class Program:
    def __init__(self): #PG-connection setup
        # local server:
        params = {'host':'', 'user':'postgres', 'database':'', 'password':''}
        # kth server:
        # params = {'host':'nestor2.csc.kth.se', 'user': 'yourkthusername', 'database':'', 'password':'yournestorpassword'}
        self.conn = pgdb.Connection(**params)
        self.conn.autocommit=False
        # specify the command line menu here
        self.actions = [self.population_query, self.population_scatterplot, self.exit]
        # menu text for each of the actions above
        self.menu = ["Population Query", "Population Scatterplot", "Exit"]
        self.cur = self.conn.cursor()


    def print_menu(self):
        """Prints a menu of all functions this program offers.  Returns the numerical correspondant of the choice made."""
        for i, x in enumerate(self.menu):
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
        minpop = input("min_population: ")
        maxpop = input("max_population: ")
        query ="SELECT * FROM city WHERE population >=%s AND population <= %s" % (minpop, maxpop)
        print("Will execute: ", query)

        self.cur.execute(query)
        self.print_answer()


    def l_of_tuples_to_l_of_lists(self, list_of_tuples):
        xs = []
        ys = []
        for t in list_of_tuples:
            print("Considering tuple", t)
            if (t[0] != None and t[1] != None):
                xs.append(t[0])
                ys.append(t[1])
            else:
                print("Dropped tuple ", t)

        return [xs, ys]


    def population_scatterplot(self):
        user_input = input("Per year or per decade? Y for year, D for decade. Your answer ([Y/D]): ")
        print(user_input)
        if user_input.lower() == "y":
            select_1 = "year"
            group_by = "year"
        else:
            select_1 = "(FLOOR(year/10)*10) AS decade"
            group_by = "decade"


        query = "SELECT {}, SUM(population) AS total_pop FROM citypops GROUP BY {} ORDER BY {};".format(select_1, group_by, group_by)
        print("Will execute: ", query)

        self.cur.execute(query)
        # self.print_answer()

        results = self.cur.fetchall()
        results = [tuple(int(item) for item in t) for t in results]

        xs_and_ys = self.l_of_tuples_to_l_of_lists(results)

        plt.scatter(xs_and_ys[0], xs_and_ys[1])
        plt.show()  # display figure if you run this code locally
        plt.savefig("figure.png") # save figure as image in local directory


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
