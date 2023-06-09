import re

import requests
from packaging import version
import subprocess



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
    output = subprocess.check_output(command, shell=True, encoding="utf-8")
    command = "./wbi install python --version " + python_versions + " --operating-system " + OS
    output = output + subprocess.check_output(command, shell=True, encoding="utf-8")
    command = "./wbi install quarto --version " + quarto_versions + " --operating-system " + OS
    output = output + subprocess.check_output(command, shell=True, encoding="utf-8")
    command = "./wbi install workbench --operating-system " + OS
    output = output + subprocess.check_output(command, shell=True, encoding="utf-8")
    return output
