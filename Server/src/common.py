import sys
import pathlib

app_path = pathlib.Path().absolute()

if sys.platform == "linux" or sys.platform == "linux2" or sys.platform == "darwin":
    common_path = str(app_path) + '/Common/'
elif sys.platform == "win32" or sys.platform == "win64":
    common_path = str(app_path) + '\\Common\\'


sys.path.append(common_path)
