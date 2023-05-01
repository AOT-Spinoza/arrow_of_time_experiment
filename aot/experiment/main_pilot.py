import os.path as op
import argparse
from psychopy import logging
import yaml
from session import HCPMovieELSession
from pathlib import Path
import aot

base_dir = Path(aot.__path__[0])
core_expt_yaml_path = base_dir / "experiment/core_exp_settings.yml"
core_settings = yaml.load(open(core_expt_yaml_path), Loader=yaml.FullLoader)

parser = argparse.ArgumentParser()
parser.add_argument("--task", default=90, nargs="?")
parser.add_argument("--run", default=1, nargs="?")
parser.add_argument("--eyelink", default=True,
                    action=argparse.BooleanOptionalAction)

cmd_args = parser.parse_args()
task, run, eyelink = (
    cmd_args.task,
    cmd_args.run,
    cmd_args.eyelink,
)


def main():
    settings_dir = base_dir / core_settings["paths"]["settings_path"] / "pilot"
    output_dir = base_dir / core_settings["paths"]["output_path"] / "pilot"
    output_str = f"task-{str(task).zfill(2)}_run-{str(run).zfill(2)}_task-movie"
    runs_input_yaml = settings_dir / \
        f"experiment_settings_task_{str(task).zfill(2)}_run_{str(run).zfill(2)}.yml"

    session_object = HCPMovieELSession(
        output_str=output_str,
        output_dir=output_dir,
        core_settings_file=core_expt_yaml_path,
        run_settings_file=runs_input_yaml,
        eyetracker_on=eyelink,
    )
    session_object.create_trials()
    logging.warn(f"Writing results to: {output_dir / output_str}")
    session_object.run()
    session_object.close()


if __name__ == "__main__":
    main()
