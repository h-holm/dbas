#!/usr/bin/python
import pgdb
import matplotlib
import matplotlib.pyplot as plt
from sys import argv


class Program:
    def __init__(self): #PG-connection setup
        # local server:
        params = {'host':'', 'user':'postgres', 'database':'', 'password':''}
        self.conn = pgdb.Connection(**params)
        self.conn.autocommit=False
        # specify the command line menu here
        self.actions = [self.population_query, self.scatterplot_population, self.plot_datapoints_per_year, self.plot_mean_and_stdev_per_decade, self.exit]
        # menu text for each of the actions above
        self.menu = ["Population Query", "Population Scatterplot", "Plot # of datapoints per year", "Plot mean and std_dev per decade", "Exit"]
        self.cur = self.conn.cursor()


    def print_menu(self, input_menu):
        """Prints a menu of all functions this program offers.  Returns the numerical correspondant of the choice made."""
        for i, x in enumerate(input_menu):
            print("%i. %s"%(i+1, x))
        return self.get_int(input_menu)


    def get_int(self, input_menu):
        """Retrieves an integer from the user.
        If the user fails to submit an integer, it will reprompt until an integer is submitted."""
        while True:
            try:
                choice = int(input("Choose: "))
                if 1 <= choice <= len(input_menu):
                    return choice
                print("Invalid choice.")
            except (NameError, ValueError, TypeError, SyntaxError):
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


    def scatterplot_population(self):
        """
        1. Create a scatterplot of x=year against y=total population of all
           cities in PopData.
        """

        scatter_menu = ["Per year", "Per decade"]
        choice = None
        while choice not in [1, 2]:
            choice = self.print_menu(scatter_menu)

        if choice == 1:
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


    def plot_datapoints_per_year(self):
        """
        2.      Also plot the number of cities for which we have data per year.
                What can you say about this?
        Answer: As is common in data science situations, we have found
                ourselves in a situation where our data is not perfect.
        """

        query = "SELECT year, COUNT(DISTINCT(city, country)) FROM citypops GROUP BY year;"
        print("Will execute: ", query)

        self.cur.execute(query)
        results = self.cur.fetchall()
        results = [tuple(int(item) for item in t) for t in results]

        xs_and_ys = self.l_of_tuples_to_l_of_lists(results)

        plt.scatter(xs_and_ys[0], xs_and_ys[1])
        plt.show()  # display figure if you run this code locally
        plt.savefig("figure.png") # save figure as image in local directory


    def plot_mean_and_stdev_per_decade(self):
        """
        3. Try to also create an SQL query and accompanying plot that aggregates
           information by decade and displays the mean population and standard
           deviations per decade using an matplotlib errorbar plot
        """

        query = "SELECT (FLOOR(year/10)*10) AS decade, AVG(population) AS mean_pop, STDDEV_SAMP(population) AS stddev_pop FROM citypops GROUP BY decade ORDER BY decade;"
        print("Will execute: ", query)

        self.cur.execute(query)
        results = self.cur.fetchall()

        results = [tuple(int(item) if not item is None else item for item in t) for t in results]

        xs = []
        ys = []
        yerrs = []
        for t in results:
            print("Considering tuple", t)
            if (t[0] != None and t[1] != None and t[2] != None):
                xs.append(t[0])
                ys.append(t[1])
                yerrs.append(t[2])
            else:
                print("Dropped tuple ", t)

        plt.errorbar(x = xs, y = ys, yerr = yerrs)
        plt.show()
        plt.savefig("Errorplot.png")


    def fit_line(self):
        """
        b)  Let us attempt to predict a city’s population by fitting a line
            y = ax + b to the y=population, x=year data per city.
            PostgreSQL has aggregation functions to find a best-fitting line
            approximation to a set of x coordinates X and y coordinates
            Y: regr_slope(Y, X) (gives a), regr_intercept(Y, X) (gives b) and
            the degree of determination r2 measures how closely the data follows
            a linear trend r2 = regr_r2(Y, X) (1 = data follows linear trend, 0
            does not follow linear trend at all).
        """
        pass


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
                self.actions[self.print_menu(self.menu)-1]()
            except IndexError:
                print("Bad choice")
                continue


if __name__ == "__main__":
    db = Program()
    db.run()
