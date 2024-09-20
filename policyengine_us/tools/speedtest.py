import timeit
import yaml


def import_pe():
    from policyengine_us import Microsimulation


def run_pe():
    from policyengine_us import Microsimulation

    Microsimulation().calculate("household_net_income")


COUNT_RUNS = 3
time_to_import = timeit.timeit(import_pe, number=COUNT_RUNS) / COUNT_RUNS
time_to_run = (
    timeit.timeit(run_pe, number=COUNT_RUNS) / COUNT_RUNS - time_to_import
)

with open("speedtest.yaml", "w") as f:
    f.write(yaml.dump({"import": time_to_import, "run": time_to_run}))
