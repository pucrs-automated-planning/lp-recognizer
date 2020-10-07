#!/usr/bin/env python2.7

import math, ast
import matplotlib as mpl
mpl.use('Agg')
mpl.use('pgf')
mpl.rcParams.update({
    "pgf.texsystem": "pdflatex",
    'font.family': 'serif',
    'text.usetex': True,
    'pgf.rcfonts': False,
})

import matplotlib.pyplot as plt
import matplotlib.cm as cm
import numpy as np
import pandas as pd
from scipy.stats import gaussian_kde

# Trocar pra estrelinhas
# Testar com eixo logaritmico
# 

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

    def get_correlations(self, other):
        # Using h-value of real goal
        accuracy_correlation = 0
        accuracy_inv_correlation = 0
        accuracy_no_correlation = 0
        for h1, h2, a1, a2 in zip(self.h_values, other.h_values, self.accuracy, other.accuracy):
            correlation = (h1 - h2) * (a1 - a2)
            if correlation > 0:
                accuracy_correlation += 1
            elif correlation < 0:
                accuracy_inv_correlation += 1
            else:
                accuracy_no_correlation += 1
        spread_correlation = 0
        spread_inv_correlation = 0
        spread_no_correlation = 0
        for h1, h2, a1, a2 in zip(self.h_values, other.h_values, self.spread, other.spread):
            correlation = (h1 - h2) * (a1 - a2)
            if correlation > 0:
                spread_correlation += 1
            elif correlation < 0:
                spread_inv_correlation += 1
            else:
                spread_no_correlation += 1
        # Using h-value of chosen goal
        real_accuracy_correlation = 0
        real_accuracy_inv_correlation = 0
        real_accuracy_no_correlation = 0
        for h1, h2, a1, a2 in zip(self.real_h_values, other.real_h_values, self.accuracy, other.accuracy):
            correlation = (h1 - h2) * (a1 - a2)
            if correlation > 0:
                real_accuracy_correlation += 1
            elif correlation < 0:
                real_accuracy_inv_correlation += 1
            else:
                real_accuracy_no_correlation += 1
        real_spread_correlation = 0
        real_spread_inv_correlation = 0
        real_spread_no_correlation = 0
        for h1, h2, a1, a2 in zip(self.real_h_values, other.real_h_values, self.spread, other.spread):
            correlation = (h1 - h2) * (a1 - a2)
            if correlation > 0:
                real_spread_correlation += 1
            elif correlation < 0:
                real_spread_inv_correlation += 1
            else:
                real_spread_no_correlation += 1
        return [real_accuracy_correlation, real_accuracy_inv_correlation, real_accuracy_no_correlation, \
            real_spread_correlation, real_spread_inv_correlation, real_spread_no_correlation, \
            accuracy_correlation, accuracy_inv_correlation, accuracy_no_correlation, \
            spread_correlation, spread_inv_correlation, spread_no_correlation]

    def append(self, real_h_values, h_values, real_hc_values, hc_values, spread, agreement):
        self.real_h_values += real_h_values
        self.h_values += h_values
        self.real_hc_values += real_hc_values
        self.hc_values += hc_values
        self.spread += spread
        self.accuracy += [real_h == h for (real_h, h) in zip(real_h_values, h_values)]
        self.agreement += agreement

def get_average_col(rows, n_cols):
    means = []
    for c in range(n_cols):
        means.append(np.mean([row[c] for row in rows]))
    return means

class Results:
    def __init__(self, domains, observabilities, constraint_sets, constraint_names, correlation_names):
        self.domains = [d + "-optimal" for d in domains]# + [d + "-suboptimal" for d in domains]
        self.observabilities = observabilities
        self.constraint_sets = constraint_sets
        self.constraint_names = constraint_names
        self.correlation_names = correlation_names
        self.instances = self.read_lists()

    def read_lists(self):
        per_obs = []
        for obs in self.observabilities:
            per_c = []
            for c, name in zip(self.constraint_sets, self.constraint_names):
                instances = Instances(name)
                for domain in self.domains:
                    with open("%sh_%s_%s.txt" % (domain, obs, c)) as f:
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

    def combine_instances(self):
                    real_h_values = ast.literal_eval(f.readline())
                    h_values = ast.literal_eval(f.readline())
                    spread = ast.literal_eval(f.readline())
                    #delta_values = ast.literal_eval(f.readline())
                    per_c.append(Instances(name, real_h_values, h_values, spread))

    def get_mean_h_values(self):
        return [[np.mean(y.real_h_values) for y in x] for x in self.instances]

    def get_correlation_data(self, obs):
        names = []
        correlations = []
        const_instances = self.instances[obs]
        n_rows = len(const_instances)
        n_cols = len(self.correlation_names)
        # For each pair
        for i in range(n_rows):
            correlations.append(const_instances[i-1].get_correlations(const_instances[i])[0:n_cols])
            names.append(get_title(const_instances[i-1], const_instances[i]))
        # correlations[c]
        return correlations, names

    def get_mean_correlation_data(self):
        n_cols = len(self.correlation_names)
        # (Data per const) per obs
        correlations_o_c = []
        for obs in range(len(self.observabilities)):
            correlations, names = self.get_correlation_data(obs)
            correlations_o_c.append(correlations)
        # Transpose to (Data per obs) per const
        correlations_c_o = list(map(list, zip(*correlations_o_c))) 
        # (Mean per obs) per const
        correlations = [get_average_col(correlations_o, n_cols) for correlations_o in correlations_c_o]
        return correlations, names


class Plot:

    def __init__(self, ext=".pgf"):
        self.ext = ext

    def get_title(self, x, y, obs = None):
        title = '{} vs {}'.format(x.name, y.name)
        if obs != None:
            title = str(obs) + "\% - " + title
        return title

    def scatter_plot(self, x, y, obs = None):    
        fig, ax = plt.subplots()
        plt.xlabel(x.name)
        plt.ylabel(y.name)
        title = self.get_title(x, y, obs)
        #plt.title(title)
        x = x.real_h_values
        y = y.real_h_values
        xy = np.vstack([x,y])
        colors = gaussian_kde(xy)(xy)
        area = 8
        max_h_value = max(max(x), max(y))
        ax.plot([0, max_h_value], [0, max_h_value], ls="--", c=".3")
        ax.scatter(x, y, c=colors, s=area)
        ax.set_xlim((0,max_h_value))
        ax.set_ylim((0,max_h_value))
        x0,x1 = ax.get_xlim()
        y0,y1 = ax.get_ylim()
        ax.set_aspect(abs(x1-x0)/abs(y1-y0))
        fig.set_size_inches(w=3.2, h=2.5)
        fig.savefig(title + ' scatter.' + self.ext)
           
    def mean_chart(self, h_values, observabilities, constraint_sets):
        df = pd.DataFrame(h_values,
                         index=[str(x) for x in observabilities],
                         columns=pd.Index(constraint_sets, name='Constraints'))
        title = "" if "pgf" in self.ext else "Average h-values per contraint set per obs"
        ax = df.plot(kind='bar', figsize=(10,4), title=title)
        fig = ax.get_figure()
        fig.set_size_inches(w=3.2, h=1.8)
        fig.savefig("h-values" + self.ext)

    def count_chart(self, results_per_obs, obs = None):
        col = results_per_obs.correlation_names
        if obs != None:
            correlations, row = results_per_obs.get_correlation_data(obs)
        else:
            correlations, row = results_per_obs.get_mean_correlation_data()
        # Mean of all pairs
        means = get_average_col(correlations, len(col))
        correlations.append(means)
        row.append("Mean")
        df = pd.DataFrame(correlations,
                         index=row,
                         columns=pd.Index(col, name='Number of'))
        title = "Accuracy & Spread vs h-value Correlation"
        if obs != None:
            title += " - " + str(results_per_obs.observabilities[obs])
        else:
            title += " (average)"
        if "pgf" not in self.ext:
            ax = df.plot(kind='barh', figsize=(10,4), title=title)
        ax = df.plot(kind='barh', figsize=(10,4))
        ax.invert_yaxis()
        fig = ax.get_figure()
        fig.set_size_inches(w=3.2, h=2.5)
        fig.savefig(title + self.ext)

    def quad_plot_spread(self, i1, i2, obs = None):    
        fig, ax = plt.subplots()
        plt.xlabel("h1 - h2")
        plt.ylabel("s1 - s2")
        title = self.get_title(i1, i2, obs)
        x = [h1 - h2 for h1, h2 in zip(i1.real_h_values, i2.real_h_values)]
        y = [s1 - s2 for s1, s2 in zip(i1.spread, i2.spread)]
        xy = [(i, j) for i, j in zip(x, y)]
        sizes = [xy.count(p) * 4 for p in xy]
        max_h_value = max(max(x), max(y))
        ax.axvline(x=0, ls="--", c=".1")
        ax.axhline(y=0, ls="--", c=".1")
        ax.scatter(x, y, s=sizes, c=".4")
        ax.set_xlim((-max_h_value,max_h_value))
        ax.set_ylim((-max_h_value,max_h_value))
        x0,x1 = ax.get_xlim()
        y0,y1 = ax.get_ylim()
        ax.set_aspect(abs(x1-x0)/abs(y1-y0))
        if "pgf" not in self.ext:
            ax.set_title(title)
        #fig.set_size_inches(w=3.2, h=2.5)
        fig.savefig(title + ' quad_spread.png')

    def plot_all(self, results, observabilities, constraint_sets):
        mean_values = results.get_mean_h_values()
        print(mean_values)
        # h-value distribution
        #self.mean_chart(mean_values, observabilities, constraint_names)
        # Scatter & Quad Plots
        for obs, values in zip(observabilities, results.instances):
            for c in range(len(constraint_sets)):
                #self.scatter_plot(values[c-1], values[c], obs)
                self.quad_plot_spread(values[c-1], values[c], obs)
        # Correlations
        #for o in range(len(observabilities)):
        #    self.count_chart(results, o)
        #self.count_chart(results)


class Dat:

    def get_title(self, x, y, obs = None):
        title = '{} vs {}'.format(x.name, y.name)
        if obs != None:
            title = str(obs) + " - " + title
        return title

    def quad_plot_agreement(self, i1, i2, obs = None):    
        x = [h1 - h2 for h1, h2 in zip(i1.real_hc_values, i2.real_hc_values)]
        y = [s1 - s2 for s1, s2 in zip(i1.agreement, i2.agreement)]
        x_neg = [h2 - h1 for h1, h2 in zip(i1.real_hc_values, i2.real_hc_values)]
        y_neg = [s2 - s1 for s1, s2 in zip(i1.agreement, i2.agreement)]
        #xy = [(i, j) for i, j in zip(x, y)]
        #sizes = [xy.count(p) * 4 for p in xy]
        file = open(self.get_title(i1, i2, obs) + ' quad.dat', "w")
        file.write("x y xn yn\n")
        for i in range(len(x)):
            file.write("%s %s %s %s\n" % (x[i], y[i], x_neg[i], y_neg[i]))
        file.close()

    def scatter_plot(self, i1, i2, obs = None):    
        x = i1.real_hc_values 
        y = i2.real_hc_values
        xy = [(i, j) for i, j in zip(x, y)]
        sizes = [xy.count(p) * 4 for p in xy]
        file = open(self.get_title(i1, i2, obs) + ' scatter.dat', "w")
        file.write("x y s\n")
        for i in range(len(x)):
            file.write("%s %s %s\n" % (x[i], y[i], sizes[i]))
        file.close()

    def print_percentages(self, results, observabilities, constraint_sets):
        better = [0.0] * len(constraint_sets)
        worse = [0.0] * len(constraint_sets)
        draw = [0.0] * len(constraint_sets)
        for obs, instance in zip(observabilities, results.instances):
            for c in range(len(constraint_sets)):
                i1 = instance[c-1]
                i2 = instance[c]
                for h1, h2 in zip(i1.real_hc_values, i2.real_hc_values):
                    if h1 > h2:
                        better[c] += 1
                    elif h2 > h1:
                        worse[c] += 1
                    else:
                        draw[c] += 1

        for c in range(len(constraint_sets)):
            i1 = instance[c-1]
            i2 = instance[c]
            better[c] = better[c] / len(i1.real_hc_values) / len(observabilities) * 100
            worse[c] = worse[c] / len(i1.real_hc_values) / len(observabilities) * 100
            draw[c] = draw[c] / len(i1.real_hc_values) / len(observabilities) * 100
            print(i1.name + " vs " + i2.name)
            print(i1.name + " better than " + i2.name + ": %.2f" % better[c] + "%")
            print(i2.name + " better than " + i1.name + ": %.2f" % worse[c] + "%")
            print(i1.name + " equal to " + i2.name + ": %.2f" % draw[c] + "%")
            print("")


    def write_all(self, results, observabilities, constraint_sets):
        # Scatter & Quad Plots
        for obs, instance in zip(observabilities, results.instances):
            for c in range(len(constraint_sets)):
                self.scatter_plot(instance[c-1], instance[c], obs)
                self.quad_plot_agreement(instance[c-1], instance[c], obs)

if __name__ == '__main__':
    observabilities = [10, 30, 50, 70]
    constraint_sets = ["lmcut_constraints()", "pho_constraints()", "state_equation_constraints()"]
    constraint_names = ["LMC", "PH", "SEQ"]
    correlation_names = ["Acc. CR > 1", "Acc. CR < 1", "Acc. CR = 0", "Spr. CR > 1", "Spr. CR < 1", "Spr. CR = 0"]
    domains = [
    'blocks-world', 
    'depots', 
    'driverlog', 
    'dwr', 
    'easy-ipc-grid', 
    'ferry', 
    'logistics', 
    'miconic', 
    'rovers', 
    'satellite', 
    'sokoban',
    'zeno-travel'
    ]
    results = Results(domains, observabilities, constraint_sets, constraint_names, correlation_names)
    #plot = Plot(".pgf")
    #plot.plot_all(results, observabilities, constraint_sets)
    dat = Dat()
    dat.print_percentages(results, observabilities, constraint_sets)
    dat.write_all(results, observabilities, constraint_sets)