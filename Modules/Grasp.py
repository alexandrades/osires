import sys
import os
import re
import json
from random import randint
from Utility.modules_utils import verify_constraints, save_simulation, get_vizinhos
from Utility.temp_files_handler import TempFilesHandler

class Grasp:
    def __init__(self, repository, model):
        self.repository = repository
        self.model = model
        self.current_values = self.getInitialValues()
        self.steps = self.get_steps()
        # self.limites = simulation_config['Resources']
        self.vizinhos = []
        # self.save_path = save_path

    def generate_random_inputs(self, resources):
        new_values = self.current_values
        for idx, resource in enumerate(resources.items()):
            new_values[idx] = randint(int(resource[1]['minimum_value']), int(resource[1]['maximum_value']))

        return new_values

    def execute_simulation(self, event):
        print("INICIANDO GRASP.")
        while not event.is_set():
            print("GERANDO VIZINHOS.")
            previous_values = self.current_values
            self.vizinhos = get_vizinhos(self.repository.resources, self.current_values)
            print("GERANDO \"INPUTS.CSV")
            with open("data/" + self.repository.input_file, 'r+') as file:
                line = file.readline()

            with open("data/" + self.repository.input_file, 'w') as file:
                file.write(line)
                for v in self.vizinhos:
                    l = ""
                    for v_i in v:
                        l += str(v_i) + " "

                    l += '\n'
                    file.write(l)

            print("INICIANDO EXECUÇÃO DAS SIMULAÇÕES.")
            if sys.platform.startswith('linux'):
                os.system("java -jar JaamSim2022-06.jar " + self.repository.model_file + " -h")
            else:
                os.system("java -jar JaamSim2022-06.jar data/" + self.repository.model_file + " -h")

            print("FIM DAS SIMULAÇÕES")
            print("COMPARANDO OS RESULTADOS COM O MELHOR ATUAL")
            with open("data/" + self.repository.model_file[:-3] + "dat", 'r') as output_file:
                header = output_file.readline()
                header = re.sub(r'\t+', ' ', header).split()
                lines = output_file.readlines()

                for line in lines:
                    line = re.sub(r'\t+', ' ', line).split()
                    if line[-1][-1] == ':':
                        print("TODOS OS RESULTADOS COMPARADOS")
                        break
                    print("COMPARAÇAO: ", line[-1], self.model.best_values['Value'])
                    if float(line[-1]) > float(self.model.best_values['Value']):
                        print("MELHORA ENCONTRADA.")

                        for i in range(0, len(line[2:6])):
                            self.current_values[i] = int(float(line[i+2]))
                        
                        resources = [int(float(resource)) for resource in line[2:]]
                        print("RESOURCES", resources)

                        if verify_constraints(header, resources, self.repository):    
                            # VERIFICAR SE AS RESTRIÇÕES SÃO ATENDIDAS
                            best_values = {"Params": [], "Value": ""}
                            best_values['Value'] = float(line[-1])
                            best_values['Params'] = line[2:6]
                            self.model.best_values = best_values
                            with open(f'./config/{self.repository.model_file[0:-4]}.config', 'w') as json_config:
                                json.dump(self.repository.get_dict_config(), json_config, indent=4)
                            # save_simulation(self.save_path, self.simulation_config)
                            
                            if self.repository.osires_file != '':
                                save_simulation(self.repository.osires_file, self.repository.get_dict_config())

            if self.current_values == previous_values:
                self.current_values = self.generate_random_inputs(self.repository.resources)
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

    