import sys
sys.path.append("site-packages")

import logging

logging.info("Python version: %s", sys.version)
print(sys.version)

from time import sleep
import requests
import json
import datetime
from datetime import timedelta

print('Initializing data polling app')
authentication_key = 'mptni9iYgawgTtiIvpSkTI3ba1xltXmG'
authentication_secret = 'dFTlE2aL2wRLP0kbg2l0Af1B7oMrcYXf'
previous_id = ''

simplicate_projects_url = 'https://yellowarrow.simplicate.nl/api/v2/projects/project?limit=1&sort=-created&fields=created&q[created][gt]='
simplicate_employees_url = 'https://yellowarrow.simplicate.nl/api/v2/hrm/employee?fields=id&q[id]='

dataPolling = True

print('Running data polling app.. waiting for new projects')
while dataPolling:
    current_timestamp = datetime.datetime.now()
    check_timestamp = str(current_timestamp + timedelta(seconds=-11))
    request_projects = requests.get(simplicate_projects_url + check_timestamp,
                                    headers={
                                        'Authentication-Key': authentication_key,
                                        'Authentication-Secret': authentication_secret
                                    })
    if request_projects.status_code == 200 and request_projects.json()['data']:
        project = {}
        project_json_object = request_projects.json()
        if previous_id != project_json_object['data'][0]['id']:
            # create project json body
            print('New project found')
            json_object_unstructured = request_projects.json()
            print(project_json_object)
            if 'project_manager' in project_json_object['data'][0]:
                project_manager_simplicate_id = project_json_object['data'][0]['project_manager']['employee_id']
                request_employees = requests.get(simplicate_employees_url + project_manager_simplicate_id,
                                                 headers={
                                                     'Authentication-Key': authentication_key,
                                                     'Authentication-Secret': authentication_secret
                                                 })
                employee_json_object = request_employees.json()
                project['projectleider_email'] = employee_json_object['data'][0]['work_email']
            else:
                project['projectleider_email'] = None

            previous_id = project_json_object['data'][0]['id']
            project["bedrijf"] = project_json_object['data'][0]['organization']['name']
            project['projectnaam'] = project_json_object['data'][0]['name']
            project['uurtarief'] = project_json_object['data'][0]['hours_rate_type']
            project['projectnummer'] = project_json_object['data'][0]['project_number']
            project['simplicate_url'] = project_json_object['data'][0]['simplicate_url']
            headers = {
                'Content-Type': 'application/json',
            }
            requests.post('https://prod-02.westeurope.logic.azure.com:443/workflows/67b2bc14f94d4670a1fa4fcb219b60cd/triggers/manual/paths/invoke?api-version=2016-06-01&sp=%2Ftriggers%2Fmanual%2Frun&sv=1.0&sig=WHSw8AQHKxUow9hlVhXjsbrg9TgMtjEYKa5iDHufzRg',
                          data=json.dumps(project),
                          headers=headers)
            print('Project sent to Microsoft Flow to handle the event')

    sleep(10)


