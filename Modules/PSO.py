import sys
import os
import re
import json
import copy
import numpy as np
from random import randint
from Utility.modules_utils import verify_constraints, save_simulation
from Utility.temp_files_handler import TempFilesHandler

class Particle():
    def __init__(self, n_dimensions, mins, maxs, max_prob, scale):
        self.mins = np.array(mins)
        self.maxs = np.array(maxs)
        self.scale = scale
        self.position = np.round(np.random.uniform(self.mins, self.maxs, n_dimensions)/self.scale)*self.scale
        self.velocity = np.zeros(n_dimensions)
        self.best_position = np.copy(self.position)
        self.max_prob = max_prob
        self.best_value = -np.inf if max_prob else np.inf

    def update(self, w, c1, c2, g_best):
        r1, r2 = np.random.random(self.position.shape), np.random.random(self.position.shape)
        self.velocity = (w * self.velocity +
                         c1 * r1 * (self.best_position - self.position) +
                         c2 * r2 * (g_best - self.position))
        self.position += self.velocity
        self.position = np.round(self.position/self.scale)*self.scale
        self.position = np.clip(self.position, self.mins, self.maxs)

    def evaluate(self, value):
        if (self.max_prob and value > self.best_value) or (not self.max_prob and value < self.best_value):
            self.best_value = value
            self.best_position = np.copy(self.position)

class Swarm():
    def __init__(self, n_particles, n_dimensions, mins, maxs, max_prob, scale=1):
        self.particles = [Particle(n_dimensions, mins, maxs, max_prob, scale) for _ in range(n_particles)]
        self.g_best = np.copy(self.particles[0].position)
        self.max_prob = max_prob
        self.best_value = -np.inf if max_prob else np.inf
        self.positions_history = []
        self.best_position_history = []

    def update(self, f, w = 0.5, c1 = 1.0, c2 = 1.0, repository = None):
        values = f([particle.position for particle in self.particles])
        i = 0
        for value, particle in zip(values, self.particles):
            particle.evaluate(value)
            print("COMPARAÇAO: ", i, value, self.best_value)
            i += 1
            if (self.max_prob and value > self.best_value) or (not self.max_prob and value < self.best_value):
                self.best_value = value
                self.g_best = np.copy(particle.best_position)
                with open(f'./config/{repository.model_file[0:-4]}.config', 'w') as json_config:
                    config_data = repository.get_dict_config()
                    json.dump(repository.get_dict_config(), json_config, indent=4)
                # save_simulation(self.save_path, self.simulation_config)
                
                if repository.osires_file != '':
                    save_simulation(repository.osires_file, repository.get_dict_config())
            particle.update(w, c1, c2, self.g_best)

        return self.best_value, self.g_best.tolist()

class PSO:
    def __init__(self, repository, model):
        self.repository = repository
        self.model = model
        self.current_values = self.getInitialValues()
        self.steps = np.array(self.get_steps(), dtype=float)
        # self.limites = simulation_config['Resources']
        self.vizinhos = []
        self.best_values_set = {'Values': [], 'Interactions': []}
        self.interaction = 0
        self.max_prob = self.repository.opt_type != "MIN"
        print("GERANDO PARTICULAS.")
        self.swarm = Swarm(100, len(self.current_values), [int(resource['minimum_value']) for resource in self.repository.resources.values()], [int(resource['maximum_value']) for resource in self.repository.resources.values()], self.max_prob, self.steps)
        # self.save_path = save_path
        print("files:", self.repository.model_file)

    def execute_simulation(self, event):
        print("INICIANDO PSO.")
        best_values = {"Params": [], "Value": ""}
        best_values['Params'] = self.current_values
        best_values['Value'] = float(self.repository.best_values['Value'])
        self.update_params(best_values)
        while not event.is_set():
            print("MOVENDO AS PARTICULAS.")
            aux = {"Params": [], "Value": ""}
            aux['Value'], aux['Params'] = self.swarm.update(self.generator, 0.5, 1, 1, self.repository)

            if(aux['Value'] > best_values['Value'] and self.max_prob) or (aux['Value'] < best_values['Value'] and not self.max_prob):
                best_values = aux

            self.update_params(best_values)
            print("FIM DA COMPARAÇÃO.")
        
        #PARA ANÁLISE DE RESULTADOS
        print("Salvando os resultados em PSO_"+self.repository.model_file[:-4]+".json")
        with open("data/results/PSO_"+self.repository.model_file[:-4]+".json", 'w') as file:
            json.dump(self.best_values_set, file, indent=4)
                

    def generator(self, inputs):
        # Criando um vetor de valores para cada particula (Pré-setado)
        values = [(-np.inf if self.max_prob else np.inf) for _ in range(len(inputs))]
        print("GERANDO \"INPUTS.CSV")
        with open("data/" + self.repository.input_file, 'r+') as file:
            line = file.readline()

        with open("data/" + self.repository.input_file, 'w') as file:
            file.write(line)
            for v in inputs:
                l = "\n"
                for v_i in v:
                    l += str(int(v_i)) + " "
                
                file.write(l)

        print("INICIANDO EXECUÇÃO DAS SIMULAÇÕES.")
        if sys.platform.startswith('linux'):
            os.system("java -jar JaamSim2024-08.jar " + self.repository.model_file + " -h")
        else:
            os.system("java -jar JaamSim2024-08.jar data/" + self.repository.model_file + " -h")

        print("FIM DAS SIMULAÇÕES")
        print("COMPARANDO OS RESULTADOS COM O MELHOR ATUAL")
        with open("data/" + self.repository.model_file[:-3] + "dat", 'r') as output_file:
            lines = output_file.readlines()
            for line in lines:
                line = re.sub(r'\t+', ' ', line).split()
                if(len(line) == 0): continue
                if('Scenario' not in line[0]): continue
                header = line
                break

            #print("HEADER: ", header)
            idx = 0

            for line in lines:
                line = re.sub(r'\t+', ' ', line).split()
                if(len(line) == 0): continue
                if('Scenario' in line[0]): continue

                try:
                    new_value = float(line[-1])
                except:
                    continue 

                self.interaction += 1

                for i in range(0, len(line[2:len(self.repository.resources)+2])):
                    self.current_values[i] = int(float(line[i+2]))
                
                resources = [int(float(resource)) for resource in line[2:]]
                #print("RESOURCES",idx, resources)
                idx+=1

                if (verify_constraints(header, resources, self.repository)):
                    print("Value fouded!")
                    values[int(line[0])-1] = new_value

                
        print("Shape", len(values))
        return values
                 
    def getInitialValues(self):
        if int(self.model.best_values['Value']) > 0:
            return self.model.best_values['Params']

        initial_values = []
        for resource, resource_value in self.repository.resources.items():
            initial_values.append(resource_value['initial_value'])
        return initial_values


    def get_steps(self):
        steps = []
        for resource, resource_value in self.repository.resources.items():
            steps.append(resource_value['step_value'])
        return steps

    def update_params(self, best_values):
        self.best_values_set['Interactions'].append(self.interaction)
        self.best_values_set['Values'].append(best_values['Value'])
        self.model.best_values = best_values
        self.model.best_values_set = self.best_values_set
    