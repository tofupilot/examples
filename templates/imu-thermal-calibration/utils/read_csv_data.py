from openhtf import PhaseResult
from pandas import read_csv

def read_csv_data(csv_path):
    return read_csv(csv_path, delimiter='\t')
