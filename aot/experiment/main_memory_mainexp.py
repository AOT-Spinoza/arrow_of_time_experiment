import os.path as op
import argparse
from psychopy import logging
import yaml
from session import HCPMovieELSessionMemory
from pathlib import Path
import aot

base_dir = Path(aot.__path__[0])
core_expt_yaml_path = base_dir / "experiment/core_exp_settings.yml"
core_settings = yaml.load(open(core_expt_yaml_path), Loader=yaml.FullLoader)

parser = argparse.ArgumentParser()
parser.add_argument("--subject", default=1, nargs="?")
parser.add_argument("--ses", default=8, nargs="?")
parser.add_argument("--run", default=1, nargs="?")

parser.add_argument("--eyelink", default=True,
                    action=argparse.BooleanOptionalAction)

cmd_args = parser.parse_args()
subject, ses, run, eyelink = (
    cmd_args.subject,
    cmd_args.ses,
    cmd_args.run,
    cmd_args.eyelink,
)


def main():
    settings_dir = base_dir / \
        core_settings["paths"]["settings_path"] / "memory_main"
    output_dir = base_dir / \
        core_settings["paths"]["output_path"] / "memory_main"
    output_str = f"sub-{str(subject).zfill(2)}_ses-{str(ses).zfill(2)}_run-{str(run).zfill(2)}_task-memory"
    runs_input_yaml = settings_dir / \
        f"experiment_settings_sub_{str(subject).zfill(2)}_ses_{str(ses).zfill(2)}_run_{str(run).zfill(2)}.yml"

    session_object = HCPMovieELSessionMemory(
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
