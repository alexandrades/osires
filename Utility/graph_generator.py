import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import numpy as np

def build_graph(repository):
    fig, ax0 = plt.subplots(1, 1, figsize=(8, 4))
    if(repository.best_values_set != {} and repository.best_values_set['Interactions'] != {} and repository.best_values_set['Values'] != {}): 
        ax0.plot(repository.best_values_set['Interactions'], repository.best_values_set['Values'], linewidth = 2) 
        maxx = max(repository.best_values_set['Interactions'])
        maxy = max(repository.best_values_set['Values'])
        ax0.set_xlim(right = maxx + maxx/2)
        ax0.set_ylim(top = maxy + maxy/2)
    else: ax0.plot([], [], linewidth = 2)
    ax0.set(title='Optimizacion',
              xlabel ='Interaction',
              ylabel ='Value')
    ax0.set_xlim(left = 1)
    ax0.set_ylim(bottom = 0)
    ax0.grid(True)
    return plt.gcf()
