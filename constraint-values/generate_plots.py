#!/usr/bin/env python2.7

import math, ast
import matplotlib as mpl
mpl.use('Agg')
import matplotlib.pyplot as plt
import matplotlib.cm as cm
import numpy as np
import pandas as pd
from scipy.stats import gaussian_kde

class Instances:
    def __init__(self, name, real_h_values, h_values, spread):
        self.name = name
        self.real_h_values = real_h_values
        self.h_values = h_values
        self.spread = spread
        self.accuracy = [real_h == h for (real_h, h) in zip(real_h_values, h_values)]

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

def get_title(x, y, obs = None):
    title = '{} vs {}'.format(x.name, y.name)
    if obs != None:
        title = str(obs) + "% - " + title
    return title

def get_average_col(rows, n_cols):
    means = []
    for c in range(n_cols):
        means.append(np.mean([row[c] for row in rows]))
    return means

class Results:
    def __init__(self, observabilities, constraint_sets, constraint_names, correlation_names):
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
                with open("h_%s_%s.txt" % (obs, c)) as f:
                    real_h_values = ast.literal_eval(f.readline())
                    h_values = ast.literal_eval(f.readline())
                    spread = ast.literal_eval(f.readline())
                    per_c.append(Instances(name, real_h_values, h_values, spread))
            per_obs.append(per_c)
        return per_obs

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


def generate_scatter_plot(x, y, obs = None):    
    fig, ax = plt.subplots()
    plt.xlabel(x.name)
    plt.ylabel(y.name)
    title = get_title(x, y, obs)
    plt.title(title)
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
    fig.savefig(title + ' scatter.png')

       
def generate_mean_chart(h_values, observabilities, constraint_sets):
    df = pd.DataFrame(h_values,
                     index=[str(x) for x in observabilities],
                     columns=pd.Index(constraint_sets, name='Constraints'))
    title = 'Average h-values per contraint set per obs%'
    ax = df.plot(kind='bar', figsize=(10,4), title=title)
    ax.get_figure().savefig("h-values.png")


def generate_count_chart(results_per_obs, obs = None):
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
        title += " - " + str(results_per_obs.observabilities[obs]) + '%'
    else:
        title += " (average)"
    ax = df.plot(kind='barh', figsize=(10,4), title=title)
    ax.invert_yaxis()
    ax.get_figure().savefig(title + ".png")
    print(title)


if __name__ == '__main__':
    observabilities = [10, 30, 50, 70]
    constraint_sets = ["lmcut_constraints()", "pho_constraints()", "state_equation_constraints()"]
    constraint_names = ["LMC", "PH", "SEQ"]
    correlation_names = ["Acc. CR > 1", "Acc. CR < 1", "Acc. CR = 0", "Spr. CR > 1", "Spr. CR < 1", "Spr. CR = 0"]
    results = Results(observabilities, constraint_sets, constraint_names, correlation_names)

    # h-value distribution
    mean_values = results.get_mean_h_values()
    print(mean_values)
    generate_mean_chart(mean_values, observabilities, constraint_names)

    # Scatter Plots
    for obs, values in zip(observabilities, results.instances):
        for c in range(len(constraint_sets)):
            generate_scatter_plot(values[c-1], values[c], obs)

    # Correlations
    for o in range(len(observabilities)):
        generate_count_chart(results, o)
    generate_count_chart(results)
