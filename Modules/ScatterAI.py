from random import randint
from sklearn.ensemble import RandomForestRegressor
from sklearn.tree import DecisionTreeRegressor
from sklearn.neighbors import KNeighborsRegressor
from sklearn.gaussian_process import GaussianProcessRegressor
from Utility.temp_files_handler import TempFilesHandler
from Utility.modules_utils import verify_constraints, save_simulation, train_split
import joblib
import os
import sys
import re
import json

class ScatterAI:

    def __init__(self, repository, model) -> None:
        self.repository = repository
        self.model = model

    def train_split(self, output_file_path, resources):
        train_x = []
        train_y = []

        with open(output_file_path, 'r') as data_file:
            lines = data_file.readlines()[1:]
            parameters_qtt = len(resources)

            for line in lines:
                line = re.sub(r'\t+', ' ', line).split()

                input = [float(r) for r in line[2:parameters_qtt+2]]
                output = [float(p) for p in line[parameters_qtt+2:]]

                train_x.append(input)
                train_y.append(output)

        return (train_x, train_y)


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
        
        model = None

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

        while not event.is_set():
            TempFilesHandler.generate_random_inputs(self.repository.input_file, self.repository.resources)

            with open("data/" + self.repository.input_file, 'r') as input_file:
                
                lines = input_file.readlines()[1:]

                
                with open(self.repository.output_file_path, 'r') as output_file:
                    header = output_file.readline()
                    header = re.sub(r'\t+', ' ', header).split()
                for idx, line in enumerate(lines):
                    print("Predicting")

                    
                    line = line.split()
                    test_x = [int(l) for l in line]
                    predicted = model.predict([test_x])
                    resources = test_x[:]

                    new_value = float(predicted[0][-1])
                    old_value = float(self.repository.best_values['Value']) * -1 if self.repository.opt_type == "MIN" else float(self.repository.best_values['Value'])

                    print("PREDICTED: \n\n", test_x, new_value)

                    if self.repository.opt_type == "MIN":
                        new_value = new_value * -1

                    resources.extend(predicted[0])
                    print("PRÉ-AVALIAÇÃO", new_value, old_value)
                    if new_value > old_value or old_value == 0:
                        if verify_constraints(header, resources, self.repository):
                            best_values = {"Params": [], "Value": ""}
                            best_values['Params'] = test_x[:]
                            new_value = round(new_value, 2)
                            best_values['Value'] = new_value * -1 if self.repository.opt_type == "MIN" else new_value
                            # best_result[-1] = resources[-1]
                            self.model.best_values = best_values
                            with open(f'Config/{self.repository.model_file[0:-4]}.config', 'w') as json_config:
                                json.dump(self.repository.get_dict_config(), json_config, indent=4)

                            if self.repository.osires_file != '':
                                save_simulation(self.repository.osires_file, self.repository.get_dict_config())

            TempFilesHandler.clear_input_file(self.repository.input_file)

            print("Ciclo encerrado")
        print("Fim da execução")
