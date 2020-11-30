import sys
import pathlib

app_path = pathlib.Path().absolute()
common_path = str(app_path) + '/Common/'
sys.path.append(common_path)
