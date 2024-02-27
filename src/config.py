import yaml
import os

with open('config.yaml', 'r') as f:
    config = yaml.load(f, Loader=yaml.FullLoader)

# Create folders if they don't exist
if config['TEMP_FOLDER'] != "" and not os.path.isdir(config['TEMP_FOLDER']):
    os.makedirs(config['TEMP_FOLDER'])
if config['RESULTS_FOLDER'] != "" and not os.path.isdir(config['RESULTS_FOLDER']):
    os.makedirs(config['RESULTS_FOLDER'])