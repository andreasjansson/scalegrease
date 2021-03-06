import os
import shutil
import tempfile
import zipfile

from scalegrease import system
from scalegrease.runner import RunnerBase


class PythonRunner(RunnerBase):
    def run_job(self, artifact_storage, argv):
        tmp_dir = tempfile.mkdtemp()
        try:
            self._extract_python_resources(artifact_storage.jar_path(), tmp_dir)
            self._run_python_task(artifact_storage, argv, tmp_dir)
        finally:
            shutil.rmtree(tmp_dir)

    def _extract_python_resources(self, jar_path, tmp_dir):
        jar_file = zipfile.ZipFile(jar_path, "r")
        for info in jar_file.infolist():
            resource_path = info.filename

            if resource_path.startswith("python/"):
                jar_file.extract(info, tmp_dir)

    def _run_python_task(self, artifact, cmd_args, tmp_dir):
        sub_env = os.environ.copy()
        sub_env["PLATFORM_ARTIFACT_SPEC"] = os.path.abspath(artifact.jar_path())

        src_path = os.path.join(tmp_dir, "python")
        if "PYTHONPATH" in sub_env:
            sub_env["PYTHONPATH"] += ":" + src_path
        else:
            sub_env["PYTHONPATH"] = src_path

        cmd_line = list(cmd_args)

        cwd_backup = os.getcwd()
        os.chdir(src_path)
        try:
            system.run_with_logging(cmd_line, env=sub_env)
        finally:
            os.chdir(cwd_backup)
