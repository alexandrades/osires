import sys
import os
import re
import json
import copy
import numpy as np
from random import randint
from Utility.modules_utils import verify_constraints, save_simulation
from Utility.temp_files_handler import TempFilesHandler

class Firefly():
    def __init__(self, n_dimensions, mins, maxs, max_prob, scale):
        self.mins = np.array(mins)
        self.maxs = np.array(maxs)
        self.scale = scale
        self.position = np.round(np.random.uniform(self.mins, self.maxs, n_dimensions)/self.scale)*self.scale
        self.best_position = np.copy(self.position)
        self.max_prob = max_prob
        self.best_value = -np.inf if max_prob else np.inf
        self.intensity = 0
        self.value = 0
    
    def relative_intensity(self, firefly, gamma):
        r = np.linalg.norm(firefly.position - firefly.position)
        relative_intensity = (firefly.intensity - self.intensity) * np.exp(-gamma * r**2)
        return relative_intensity

    def evaluate(self, value):
        self.value = value
        self.intensity = self.value if self.max_prob else -self.value
        if (self.max_prob and self.value > self.best_value) or (not self.max_prob and self.value < self.best_value):
            self.best_value = self.value
            self.best_position = np.copy(self.position)

    def move(self, beta, gamma, alpha, delta, best_position):
        r = np.linalg.norm(self.position - best_position)
        attraction = beta * np.exp(-gamma * r**2) * (best_position - self.position)
        acceleration = alpha * np.random.normal(0, 1, self.position.shape)
        self.position += attraction * acceleration        

        # Introduz um pequeno deslocamento aleatório para explorar mais a superfície
        self.position += delta * np.random.uniform(-1, 1, self.position.shape)
        self.position = np.round(self.position/self.scale)*self.scale

        # Garantir que as partículas não saiam dos limites
        self.position = np.clip(self.position, self.mins, self.maxs)


class FireflySwarm():
    def __init__(self, n_fireflys, n_dimensions, mins, maxs, max_prob, beta = 1.0, gamma = 1, alpha = 2.0, delta = 0.5, scale=1, gamma_auto = True):
        self.fireflys = [Firefly(n_dimensions, mins, maxs, max_prob, scale) for _ in range(n_fireflys)]
        self.beta = beta
        self.gamma = gamma
        self.alpha = alpha
        self.delta = delta
        self.gamma_auto = gamma_auto
        self.g_best = np.copy(self.fireflys[0].position)
        self.max_prob = max_prob
        self.best_value = -np.inf if max_prob else np.inf
        if self.gamma_auto: self.gamma_auto_update()

    def gamma_auto_update(self):
        mean_distance = np.mean([np.linalg.norm(f1.position - f2.position) for f1 in self.fireflys for f2 in self.fireflys if f1 != f2])
        self.gamma = 0.693 / (mean_distance**2)

    def evaluate(self, f, repository):
        values = f([firefly.position for firefly in self.fireflys])
        i = 0
        for value, firefly in zip(values, self.fireflys):
            firefly.evaluate(value)

            print("COMPARAÇAO: ", i, value, self.best_value)
            i += 1

            if (self.max_prob and value > self.best_value) or (not self.max_prob and value < self.best_value):
                self.best_value = value
                self.g_best = np.copy(firefly.best_position)
                with open(f'./config/{repository.model_file[0:-4]}.config', 'w') as json_config:
                    config_data = repository.get_dict_config()
                    json.dump(repository.get_dict_config(), json_config, indent=4)
                # save_simulation(self.save_path, self.simulation_config)
                
                if repository.osires_file != '':
                    save_simulation(repository.osires_file, repository.get_dict_config())

    def update(self, f, repository):
        self.evaluate(f, repository)
        for i, firefly in enumerate(self.fireflys):
            for j, firefly2 in enumerate(self.fireflys):
                if (firefly2.intensity > firefly.intensity):
                    if (firefly.relative_intensity(firefly2, self.gamma) > 0):
                        firefly.move(self.beta, self.gamma, self.alpha, self.delta, firefly2.position)

        return self.best_value, self.g_best.tolist()
    
class FSO:
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
        self.swarm = FireflySwarm(100, len(self.current_values), [int(resource['minimum_value']) for resource in self.repository.resources.values()], [int(resource['maximum_value']) for resource in self.repository.resources.values()], self.max_prob, scale=self.steps)
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
            aux['Value'], aux['Params'] = self.swarm.update(self.generator, self.repository)

            if(aux['Value'] > best_values['Value'] and self.max_prob) or (aux['Value'] < best_values['Value'] and not self.max_prob):
                best_values = aux

            self.update_params(best_values)
            print("FIM DA COMPARAÇÃO.")
        
        #PARA ANÁLISE DE RESULTADOS
        print("Salvando os resultados em Firefly_"+self.repository.model_file[:-4]+".json")
        with open("data/results/Firefly_"+self.repository.model_file[:-4]+".json", 'w') as file:
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
    