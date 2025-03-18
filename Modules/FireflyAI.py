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
        i0 = self.intensity
        i1 = firefly.intensity
        r = np.linalg.norm(firefly.position - firefly.position)
        if(i1 < 0):
            aux = i1
            i1 = -i0
            i0 = -aux 
        relative_intensity = i1 * np.exp(-gamma * r**2)
        if relative_intensity > i0:
            return True
        return False

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

    def evaluate(self, header, f, repository):
        values = f([firefly.position for firefly in self.fireflys], header)
        i = 0
        for value, firefly in zip(values, self.fireflys):
            firefly.evaluate(value)

            print("COMPARAÇAO: ", i, value, self.best_value)
            i += 1

            if (self.max_prob and value > self.best_value) or (not self.max_prob and value < self.best_value):
                self.best_value = value
                self.g_best = np.copy(firefly.best_position)
                with open(f'./config/{repository.model_file[0:-4]}.config', 'w') as json_config:
                    json.dump(repository.get_dict_config(), json_config, indent=4)
                # save_simulation(self.save_path, self.simulation_config)
                
                if repository.osires_file != '':
                    save_simulation(repository.osires_file, repository.get_dict_config())

    def update(self, header, f, repository):
        self.evaluate(header, f, repository)
        for i, firefly in enumerate(self.fireflys):
            for j, firefly2 in enumerate(self.fireflys):
                if (firefly2.intensity > firefly.intensity):
                    if (firefly.relative_intensity(firefly2, self.gamma)):
                        firefly.move(self.beta, self.gamma, self.alpha, self.delta, firefly2.position)

        return self.best_value, self.g_best.tolist()
    
class FSO_AI:
    def __init__(self, repository, model):
        self.repository = repository
        self.model = model
        self.AI_model = None
        self.header = None
        self.current_values = self.getInitialValues()
        self.steps = np.array(self.get_steps(), dtype=float)
        # self.limites = simulation_config['Resources']
        self.vizinhos = []
        self.best_values_set = {'Values': [], 'Interactions': []}
        self.interaction = 0
        self.max_prob = self.repository.opt_type != "MIN"
        print("GERANDO VAGALUMES.")
        self.swarm = FireflySwarm(100, len(self.current_values), [int(resource['minimum_value']) for resource in self.repository.resources.values()], [int(resource['maximum_value']) for resource in self.repository.resources.values()], self.max_prob, scale=self.steps)
        # self.save_path = save_path
        print("files:", self.repository.model_file)

    def execute_simulation(self, event):
        print("INICIANDO FIREFLY AI.")
        self.AI_model, self.header = self.model_train(event)
        best_values = {"Params": [], "Value": ""}
        best_values['Params'] = self.current_values
        best_values['Value'] = float(self.repository.best_values['Value'])
        self.update_params(best_values)

        while not event.is_set():
            print("MOVENDO AS VAGALUMES.")
            aux = {"Params": [], "Value": ""}
            aux['Value'], aux['Params'] = self.swarm.update(self.header, self.generator, self.repository)

            if(aux['Value'] > best_values['Value'] and self.max_prob) or (aux['Value'] < best_values['Value'] and not self.max_prob):
                best_values = aux

            self.update_params(best_values)
            print("FIM DA COMPARAÇÃO.")
        
        #PARA ANÁLISE DE RESULTADOS
        print("Salvando os resultados em Firefly_AI_"+self.repository.model_file[:-4]+".json")
        with open("data/results/Firefly_AI_"+self.repository.model_file[:-4]+".json", 'w') as file:
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
    