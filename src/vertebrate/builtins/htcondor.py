"""
Implementations of ABCs that use resources available to an HTCondor pool.
"""

# Recipe for performing remote submission using the Python bindings:
# https://github.com/CHTC/recipes/tree/remote-submit-htc/workflows-htc/remote-submit

import os
import time
from typing import Any

import htcondor2 as htcondor

from vertebrate.compute import Environment


class HTCondorEnvironment(Environment):
    """
    Execute jobs on an HTCondor cluster.
    """

    # NOTE: Currently hard-coded to CHTC
    SUBMIT_REQUIREMENTS = '(TARGET.PoolName == "CHTC") && ((((Target.OpSysMajorVer == 9) && (Target.OpSysName =!= "Debian") &&  !(Target.OSPool ?: false))) || (((Target.OSPool ?: false) && ((Target.OSGVO_OS_STRING ?: "") == "RHEL 9")))) && (TARGET.Arch == "X86_64") && (TARGET.OpSys == "LINUX") && (TARGET.Disk >= RequestDisk) && (TARGET.Memory >= RequestMemory) && ((TARGET.FileSystemDomain == MY.FileSystemDomain) || (TARGET.HasFileTransfer))'

    DONE = 4

    def __init__(
        self,
        user_name: str,
        ap_name: str,
        collector_name: str,
        token_dir: str = os.path.expanduser("~/.condor/tokens.d"),
        poll_secs: float = 60.0,
        debug: bool = False,
    ) -> None:
        self.user_name = user_name
        self.ap_name = ap_name
        self.collector = htcondor.Collector(collector_name)
        self.access_point = htcondor.Schedd(
            self.collector.locate(htcondor.DaemonType.Schedd, ap_name)
        )
        self._generate_creds(token_dir)
        self.poll_secs = poll_secs
        if debug:
            htcondor.enable_debug()

    def _generate_creds(self, token_dir: str) -> None:
        htcondor.param["SEC_TOKEN_DIRECTORY"] = token_dir
        credd_ad = self.collector.locate(htcondor.DaemonType.Credd, self.ap_name)
        credd = htcondor.Credd(credd_ad)
        for service in ["rdrive", "scitokens"]:
            credd.add_user_service_cred(htcondor.CredType.OAuth, b"", service)

    def _wait_for_completion(self, submit_object):
        done = False
        while not done:
            time.sleep(self.poll_secs)
            ads = self.access_point.query(
                f"ClusterID == {submit_object.cluster()}",
                projection = ["ProcID", "JobStatus"],
            )
            done = all(i['JobStatus'] == HTCondorEnvironment.DONE for i in ads)

    def execute(self, executable: str, args: tuple = (), kwargs: dict = {}) -> Any:
        kwargs["executable"] = executable
        job = htcondor.Submit(kwargs)
        submit_object = self.access_point.submit(job, spool=True)
        self.access_point.spool(submit_object)
        self._wait_for_completion(submit_object)
        self.access_point.retrieve(f"ClusterID == {submit_object.cluster()}")
        self.access_point.edit(submit_object.cluster(), "LeaveJobInQueue", False)

    def __contains__(self, item: str) -> bool:
        return os.path.exists(item)
