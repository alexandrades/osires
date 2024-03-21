from random import randint
from sklearn.ensemble import RandomForestRegressor
from sklearn.tree import DecisionTreeRegressor
from sklearn.neighbors import KNeighborsRegressor
from sklearn.gaussian_process import GaussianProcessRegressor
from Utility.temp_files_handler import TempFilesHandler
from Utility.modules_utils import verify_constraints, save_simulation, train_split, get_vizinhos
import joblib
import os
import sys
import re
import json

class GraspAI:
    def __init__(self, repository, model):
        self.repository = repository
        self.model = model
        self.current_values = self.getInitialValues()
        self.steps = self.get_steps()
        # self.limites = simulation_config['Resources']
        self.vizinhos = []
        # self.save_path = save_path

    def generate_random_values(self, resources):
        new_values = self.current_values
        for idx, resource in enumerate(resources.items()):
            new_values[idx] = randint(int(resource[1]['minimum_value']), int(resource[1]['maximum_value']))

        return new_values

    def execute_simulation(self, event):
        iterations = int(int(self.repository.min_simulations_train)/100)
        for i in range(0,iterations):
            if event.is_set():
                break
            
            TempFilesHandler.generate_random_inputs(self.repository.input_file, self.repository.resources)
            
            if sys.platform.startswith('linux'):
                os.system("java -jar JaamSim2022-06.jar " + self.repository.model_file + " -h")
            else:
                os.system("java -jar JaamSim2022-06.jar data/" + self.repository.model_file + " -h")

            TempFilesHandler.save_result(self.repository.model_file, self.repository.output_file_path)

            TempFilesHandler.clear_input_file(self.repository.input_file)

            print("Ciclo encerrado")
        print("Fim da execução")

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
            header = output_file.readline()
            header = re.sub(r'\t+', ' ', header).split()
            
        while not event.is_set():
            previous_values = self.current_values
            self.vizinhos = get_vizinhos(self.repository.resources, self.current_values)
            for vizinho in self.vizinhos:
                print("VIZINHO", [vizinho])
                predicted = model.predict([vizinho])
                resources = vizinho[:]
                resources.extend(predicted[0])
                
                new_value = float(predicted[0][-1])
                old_value = float(self.repository.best_values['Value']) * -1 if self.repository.opt_type == "MIN" else float(self.repository.best_values['Value'])

                if self.repository.opt_type == "MIN":
                    new_value = new_value * -1

                    print("Validação ", new_value, old_value)
                if new_value > old_value or old_value == 0:
                    self.current_values = resources[:len(self.repository.resources)]

                    # VERIFICA AS RESTRIÇÕES
                    if verify_constraints(header, resources, self.repository):
                        best_values = {"Params": [], "Value": ""}
                        best_values['Params'] = self.current_values
                        new_value = round(new_value, 2)
                        best_values['Value'] = new_value * -1 if self.repository.opt_type == "MIN" else new_value
                        self.model.best_values = best_values
                        with open(f'Config/{self.repository.model_file[0:-4]}.config', 'w') as json_config:
                                json.dump(self.repository.get_dict_config(), json_config, indent=4)
                        
                        if self.repository.osires_file != '':
                            save_simulation(self.repository.osires_file, self.repository.get_dict_config())

            if self.current_values == previous_values:
                self.current_values = self.generate_random_values(self.repository.resources)
            print("FIM DA COMPARAÇÃO.")


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
