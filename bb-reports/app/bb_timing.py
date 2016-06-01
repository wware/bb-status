#!/usr/bin/env python

from time import localtime, asctime
from datetime import timedelta
from subprocess import Popen, PIPE
import re


from bb_report_models import Buildrequests, Buildsets, BuildsetProperties, Builds


class BuildRecord(object):
    '''
    Serves as a representation of a complete build, which is actually
    comprised of several builds of various types (from buildbot's perspective).
    '''

    def __init__(self, buildsetid):
        self.buildsetid = buildsetid
        self.submitted_at = 0
        self.complete_at = 0
        self.buildername = None
        self.number = -1
        self.owner = None
        self.list_name = None
        self.baseline_enginehost_revision = 0
        self.candidate_enginehost_revision = 0
        self.baseline_saf_revision = 0
        self.candidate_saf_revision = 0
        self.baseline_env_revision = 0
        self.candidate_env_revision = 0
        self.results = None


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

def copy_br(br):
    newbr = BuildRecord(0)
    newbr.submitted_at = br.submitted_at
    newbr.complete_at = br.complete_at
    newbr.results = br.results
    newbr.buildername = br.buildername
    newbr.number = br.number
    newbr.owner = br.owner
    newbr.list_name = br.list_name
    newbr.baseline_enginehost_revision = br.baseline_enginehost_revision 
    newbr.candidate_enginehost_revision = br.candidate_enginehost_revision
    newbr.baseline_saf_revision = br.baseline_saf_revision
    newbr.candidate_saf_revision = br.candidate_saf_revision
    newbr.baseline_env_revision = br.baseline_env_revision
    newbr.candidate_env_revision = br.candidate_env_revision

    return newbr

def get_property(raw_prop):
    '''
    Extract the real value from the weird string that looks like a list that
    buildbot uses.
    '''

    prop = None
    try:
        prop = eval(raw_prop)[0]
    except IndexError:
        pass
    except NameError:
        prop = 0

    return prop

def timing_report():
    '''
    This is the main code.
    '''

    #build_host = 'amber-buildbot-2.veracode.local'    # Test stack
    #build_host = 'jade-buildbot-1.veracode.local'    # Production
    build_host = 'amber-buildbot-3.veracode.local'    # Test stack

    # Static vars
    result_codes = ['Success', 'Warnings', 'Failure', 'Skipped', 'Exception',
                    'Retry', 'Cancelled']
    
    # Main query, which works backwards from the build properties of the Test Worker
    # builders, as they are the font of all build info.
    q = BuildsetProperties.query\
        .join(Buildsets, Buildsets.id == BuildsetProperties.buildsetid)\
        .join(Buildrequests, Buildrequests.buildsetid == Buildsets.id)\
        .join(Builds, Builds.brid == Buildrequests.id)\
        .add_columns(Buildrequests.buildsetid,
                     Buildrequests.submitted_at,
                     Buildrequests.complete_at,
                     Buildrequests.buildername,
                     Builds.number,
                     BuildsetProperties.property_name,
                     BuildsetProperties.property_value,
                     Buildsets.results,)\
        .filter(
                ((BuildsetProperties.property_name == 'test_list_file_name') |
                 (BuildsetProperties.property_name == 'owner') |
                 (BuildsetProperties.property_name == 'test_buildername') |
                 (BuildsetProperties.property_name == 'test_buildnumber') |
                 (BuildsetProperties.property_name == 'baseline_enginehost_revision') |
                 (BuildsetProperties.property_name == 'candidate_enginehost_revision') |
                 (BuildsetProperties.property_name == 'baseline_saf_revision') |
                 (BuildsetProperties.property_name == 'candidate_saf_revision') |
                 (BuildsetProperties.property_name == 'baseline_env_revision') |
                 (BuildsetProperties.property_name == 'candidate_env_revision')) &
                 (Buildrequests.buildername == 'Test Worker')
               )\
        .order_by(Buildrequests.buildsetid.desc())\
        .limit(400)\
        .all()

    # Create an array of builds.
    row_limit = 50
    run_data = []
    count = 0
    current_br = 0
    br = []
    current_buildsetid = None
    first = True

    # Loop thru rows from the query.
    for row in q:

        # Got a new buildset. Wrap-up current one.
        if row.buildsetid != current_buildsetid and not first:
            br.append(BuildRecord(row.buildsetid))
            current_br += 1
            current_buildsetid = row.buildsetid

        # Keep accumulating BuildRecord data.
        else:
            if first:
                current_buildsetid = row.buildsetid
                br.append(BuildRecord(row.buildsetid))
                first = False

        # Capture individual build properties.
        if row.property_name == 'test_list_file_name':
            br[current_br].list_name = get_property(row.property_value)
        elif row.property_name == 'owner':
            br[current_br].owner = get_property(row.property_value)
        elif row.property_name == 'baseline_enginehost_revision':
            br[current_br].baseline_enginehost_revision = get_property(row.property_value)
        elif row.property_name == 'candidate_enginehost_revision':
            br[current_br].candidate_enginehost_revision = get_property(row.property_value)
        elif row.property_name == 'baseline_saf_revision':
            br[current_br].baseline_saf_revision = get_property(row.property_value)
        elif row.property_name == 'candidate_saf_revision':
            br[current_br].candidate_saf_revision = get_property(row.property_value)
        elif row.property_name == 'baseline_env_revision':
            br[current_br].baseline_saf_revision = get_property(row.property_value)
        elif row.property_name == 'candidate_env_revision':
            br[current_br].candidate_saf_revision = get_property(row.property_value)
        elif row.property_name == 'test_buildername':
            br[current_br].buildername = get_property(row.property_value)
            br[current_br].submitted_at = row.submitted_at
            br[current_br].complete_at = row.complete_at
            br[current_br].results = 'Unknown'
            try:
                br[current_br].results = result_codes[row.results]
            except:
                pass
        elif row.property_name == 'test_buildnumber':
            br[current_br].number = get_property(row.property_value)

    # Process the BuildRecords we created.
    current_number = None
    current_buildername = None
    first = True
    row_count = 1
    for b in br:
        # Check for chunked build.
        if b.number == current_number and b.buildername == current_buildername:
            # Same build number and builder, so just contatentate the list names.
            newbr.list_name = ', '.join([newbr.list_name, b.list_name])
        else:
            if first:
                current_number = b.number
                current_buildername = b.buildername
                first = False
                newbr = copy_br(b)
                continue

            # Our limit
            row_count += 1
            if row_count > row_limit:
                break

            # Format human-readable dates.
            submitted = ''
            if newbr.submitted_at:
                submitted = asctime(localtime(newbr.submitted_at))
            complete = ''
            if newbr.complete_at:
                complete = asctime(localtime(newbr.complete_at))
            elapsed = ''
            if newbr.submitted_at > 0 and newbr.complete_at > 0:
                elapsed = timedelta(seconds=newbr.complete_at - newbr.submitted_at)
            if complete == '':
                newbr.results = 'Running'

            # Create comparison report URL.
            comp_report = '(N/A)'
            if newbr.complete_at > 0:
                comp_report = 'http://{0}:8080/reports/{1}/{2}/'\
                              .format(build_host, newbr.buildername, newbr.number)

            # More friendy display.
            if newbr.owner == None:
                chkrev = 0
                if newbr.baseline_saf_revision != newbr.candidate_saf_revision:
                    chkrev = newbr.candidate_saf_revision
                elif newbr.baseline_enginehost_revision != candidate_enginehost_revision:
                    chkrev = newbr.candidate_enginehost_revision
                elif newbr.baseline_env_revision != newbr.candidate_env_revision:
                    chkrev = newbr.candidate_env_revision
                if chkrev:
                    newbr.owner = get_change_owner(chkrev)
                else:
                    newbr.owner = '(Unknown)'
            else:
                re.search('(\w+)@veracode.com', newbr.owner)
                if m:
                    owner = m.group(1)

            # Build report table row.
            rpt = {'build_num': newbr.number,
                   'buildername': newbr.buildername,
                   'list_name': newbr.list_name,
                   'owner': newbr.owner,
                   'submitted': submitted,
                   'completed': complete,
                   'results': newbr.results,
                   'elapsed': elapsed,
                   'comp_report': comp_report,}
            run_data.append(rpt)

            # Create next record.
            newbr = copy_br(b)
            current_number = b.number
            current_buildername = b.buildername

    return run_data

if __name__ == '__main__':
    result = timing_report()
    print result


