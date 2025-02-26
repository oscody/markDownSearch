from datetime import datetime
import os


def get_date_time():
    return datetime.now().strftime('%Y-%m-%d %H:%M:%S')

def get_file_created_date(file_path):
    date_created = datetime.fromtimestamp(os.path.getctime(file_path)).strftime("%Y-%m-%d %H:%M:%S")

