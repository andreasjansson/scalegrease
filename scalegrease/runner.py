import abc
import argparse
import logging
import shutil
import sys
import tempfile
import json

from scalegrease import deploy
from scalegrease import error
from scalegrease import system


class RunnerBase(object):
    __metaclass__ = abc.ABCMeta

    def __init__(self, config):
        self._config = config

    @abc.abstractmethod
    def is_recognised(self, jar_path):
        raise NotImplementedError()

    @abc.abstractmethod
    def run_job(self, jar_path):
        raise NotImplementedError()


class ShellRunner(RunnerBase):
    def is_recognised(self, jar_path):
        pass

    def run_job(self, jar_path):
        pass


def find_runner(jar_path, config):
    names = config['runners']
    runners = []
    for rn in names:
        clazz = system.load_class(rn)
        class_config = config.get(clazz.__name__)
        runners.append(clazz(class_config))
    for r in runners:
        if r.is_recognised(jar_path):
            return r


def run(artifact_spec, config):
    artifact = deploy.Artifact(artifact_spec)
    tmp_dir = tempfile.mkdtemp(prefix="greaserun")
    jar_path = deploy.mvn_download(artifact, tmp_dir)
    runner = find_runner(jar_path, config)
    if runner is None:
        raise error.Error("Failed to find a runner for %s" % artifact_spec)
    runner.run_job(jar_path)
    shutil.rmtree(tmp_dir)


def main(argv):
    parser = argparse.ArgumentParser()
    parser.add_argument("--config-file", "-c", default="/etc/scalegrease.json",
                        help="Read configuration from CONFIG_FILE")
    parser.add_argument("--verbose", "-v", action="store_true",
                        help="Increase debug verbosity")
    parser.add_argument(
        "artifact",
        help="Specify Maven artifact to download and run, either on format "
             "group_id:artifact_id:version or group_id:artifact_id for latest version.")
    args = parser.parse_args(argv[1:])

    logging.basicConfig(level=logging.DEBUG if args.verbose else logging.INFO)
    logging.info("Reading configuration from %s", args.config_file)
    conf_file = open(args.config_file)
    conf = json.load(conf_file)
    logging.debug("Configuration read:\n%s", conf)

    try:
        run(args.artifact, conf)
    except error.Error as e:
        logging.error("Job failed: %s", e)
        return 1


if __name__ == '__main__':
    sys.exit(main(sys.argv))
