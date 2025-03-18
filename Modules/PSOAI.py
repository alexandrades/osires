from random import randint
from sklearn.ensemble import RandomForestRegressor
from sklearn.tree import DecisionTreeRegressor
from sklearn.neighbors import KNeighborsRegressor
from sklearn.gaussian_process import GaussianProcessRegressor
from Utility.temp_files_handler import TempFilesHandler
from Utility.modules_utils import verify_constraints, save_simulation, train_split
import numpy as np
import joblib
import os
import sys
import re
import json

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

    def update(self, header, f, w = 0.5, c1 = 1.0, c2 = 1.0, repository = None):
        values = f([particle.position for particle in self.particles], header)
        i = 0
        for value, particle in zip(values, self.particles):
            particle.evaluate(value)
            print("COMPARAÇAO: ", i, value, self.best_value)
            i += 1
            if (self.max_prob and value > self.best_value) or (not self.max_prob and value < self.best_value):
                self.best_value = value
                self.g_best = np.copy(particle.best_position)
                with open(f'./config/{repository.model_file[0:-4]}.config', 'w') as json_config:
                    json.dump(repository.get_dict_config(), json_config, indent=4)
                # save_simulation(self.save_path, self.simulation_config)
                
                if repository.osires_file != '':
                    save_simulation(repository.osires_file, repository.get_dict_config())
            particle.update(w, c1, c2, self.g_best)

        return self.best_value, self.g_best.tolist()

class PSO_AI:
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
        self.AI_model = None
        self.header = None
        print("GERANDO PARTICULAS.")
        self.swarm = Swarm(100, len(self.current_values), [int(resource['minimum_value']) for resource in self.repository.resources.values()], [int(resource['maximum_value']) for resource in self.repository.resources.values()], self.max_prob, self.steps)
        # self.save_path = save_path
        print("files:", self.repository.model_file)

    def execute_simulation(self, event):
        print("INICIANDO PSO AI.")
        self.AI_model, self.header = self.model_train(event)
        best_values = {"Params": [], "Value": ""}
        best_values['Params'] = self.current_values
        best_values['Value'] = float(self.repository.best_values['Value'])
        self.update_params(best_values)
        
        while not event.is_set():
            print("MOVENDO AS PARTICULAS.")
            aux = {"Params": [], "Value": ""}
            aux['Value'], aux['Params'] = self.swarm.update(self.header, self.generator, 0.5, 1, 1, self.repository)

            if(aux['Value'] > best_values['Value'] and self.max_prob) or (aux['Value'] < best_values['Value'] and not self.max_prob):
                best_values = aux

            self.update_params(best_values)
            print("FIM DA COMPARAÇÃO.")
        
        #PARA ANÁLISE DE RESULTADOS
        print("Salvando os resultados em PSO_AI_"+self.repository.model_file[:-4]+".json")
        with open("data/results/PSO_AI_"+self.repository.model_file[:-4]+".json", 'w') as file:
            json.dump(self.best_values_set, file, indent=4)
                

    def generator(self, inputs, header):
        # Criando um vetor de valores para cada particula (Pré-setado)
        values = [(-np.inf if self.max_prob else np.inf) for _ in range(len(inputs))]
        
        print("REALIZANDO PREDIÇÕES")
        for idx, input in enumerate(inputs):
            predicted = self.AI_model.predict([input])
            resources = [i for i in input]
            resources.extend(predicted[0])
            
            try:
                new_value = float(predicted[0][-1])
            except:
                continue
            if (verify_constraints(header, resources, self.repository)):
                values[idx] = new_value
        print("FIM DAS PREDIÇÕES")

        return values
    
    def model_train(self, event):
        iterations = int(int(self.repository.min_simulations_train)/100)
        print("GERANDO DADOS DE TREINAMENTO")
        for i in range(0,iterations):
            if event.is_set():
                break
            
            TempFilesHandler.generate_random_inputs(self.repository.input_file, self.repository.resources)
            
            if sys.platform.startswith('linux'):
                os.system("java -jar JaamSim2024-08.jar " + self.repository.model_file + " -h")
            else:
                os.system("java -jar JaamSim2024-08.jar data/" + self.repository.model_file + " -h")

            TempFilesHandler.save_result(self.repository.model_file, self.repository.output_file_path)

            TempFilesHandler.clear_input_file(self.repository.input_file)

        print("TREINANDO O MODELO")

        if self.repository.ml_algorithm == "RF":
            if not os.path.exists(f"data/Models/{self.repository.model_file[:-4]}_RandomForestRegressor.joblib"):
                train_x, train_y = train_split(self.repository.output_file_path, self.repository.resources)
                model = RandomForestRegressor()
                model.fit(train_x, train_y)
                joblib.dump(model, f"data/Models/{self.repository.model_file[:-4]}_RandomForestRegressor.joblib")
            else:
                print("Loaded")
                model = joblib.load(f"data/Models/{self.repository.model_file[:-4]}_RandomForestRegressor.joblib")

        if self.repository.ml_algorithm == "DT":
            if not os.path.exists(f"data/Models/{self.repository.model_file[:-4]}_DecisionTree.joblib"):
                train_x, train_y = train_split(self.repository.output_file_path, self.repository.resources)
                model = DecisionTreeRegressor()
                print("TREINO:", train_x[:5], train_y[:5])
                model.fit(train_x, train_y)
                joblib.dump(model, f"data/Models/{self.repository.model_file[:-4]}_DecisionTree.joblib")
            else:
                print("Loaded")
                model = joblib.load(f"data/Models/{self.repository.model_file[:-4]}_DecisionTree.joblib")

        if self.repository.ml_algorithm == "KN":
            if not os.path.exists(f"data/Models/{self.repository.model_file[:-4]}_KNeighborsRegressor.joblib"):
                train_x, train_y = train_split(self.repository.output_file_path, self.repository.resources)
                model = KNeighborsRegressor()
                model.fit(train_x, train_y)
                joblib.dump(model, f"data/Models/{self.repository.model_file[:-4]}_KNeighborsRegressor.joblib")
            else:
                print("Loaded")
                model = joblib.load(f"data/Models/{self.repository.model_file[:-4]}_KNeighborsRegressor.joblib")

        if self.repository.ml_algorithm == "GP":
            if not os.path.exists(f"data/Models/{self.repository.model_file[:-4]}_GaussianProcessRegressor.joblib"):
                train_x, train_y = train_split(self.repository.output_file_path, self.repository.resources)
                model = GaussianProcessRegressor()
                model.fit(train_x, train_y)
                joblib.dump(model, f"data/Models/{self.repository.model_file[:-4]}_GaussianProcessRegressor.joblib")
            else:
                print("Loaded")
                model = joblib.load(f"data/Models/{self.repository.model_file[:-4]}_GaussianProcessRegressor.joblib")

        with open(self.repository.output_file_path, 'r') as output_file:
            lines = output_file.readlines()
            for line in lines:
                line = re.sub(r'\t+', ' ', line).split()
                if(len(line) == 0): continue
                if('Scenario' not in line[0]): continue
                header = line
                break
        print("Fim do treinamento do modelo")
        return model, header
                 
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
    