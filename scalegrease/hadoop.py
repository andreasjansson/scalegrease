import logging
import subprocess

from scalegrease import system
from scalegrease import runner


class HadoopRunner(runner.RunnerBase):
    def is_recognised(self, jar_path):
        try:
            jar_listing = system.check_output(["jar", "tf", jar_path])
            return "org/apache/crunch/Pipeline.class" in jar_listing.splitlines()
        except subprocess.CalledProcessError:
            return False

    def run_job(self, jar_path):
        hadoop_cmd = self._config["command"] + [jar_path]
        logging.info("Executing: %s", " ".join(hadoop_cmd))
        subprocess.check_call(hadoop_cmd)
