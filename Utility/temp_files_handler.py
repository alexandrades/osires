import os
import re
from random import randint

class TempFilesHandler:

    @classmethod
    def create_temp_files(self, model_file_path, input_file_path):
        try:
            os.system(f'copy "{model_file_path}" data')
        except Exception as e:
            print(e)
        
        try:
            os.system(f'copy "{input_file_path}" data')
        except Exception as e:
            print(e)

    @classmethod
    def get_resources_names(self, input_file):
        print(input_file)
        with open(os.path.join('data', input_file), 'r') as f_input_file:
            resources = [resource[1:] for resource in f_input_file.readline().split()]
        
        return resources
    
    @classmethod
    def get_output_list(self, model_file):
         with open(f'data/{model_file}', 'r') as f_model_file:
            lines = f_model_file.readlines()
            rol = ""
            for line in lines:
                if "RunOutputList" in line:
                    rol = line[:]

            resources = re.sub('\{\s|\s\}', ' ', rol).split()
            # print("Resources", resources)
            return resources[2:]
         
    @classmethod
    def generate_random_inputs(self, input_file, resources):
        print(resources)

        with open("data/" + input_file, 'r+') as file:
            line = file.readline()

            for i in range(0, 101):
                param_value = ""

                for parameter, values in resources.items():
                    if param_value == "":
                        param_value = str(randint(values['minimum_value'], values['maximum_value']))
                    else:
                        param_value = param_value + " " + str(randint(values['minimum_value'], values['maximum_value']))
                param_value = param_value + '\n'
                file.write(param_value)

    @classmethod
    def save_result(self, model_file, output_file_path):
        with open("data/" + model_file[:-3] + "dat", 'r') as temp_file:
            lines = temp_file.readlines()

        for idx, line in enumerate(lines):
            items = re.sub(r'\t+', ' ', line).split()

            try:
                float(items[0])
            except:
                lines.insert(0, lines.pop(idx))
                with open(f'data/{model_file[:-3]}dat', 'w') as rewrite_file:
                    rewrite_file.writelines(lines)
            
        with open(output_file_path, 'r+') as temp_final:
            lines_final = temp_final.readlines()
            if len(lines_final) == 0:
                temp_final.write(lines[0])

        with open(output_file_path, 'a') as final_file:
            final_file.writelines(lines[1:])


    @classmethod
    def clear_input_file(self, input_file):
        with open("data/" + input_file, 'r+') as file:
            line = file.readline()

            with open("data/" + input_file, 'w') as clear_file:
                clear_file.write(line)

    @classmethod
    def getInitialValues(self, best_values, resources):
        if best_values['Value'] > 0:
            return best_values['Params']

        initial_values = []
        for resource, resource_value in resources.items():
            initial_values.append(resource_value['initial_value'])
        return initial_values
    
    @classmethod
    def get_steps(self, resources):
        steps = []
        for resource, resource_value in resources.items():
            steps.append(resource_value['step_value'])
        return steps
