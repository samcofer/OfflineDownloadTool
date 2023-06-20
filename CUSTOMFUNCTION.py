import re

import requests
from packaging import version
import subprocess
import ast
import ctypes

class ReVal(ctypes.Structure):
    _fields_ = [("version", ctypes.c_char_p), ("url", ctypes.c_char_p)]

def vscode_lookup(vsc_version, namespace, name):
    while True:
        try:
            workbench_vs_code = vsc_version
            if not isinstance(version.parse(workbench_vs_code), version.Version):
                raise ValueError
            if int(workbench_vs_code.split('.')[0]) > 1:
                workbench_ver_too_high = 1
                raise ValueError
            else:
                break
        except ValueError:
            return "The entered VSCode version does not appear valid. Please re-enter a corrected VSCode Version"

    base_url = 'https://open-vsx.org/api/'
    lookup_url = f'{base_url}-/query?'
    response = requests.get(f"{lookup_url}extensionName={name}&namespaceName={namespace}")
    response.raise_for_status()
    json_package_response = response.json()

    if not json_package_response["extensions"]:
        return "No matching extensions found"

    response = requests.get(f"{base_url}{namespace}/{name}")
    response.raise_for_status()
    json_package_response = response.json()

    for key, value in json_package_response["allVersions"].items():
        url = f"{value}/file/package.json"
        response = requests.get(url)
        json_package_response = response.json()
        print("Checking", json_package_response["name"], "version:", key)
        json_vs_code_version = json_package_response["engines"]["vscode"]
        str_vs_code_version = str(json_vs_code_version).strip('^')
        str_vs_code_version_clean = re.sub("[^0-9|.]", "", str_vs_code_version)
        if version.parse(str_vs_code_version_clean) < version.parse(workbench_vs_code):
            url = f"{value}"
            response = requests.get(url)
            json_correct_version_response = response.json()
            result = {'version': workbench_vs_code, 'ext_version': key, 'ext_req': str_vs_code_version,
                      'url': json_correct_version_response['files']['download']}
            return result

def URLRetrieval(r_versions, python_versions, quarto_versions, OS):
    command = "./wbi install r --version " + r_versions + " --operating-system " + OS
    r_output = ast.literal_eval(subprocess.check_output(command, shell=True, encoding="utf-8"))
    command = "./wbi install python --version " + python_versions + " --operating-system " + OS
    python_output = ast.literal_eval(subprocess.check_output(command, shell=True, encoding="utf-8"))
    command = "./wbi install quarto --version " + quarto_versions + " --operating-system " + OS
    quarto_output = ast.literal_eval(subprocess.check_output(command, shell=True, encoding="utf-8"))
    command = "./wbi install workbench --operating-system " + OS
    workbench_output = ast.literal_eval(subprocess.check_output(command, shell=True, encoding="utf-8"))
    return r_output, python_output, quarto_output,workbench_output

def URLRetrievalLib(r_versions, python_versions, quarto_versions, osstr):

    lib = ctypes.cdll.LoadLibrary('./wbi.so')

    lib.rurls.restype = ctypes.c_char_p
    lib.rurls.argtypes = [ctypes.c_char_p, ctypes.c_char_p]
    r_versions_dict = dict()
    for version in r_versions:
        r_url = lib.rurls(osstr.encode('utf-8'), version.encode('utf-8'))
        decode_string = r_url.decode('utf-8')
        r_versions_dict[version] = decode_string

    # print(r_versions_dict)

    lib.pythonurls.restype = ctypes.c_char_p
    lib.pythonurls.argtypes = [ctypes.c_char_p, ctypes.c_char_p]
    python_versions_dict = dict()
    for version in python_versions:
        python_versions = lib.pythonurls(osstr.encode('utf-8'), version.encode('utf-8'))
        decode_string = python_versions.decode('utf-8')
        python_versions_dict[version] = decode_string

    # print(python_versions_dict)

    lib.quartourls.restype = ctypes.c_char_p
    lib.quartourls.argtypes = [ctypes.c_char_p, ctypes.c_char_p]
    quarto_versions_dict = dict()
    for version in quarto_versions:
        quarto_url = lib.quartourls(osstr.encode('utf-8'), version.encode('utf-8'))
        decode_string = quarto_url.decode('utf-8')
        quarto_versions_dict[version] = decode_string

    # print(quarto_versions_dict)

    lib.workbenchurl.restype = ReVal
    lib.workbenchurl.argtypes = [ctypes.c_char_p]
    workbench_ReVal = lib.workbenchurl(osstr.encode('utf-8'))
    decode_URL = workbench_ReVal.url.decode('utf-8')
    decode_Version = workbench_ReVal.version.decode('utf-8')
    workbench_versions_dict = dict()
    workbench_versions_dict[decode_Version] = decode_URL

    # print(workbench_versions_dict)


    lib.driverurl.restype = ReVal
    lib.driverurl.argtypes = [ctypes.c_char_p]
    driver_ReVal = lib.driverurl(osstr.encode('utf-8'))
    decode_URL = driver_ReVal.url.decode('utf-8')
    decode_Version = driver_ReVal.version.decode('utf-8')
    driver_versions_dict = dict()
    driver_versions_dict[decode_Version] = decode_URL

    # print(driver_versions_dict)
    
    
    
    return r_versions_dict, python_versions_dict, quarto_versions_dict, workbench_versions_dict, driver_versions_dict