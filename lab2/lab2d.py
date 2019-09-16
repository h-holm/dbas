#!/usr/bin/python
import pgdb
import matplotlib
import matplotlib.pyplot as plt
import numpy as np
from sys import argv
from lab2 import *

# Create a hypothesis about what factors may be correlated to population changes
# and generate a python program that allows the user to explore this hypothesis
# in terms of a few sample queries and visualizations with some user specified
# query parameters that confirm or disprove the hypothesis. Your program should
# correctly process errors (use try ... except ... pass error handling) that may
# be thrown if data is not found or the input is invalid. You can use all the
# information from Popdata and create new relations/views as desired.

# Some ideas: You could group the cities into quartiles according to a size,
# growth-trend etc and study them. You could ask if there are correlations
# between (longitude, latitude) position of a city and population growth.
# What are the mean and standard deviation properties of city size over
# different longitude-latitude rectangles? What can we say about the cities
# with rapidly declining populations? Is there a connection to the type economy
# in which they lie in terms of service vs agriculture percentages of gdp?

# Hypothesis: already large cities grow larger.
# Divide into quartiles (small, average, big, large)
# Hypothesis: high elevation declines.

class HypothesisProgram(Program):
    def __init__(self):
        # local server:
        params = {'host':'', 'user':'postgres', 'database':'', 'password':''}
        self.conn = pgdb.Connection(**params)
        self.conn.autocommit=False
        # specify the command line menu here
        self.actions = [self.population_query, self.scatterplot_population, self.test_hypothesis, self.exit]
        # menu text for each of the actions above
        self.menu = ["Population Query", "Population Scatterplot", "Test hypothesis", "Exit"]
        self.cur = self.conn.cursor()


    def silent_population_query(self, minpop, maxpop):
        query = "SELECT * FROM city WHERE population >= {} AND population <= {}".format(minpop, maxpop)
        self.cur.execute(query)
        self.print_answer()


    def separate_into_quartiles(self, input_list_of_tuples, idx):
        l = sorted(input_list_of_tuples, key=lambda x: x[idx])
        length = len(l)

        # q4 is the largest
        q1 = l[0:int(length/4)]
        q2 = l[int(length/4):int(length/2)]
        q3 = l[int(length/2):int((3*length)/4)]
        q4 = l[int((3*length)/4):-1]
        return q1, q2, q3, q4


    def test_hypothesis(self):
        # Countries growing quickly have high a-values in comparison to their
        # population.
        all_cities_query = "SELECT cityname, country, a, b, r2, nsamples, yearfrom, yearto, minpop, maxpop FROM LinearPrediction;"
        self.cur.execute(all_cities_query)
        results = self.cur.fetchall()
        results = [t for t in results if None not in t]
        results = [tuple((str(t[0]), str(t[1]), float(t[2]), float(t[3]), float(t[4]), int(t[5]), int(t[6]), int(t[7]), int(t[8]), int(t[9]))) for t in results]

        # This corresponds to the a value. High a equals high growth.
        idx_to_sort_on = 2
        q1, q2, q3, q4 = self.separate_into_quartiles(results, idx_to_sort_on)

        avg_a_q1 = sum([t[2] for t in q1]) / len(q1)
        avg_a_q2 = sum([t[2] for t in q2]) / len(q2)
        avg_a_q3 = sum([t[2] for t in q3]) / len(q3)
        avg_a_q4 = sum([t[2] for t in q4]) / len(q4)

        avg_pop_q1 = int(sum([int((t[8]+t[9])/2) for t in q1]) / len(q1))
        avg_pop_q2 = int(sum([int((t[8]+t[9])/2) for t in q2]) / len(q2))
        avg_pop_q3 = int(sum([int((t[8]+t[9])/2) for t in q3]) / len(q3))
        avg_pop_q4 = int(sum([int((t[8]+t[9])/2) for t in q4]) / len(q4))

        # print()
        # print(avg_pop_q1, avg_pop_q2, avg_pop_q3, avg_pop_q4)
        # print(avg_a_q1, avg_a_q2, avg_a_q3, avg_a_q4)

        avg_pops = [avg_pop_q1, avg_pop_q2, avg_pop_q3, avg_pop_q4]
        avg_as = [avg_a_q1, avg_a_q2, avg_a_q3, avg_a_q4]

        user_input = input("\nDisplay scatterplot with a-value as percentage of population? [Y/N] ")
        while user_input.lower() not in ['y', 'n']:
            user_input = input('Either "Y" or "N": ')

        if user_input.lower() == "y":
            avg_pops = np.asarray(avg_pops)
            avg_as = np.asarray(avg_as)
            avg_as = avg_as / avg_pops

        fig, ax = plt.subplots()
        ax.scatter(avg_pops, avg_as)
        qs = ["Qrt1", "Qrt2", "Qrt3", "Qrt4"]
        for i, txt in enumerate(qs):
            ax.annotate(txt, (avg_pops[i], avg_as[i]))

        plt.xlabel("Avg pop of quartile")
        plt.ylabel("Avg a-value of quartile")
        plt.title("A-values compared to average population size of quartiles")
        plt.show()


def main():
    print("Hypothesis: large cities grow larger")
    db = HypothesisProgram()
    db.run()


if __name__ == "__main__":
    main()
