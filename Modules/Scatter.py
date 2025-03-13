from random import randint
import os
import sys
import re
import json
from plyer import filechooser
from Utility.temp_files_handler import TempFilesHandler
from Utility.modules_utils import verify_constraints, save_simulation

class Scatter:

    def __init__(self, repository, model) -> None:
        self.repository = repository
        self.model = model
        self.vizinhos = []
        self.best_values_set = {'Values': [], 'Interactions': []}
        self.interaction = 0

    def compare_simulation_results(simulation_config, best_result):
        with open(f"data/{simulation_config['Model'][:-4]}.dat", 'r') as result_file:
            result_file.readline()
            lines = result_file.readlines()

            for line in lines:
                line = re.sub(r'\t+', ' ', line)
                line = line.split()

                if float(line[-1]) > float(best_result['Value']):
                    print("aprimorante")
                    resources = [int(float(resource)) for resource in line[2:(len(simulation_config['Resources']))+2]]
                    best_result['Params'] = resources[:]
                    best_result['Value'] = round(float(line[-1]), 2)
                print('ok')

    def execute_simulation(self, event):
        print("ENDEREÇO ATUALIZADO ", os.getcwd())

        while not event.is_set():
            TempFilesHandler.generate_random_inputs(self.repository.input_file, self.repository.resources)
            if sys.platform.startswith('linux'):
                os.system("java -jar JaamSim2024-08.jar " + self.repository.model_file + " -h")
            else:
                os.system("java -jar JaamSim2024-08.jar data/" + self.repository.model_file + " -h")

            if not event.is_set():
                TempFilesHandler.save_result(self.repository.model_file, self.repository.output_file_path)

            with open(f"data/{self.repository.model_file[:-4]}.dat", 'r') as result_file:
                header = result_file.readline()
                header = re.sub(r'\t+', ' ', header).split()
                lines = result_file.readlines()

                for line in lines:
                    self.interaction += 1

                    line = re.sub(r'\t+', ' ', line).split()
                    if(len(line) == 0): continue
                    if('Scenario' in line[0]): continue

                    resources = [int(float(resource)) for resource in line[2:]]

                    try:
                        new_value = float(line[-1])
                        old_value = float(self.repository.best_values['Value']) * -1 if self.repository.opt_type == "MIN" else float(self.repository.best_values['Value'])
                        old_params = self.repository.best_values['Params']
                    except:
                        continue

                    print("COMPARAÇAO: ", line[-1], self.model.best_values['Value'])

                    if self.repository.opt_type == "MIN":
                        new_value = new_value * -1

                    print("PRÉ-AVALIAÇÃO", line[-1], new_value, old_value, new_value > old_value)
                    if new_value > old_value or old_value == 0:
                        print("VALIDA\n")
                        if verify_constraints(header, resources, self.repository):
                            best_values = {"Params": [], "Value": ""}
                            best_values['Params'] = [r for r in resources[:len(self.repository.resources)]]

                            new_value = round(new_value, 2)
                            best_values['Value'] = new_value * -1 if self.repository.opt_type == "MIN" else new_value
                            
                            self.model.best_values = best_values
                            self.best_values_set['Interactions'].append(self.interaction)
                            self.best_values_set['Values'].append(best_values['Value'])

                            with open(f'Config/{self.repository.model_file[0:-4]}.config', 'w') as json_config:
                                json.dump(self.repository.get_dict_config(), json_config, indent=4)
                            
                            if self.repository.osires_file != '':
                                save_simulation(self.repository.osires_file, self.repository.get_dict_config())
                    
                    else:
                        self.best_values_set['Interactions'].append(self.interaction)
                        self.best_values_set['Values'].append(old_value)
                        best_values = {"Params": [], "Value": ""}
                        best_values['Value'] = old_value
                        best_values['Params'] = old_params
                        self.model.best_values = best_values
                    
                    self.model.best_values_set = self.best_values_set

                print('ok')

            TempFilesHandler.clear_input_file(self.repository.input_file)

            print("Ciclo encerrado")
        print("Fim da execução")
