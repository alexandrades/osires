from plyer import filechooser
import json
import re
import os

def add_config_parameter(config_file, key, value):
    with open(f'./config/{config_file[0:-4]}.config', 'r+') as fr:
        config = json.load(fr)
        config[key] = value
        with open(f'./config/{config_file[0:-4]}.config', 'w') as fw:
            json.dump(config, fw)


def verify_constraints(header, resources, repository):
    operators = ['>', '<', '==', '+', '-', '*', '/', '!=', '**', '>=', '<=', '%', 'and', 'or', 'not']
    mapping = {}

    for idx, resource in enumerate(resources):
        mapping[header[idx+1]] = resource

    for constraint in repository.constraints:
        constraint = constraint.split()
        for idx, element in enumerate(constraint):
            if re.match(r'^-?\d+(\.\d+)?$', element) is not None:
                break
            
            if (element not in operators):
                constraint[idx] = f"mapping['{element}']"

        constraint = ' '.join(constraint)
        if not eval(constraint):
            return False
    
    return True


def save_simulation(save_path, opt_config):
    with open(f'{save_path}.osires', 'w') as saved_file:
        json.dump(opt_config, saved_file, indent=4)
    print("Atualizando")

    
def train_split(output_file_path, resources):
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

def get_vizinhos(resources, current_values):
        vizinhos = []
        n = int((100 / len(resources)) / 2)

        for idx, resource in enumerate(resources.items()):
            step = resource[1]['step_value']
            top = resource[1]['maximum_value']
            bottom = top
            had_colision = 0

            for j in range(0, n):
                top += step
                bottom -= step

                if top > resource[1]['maximum_value']:
                    top = resource[1]['minimum_value']
                    had_colision = -1

                if bottom < resource[1]['minimum_value']:
                    bottom = resource[1]['maximum_value']
                    had_colision = -1

                if top > bottom and had_colision == -1:
                    break
                
                top_neighbor = current_values[:]
                bottom_neighbor = current_values[:]
                top_neighbor[idx] = top
                bottom_neighbor[idx] = bottom
                
                vizinhos.append(top_neighbor)
                vizinhos.append(bottom_neighbor)

        return vizinhos