#!/usr/bin/env python2.7

import math, ast, sys
import matplotlib as mpl
mpl.use('Agg')

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import itertools as it
from scipy.stats import gaussian_kde

# Contains the values of all instances of all domains together, for a given obs% and the given constraint set.
class Instances:

    def __init__(self, name):
        self.name = name
        self.real_h_values = []
        self.h_values = []
        self.real_hc_values = []
        self.hc_values = []
        self.spread = []
        self.accuracy = []
        self.agreement = []

    def append(self, real_h_values, h_values, real_hc_values, hc_values, spread, agreement):
        self.real_h_values += real_h_values
        self.h_values += h_values
        self.real_hc_values += real_hc_values
        self.hc_values += hc_values
        self.spread += spread
        self.accuracy += [real_h == h for (real_h, h) in zip(real_h_values, h_values)]
        self.agreement += agreement


# Contains the Instances for each contraint set, for each obs%.
class Results:

    def __init__(self, domains, observabilities, constraint_sets, constraint_names):
        self.domains = domains
        self.observabilities = observabilities
        self.constraint_sets = constraint_sets
        self.constraint_names = constraint_names
        self.instances = self.read_lists()

    def read_lists(self):
        per_obs = []
        for obs in self.observabilities:
            per_c = []
            for c, name in zip(self.constraint_sets, self.constraint_names):
                instances = Instances(name)
                for domain in self.domains:
                    with open("%s-%s-%s.txt" % (domain, c, obs)) as f:
                        real_h_values = ast.literal_eval(f.readline())
                        h_values = ast.literal_eval(f.readline())
                        spread = ast.literal_eval(f.readline())
                        real_hc_values = ast.literal_eval(f.readline())
                        hc_values = ast.literal_eval(f.readline())
                        fnr = ast.literal_eval(f.readline())
                        fpr = ast.literal_eval(f.readline())
                        agreement = ast.literal_eval(f.readline())
                        instances.append(real_h_values, h_values, real_hc_values, hc_values, spread, agreement)
                per_c.append(instances)
            per_obs.append(per_c)
        return per_obs

    def get_mean_h_values(self):
        mean_values = []
        for obs_instance in self.instances:
            per_c = []
            for obs_c_instance in obs_instance:
                per_c.append(np.mean(obs_c_instance.real_hc_values))
            mean_values.append(per_c)
        return mean_values


# Functions to draw png plots.
class Plot:

    def get_name(self, x, y, obs = None):
        title = '{} vs {}'.format(x.name, y.name)
        file = title.replace(" ", "-")
        if obs != None:
            title = title + " - " + str(obs) + "%"
            file = file + "-" + str(obs)
        return title, file
           
    def mean_chart(self, h_values, observabilities, constraint_sets):
        df = pd.DataFrame(h_values,
                         index=[str(x) for x in observabilities],
                         columns=pd.Index(constraint_sets, name='Constraints'))
        title = "Average h-values per contraint set per obs%"
        ax = df.plot(kind='bar', figsize=(10,4), title=title)
        fig = ax.get_figure()
        fig.savefig("mean-%s.png" % '-'.join(constraint_sets))

    def scatter_plot(self, x, y, obs = None):    
        fig, ax = plt.subplots()
        plt.xlabel(x.name)
        plt.ylabel(y.name)
        title, file = self.get_name(x, y, obs)
        plt.title(title)
        x = x.real_hc_values
        y = y.real_hc_values
        xy = [(i, j) for i, j in zip(x, y)]
        sizes = [xy.count(p) * 4 + 8 for p in xy]
        max_h_value = max(max(x), max(y))
        ax.plot([0, max_h_value], [0, max_h_value], ls="--", c=".3")
        ax.scatter(x, y, s=sizes)
        ax.set_xlim((0,max_h_value))
        ax.set_ylim((0,max_h_value))
        x0,x1 = ax.get_xlim()
        y0,y1 = ax.get_ylim()
        ax.set_aspect(abs(x1-x0)/abs(y1-y0))
        fig.savefig('scatter-' + file + '.png')

    def agr_plot(self, i1, i2, obs = None):    
        fig, ax = plt.subplots()
        plt.xlabel("h1 - h2")
        plt.ylabel("Agr1 - Agr2")
        title, file = self.get_name(i1, i2, obs)
        x = [h1 - h2 for h1, h2 in zip(i1.real_hc_values, i2.real_hc_values)]
        y = [s1 - s2 for s1, s2 in zip(i1.agreement, i2.agreement)]
        xy = [(i, j) for i, j in zip(x, y)]
        sizes = [xy.count(p) * 4 + 8 for p in xy]
        ax.axvline(x=0, ls="--", c=".1")
        ax.axhline(y=0, ls="--", c=".1")
        ax.scatter(x, y, s=sizes, c=".4")
        xabs_max = abs(max(ax.get_xlim(), key=abs))
        ax.set_xlim(xmin=-xabs_max, xmax=xabs_max)
        yabs_max = abs(max(ax.get_ylim(), key=abs))
        ax.set_ylim(ymin=-yabs_max, ymax=yabs_max)
        x0,x1 = ax.get_xlim()
        y0,y1 = ax.get_ylim()
        ax.set_aspect(abs(x1-x0)/abs(y1-y0))
        ax.set_title(title)
        fig.savefig('agr-' + file + '.png')

    def plot_all(self, results, observabilities, constraint_sets):
        # Mean h-value Plot
        mean_values = results.get_mean_h_values()
        self.mean_chart(mean_values, observabilities, results.constraint_names)
        # Scatter & Quad Plots
        pairs = list(it.combinations(range(len(constraint_sets)), 2))
        for obs, instance in zip(observabilities, results.instances):
            for p in range(len(pairs)):
                i1 = instance[pairs[p][0]]
                i2 = instance[pairs[p][1]]
                self.scatter_plot(i1, i2, obs)
                self.agr_plot(i1, i2, obs)


# Functions to write data files.
class Dat:

    def get_name(self, x, y, obs = None):
        file = '{}-vs-{}'.format(x.name, y.name)
        if obs != None:
            file = file + "-" + str(obs)
        return title, file

    def agr_plot(self, i1, i2, obs = None):    
        x = [h1 - h2 for h1, h2 in zip(i1.real_hc_values, i2.real_hc_values)]
        y = [s1 - s2 for s1, s2 in zip(i1.agreement, i2.agreement)]
        x_neg = [h2 - h1 for h1, h2 in zip(i1.real_hc_values, i2.real_hc_values)]
        y_neg = [s2 - s1 for s1, s2 in zip(i1.agreement, i2.agreement)]
        file = open(self.get_name(i1, i2, obs) + '-agr.dat', "w")
        file.write("x y xn yn\n")
        for i in range(len(x)):
            file.write("%s %s %s %s\n" % (x[i], y[i], x_neg[i], y_neg[i]))
        file.close()

    def scatter_plot(self, i1, i2, obs = None):    
        x = i1.real_hc_values 
        y = i2.real_hc_values
        xy = [(i, j) for i, j in zip(x, y)]
        sizes = [xy.count(p) * 4 for p in xy]
        file = open(self.get_name(i1, i2, obs) + '-scatter.dat', "w")
        file.write("x y s\n")
        for i in range(len(x)):
            file.write("%s %s %s\n" % (x[i], y[i], sizes[i]))
        file.close()

    def print_percentages(self, results, observabilities, constraint_sets):
        pairs = list(it.combinations(range(len(constraint_sets)), 2))
        better = [0.0] * len(pairs)
        worse = [0.0] * len(pairs)
        draw = [0.0] * len(pairs)
        for obs, instance in zip(observabilities, results.instances):
            for p in range(len(pairs)):
                i1 = instance[pairs[p][0]]
                i2 = instance[pairs[p][1]]
                for h1, h2 in zip(i1.real_hc_values, i2.real_hc_values):
                    if h1 > h2:
                        better[p] += 1
                    elif h2 > h1:
                        worse[p] += 1
                    else:
                        draw[p] += 1
        for p in range(len(pairs)):
            i1 = instance[pairs[p][0]]
            i2 = instance[pairs[p][1]]
            better[p] = better[p] / len(i1.real_hc_values) / len(observabilities) * 100
            worse[p] = worse[p] / len(i1.real_hc_values) / len(observabilities) * 100
            draw[p] = draw[p] / len(i1.real_hc_values) / len(observabilities) * 100
            print(i1.name + " vs " + i2.name)
            print(i1.name + " better than " + i2.name + ": %.2f" % better[p] + "%")
            print(i2.name + " better than " + i1.name + ": %.2f" % worse[p] + "%")
            print(i1.name + " equal to " + i2.name + ": %.2f" % draw[p] + "%")
            print("")

    def write_all(self, results, observabilities, constraint_sets):
        # Scatter & Quad Plots Data
        pairs = list(it.combinations(range(len(constraint_sets)), 2))
        for obs, instance in zip(observabilities, results.instances):
            for p in range(len(pairs)):
                i1 = instance[pairs[p][0]]
                i2 = instance[pairs[p][1]]
                self.scatter_plot(i1, i2, obs)
                self.agr_plot(i1, i2, obs)


# Writes data files and draws plots.
def generate_all(dat, png, domains, constraint_sets, constraint_names):
    observabilities = [10, 30, 50, 70]
    results = Results(domains, observabilities, constraint_sets, constraint_names)
    if dat:
        dat = Dat()
        dat.print_percentages(results, observabilities, constraint_sets)
        dat.write_all(results, observabilities, constraint_sets)
    if png:
        plot = Plot()
        plot.plot_all(results, observabilities, constraint_sets)


if __name__ == '__main__':
    # Domains
    fast = True
    # Constraint set
    lmc = False
    dr = False
    flow = False
    basic = False
    # Files
    png = False
    dat = False
    # Parse
    for arg in sys.argv:
        if arg == '-fast':
            fast = True
        elif arg == '-full':
            fast = False
        elif arg == '-lmc':
            lmc = True
        elif arg == '-del':
            dr = True
        elif arg == '-flow':
            flow = True
        elif arg == '-basic':
            basic = True
        elif arg == '-png':
            png = True
        elif arg == '-dat':
            dat = True
    if fast:
        domains = [
        'blocks-world-optimal', 
        'depots-optimal', 
        'driverlog-optimal', 
        'dwr-optimal', 
        'rovers-optimal', 
        'sokoban-optimal'
        ]
    else:
        domains = [
        'blocks-world-optimal', 
        'depots-optimal', 
        'driverlog-optimal', 
        'dwr-optimal', 
        'easy-ipc-grid-optimal', 
        'ferry-optimal', 
        'logistics-optimal', 
        'miconic-optimal', 
        'rovers-optimal', 
        'satellite-optimal', 
        'sokoban-optimal',
        'zeno-travel-optimal'
        ]
    # Create files
    if basic:
        generate_all(dat, png, domains,
            ["delta-cl", "delta-cp", "delta-cs", "delta-cd", "delta-cf1"],
            ["LMC", "PH", "SEQ", "DEL", "F1"])
    if lmc:
        generate_all(dat, png, domains,
            ["delta-cl", "delta-o-cl"], 
            ["LMC", "LMC+"])
    if dr:
        generate_all(dat, png, domains,
            ["delta-cd", "delta-o-cd"],
            ["DEL", "DEL+"])
    if flow:
        generate_all(dat, png, domains,
            ["delta-cf1", "delta-cf2"],
            ["F1", "F2"])