#!/usr/bin/python
import pgdb
import matplotlib
import matplotlib.pyplot as plt
import numpy as np
from sys import argv


class Program:
    def __init__(self): #PG-connection setup
        # local server:
        params = {'host':'', 'user':'postgres', 'database':'', 'password':''}
        self.conn = pgdb.Connection(**params)
        self.conn.autocommit=False
        # specify the command line menu here
        self.actions = [self.population_query, self.scatterplot_population, self.plot_datapoints_per_year, self.plot_mean_and_stdev_per_decade, self.scatterplot_user_input, self.exit]
        # menu text for each of the actions above
        self.menu = ["Population Query", "Population Scatterplot", "Plot # of datapoints per year", "Plot mean and std_dev per decade", "Scatterplot data about your city", "Exit"]
        self.cur = self.conn.cursor()


    def print_menu(self, input_menu):
        """Prints a menu of all functions this program offers.  Returns the numerical correspondant of the choice made."""
        print()
        for i, x in enumerate(input_menu):
            print("%i. %s"%(i+1, x))
        print()
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


    def scatterplot_user_input(self):
        """
        c)  Now create a text menu in python that asks a user a city and associated
            country and creates a figure that displays all the population, year
            datapoints for the city as a scatterplot with x-axis = year, y-axis =
            population as well as predicted behavior of population as a line y =
            ax + b on a graph.
        """

        cities_query = "SELECT DISTINCT city, country FROM citypops;"
        self.cur.execute(cities_query)
        cities = self.cur.fetchall()
        cities = [t[0] for t in cities]
        cities_lower = [c.lower() for c in cities]
        user_city = input("\nPlease choose a city: ").lower().strip()
        while user_city not in cities_lower:
            user_city = input("\nPlease choose a valid city: ").lower().strip()

        # seen = list()
        # dups = list()
        # for c in cities_lower:
        #     if c in seen:
        #         dups.append(c)
        #     seen.append(c)
        # print(dups)

        country_query = "SELECT DISTINCT country FROM citypops WHERE city = '{}';".format(user_city.title())
        self.cur.execute(country_query)
        countries = self.cur.fetchall()
        countries = [t[0] for t in countries]

        if cities_lower.count(user_city) > 1:
            print("\nThe city '{}' exists in the following countries: ".format(user_city.title()))
            for i, c in enumerate(countries):
                print("\t{}: {}".format(i+1, c))
            user_country = input("\nPlease specify which country you mean: ").lower()
            countries_lower = [c.lower() for c in countries]
            while user_country not in countries_lower:
                user_country = input("\nPlease choose a valid country: ").lower()
        else:
            user_country = countries[0]

        user_country = user_country.upper()
        user_city = user_city.title()

        scatter_query = "SELECT year, population FROM citypops WHERE city = '{}' AND country = '{}'".format(user_city, user_country)
        self.cur.execute(scatter_query)
        years_pops = self.cur.fetchall()
        years_pops = [(int(y_p[0]), int(y_p[1])) for y_p in years_pops]

        years = list()
        pops = list()
        for y_p in years_pops:
            # print("Considering tuple", y_p)
            if (y_p[0] != None and y_p[1] != None):
                years.append(y_p[0])
                pops.append(y_p[1])
            else:
                print("Dropped tuple ", y_p)


        line_query = "SELECT a, b, yearfrom, r2, nsamples FROM LinearPrediction WHERE cityname = '{}' AND country = '{}';".format(user_city, user_country)
        self.cur.execute(line_query)
        a_b_yf_r2_ns = self.cur.fetchall()
        a_b_yf_r2_ns = [(float(t[0]), float(t[1]), int(t[2]), float(t[3]), int(t[4])) for t in a_b_yf_r2_ns]
        a_b_yf_r2_ns = a_b_yf_r2_ns[0]

        a = a_b_yf_r2_ns[0]
        b = a_b_yf_r2_ns[1]
        yf = a_b_yf_r2_ns[2]
        r2 = a_b_yf_r2_ns[3]
        ns = a_b_yf_r2_ns[4]

        future = np.array(range(2020, 2031))
        pop_predictions = a*future + b
        print("\n# of samples: ", ns)
        print("r2 value: ", r2)
        for i, p in enumerate(pop_predictions):
            print("Population prediction for {}: ".format(future[i]), int(p))

        plt.scatter(years, pops, label='Population per year')
        plt.plot(years, a * np.asarray(years) + b, '-', label='Prediction: y = ax + m')
        plt.show()

        # Examples of strongly inclining trend:
        # 1. Karaj, IR
        # 2. Tijuana, Mexico
        # 3. Esfahan, IR
        # Examples of strongly declining trend:
        # 1. Nezahualcóyotl, MEX
        # 2. Detroit, USA
        # 3. Lodz, PL

        # Example of SQL queries to use if we want to find strongly in-/declining
        # cities:
        # SELECT cityname, country, r2 FROM LinearPrediction WHERE nsamples > 4 AND a > 30000 AND r2 > 0.9;
        # SELECT cityname, country, r2 FROM LinearPrediction WHERE nsamples > 4 AND a < -5000 AND r2 > 0.9;


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
