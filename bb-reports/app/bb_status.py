import requests
from subprocess import Popen, PIPE
import re


sshpass = '/usr/bin/sshpass'
saf_cmd = "svn log -r {0} svn+ssh://enguser@skunkworks/usr/rep/svn/saf"
pass_cmd = "sudo {0} -p ".format(sshpass)
pass_cmd += '{0}'

def get_change_owner(rev):
    my_saf_cmd = saf_cmd.format(rev)
    my_pass_cmd = pass_cmd.format(r"optimus\'2")
    cmd = '{0} {1}'.format(my_pass_cmd, my_saf_cmd)
    proc = Popen(cmd, stdin=PIPE, stdout=PIPE, stderr=PIPE, shell=True)
    o, e = proc.communicate()
    result = None
    try:
        if len(o) > 0:
            result = o.split('|')[1].strip()
    except Exception as e:
        pass

    return result

def sorted_humanly(src_list):
    convert = lambda text: int(text) if text.isdigit() else text
    alphanum_key = lambda key: [convert(c) for c in re.split('([0-9]+)', key)]

    return sorted(src_list, key=alphanum_key)

def get_property(property_list, property_name):
    value = None
    for prop in property_list:
        if prop[0] == property_name:
            value = prop[1]
            break

    return value

def status_report():
    #host = 'amber-buildbot-2.veracode.local'
    #host = 'jade-buildbot-1.veracode.local'
    host = 'amber-buildbot-3.veracode.local'
    port = 8080
    api = 'json'
    url_base = 'http://{0}:{1}/{2}'.format(host, port, api)

    r = requests.get(url_base)
    data = r.json()
    
    status_data = []
    workers = sorted_humanly(data['slaves'].keys())
    for worker in workers:
        connected = data['slaves'][worker]['connected']
        if connected:
            connected = 'connected'
        else:
            connected = 'not connected'
        builds = len(data['slaves'][worker]['runningBuilds'])
        if builds < 1:
            row = {'worker': worker,
                   'connected': connected,
                   'step': 'Idle',
                   'owner': '',
                   'buildername': '',
                   'enginehost_branch': '',
                   'env_branch': '',
                   'saf_branch': '',
                  }
            status_data.append(row)
            continue

        # Loop thru builds (can have multiple builds per worker).
        previous_worker = ''
        for build in range(builds):
            build_num = data['slaves'][worker]['runningBuilds'][build]['number']
            list_step_name = data['slaves'][worker]['runningBuilds'][build]['currentStep']['text']
            step_name = ' '.join(list_step_name)
            step_num = data['slaves'][worker]['runningBuilds'][build]['currentStep']['step_number']
            owner = data['slaves'][worker]['runningBuilds'][build]['blame']
            if isinstance(owner, list):
                try:
                    owner = owner[0]
                except IndexError:
                    owner = ''

            props = data['slaves'][worker]['runningBuilds'][build]['properties']
            buildername = get_property(props, 'buildername')
            candidate_enginehost_branch = get_property(props, 'candidate_enginehost_branch')
            candidate_enginehost_revision = get_property(props, 'candidate_enginehost_revision')
            candidate_env_branch = get_property(props, 'candidate_env_branch')
            candidate_env_revision = get_property(props, 'candidate_env_revision')
            candidate_saf_branch = get_property(props, 'candidate_saf_branch')
            candidate_saf_revision = get_property(props, 'candidate_saf_revision')
            baseline_enginehost_revision = get_property(props, 'baseline_enginehost_revision')
            baseline_env_revision = get_property(props, 'baseline_env_revision')
            baseline_saf_revision = get_property(props, 'baseline_saf_revision')

            # Get owner from svn if necessary.
            if not owner:
                if candidate_saf_revision != baseline_saf_revision:
                    owner = get_change_owner(candidate_saf_revision)
                if candidate_enginehost_revision != baseline_enginehost_revision:
                    owner = get_change_owner(candidate_enginehost_revision)
                if candidate_env_revision != baseline_env_revision:
                    owner = get_change_owner(candidate_env_revision)

            display_worker = worker
            display_connected = connected
            if worker == previous_worker:
                display_worker = ''
                display_connected = ''
            previous_worker = worker
            # Build a row for display.
            row = {'worker': display_worker,
                   'connected': display_connected,
                   'build_num': build_num,
                   'step': '{0} (Step {1})'.format(step_name, step_num),
                   'owner': owner,
                   'buildername': buildername,
                   'enginehost_branch': '{0}@{1}'.format(candidate_enginehost_branch, candidate_enginehost_revision),
                   'env_branch': '{0}@{1}'.format(candidate_env_branch, candidate_env_revision),
                   'saf_branch': '{0}@{1}'.format(candidate_saf_branch, candidate_saf_revision),}
            status_data.append(row)

    return status_data

if __name__ == '__main__':
    status_report()
