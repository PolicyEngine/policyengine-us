"""Time repeated single-household simulations of the shipped policy.

Run the same file against two checkouts to compare them:

    uv run --locked python scripts/benchmark_household_simulation.py

Each iteration constructs one ``Simulation`` from an identical situation and
calculates ``household_net_income``, which is what a household API request
does. The situation carries a county so the run is identical on revisions that
require an explicit SPM area and on revisions that ignore county entirely.
"""

import argparse
import json
import time


YEAR = 2024
COUNTY = "06037"


def situation(earnings):
    return {
        "people": {
            "you": {
                "age": {YEAR: 40},
                "employment_income": {YEAR: earnings},
            },
            "spouse": {"age": {YEAR: 38}},
            "child": {"age": {YEAR: 6}},
        },
        "families": {"family": {"members": ["you", "spouse", "child"]}},
        "marital_units": {"marital_unit": {"members": ["you", "spouse"]}},
        "tax_units": {"tax_unit": {"members": ["you", "spouse", "child"]}},
        "spm_units": {"spm_unit": {"members": ["you", "spouse", "child"]}},
        "households": {
            "household": {
                "members": ["you", "spouse", "child"],
                "state_code": {YEAR: "CA"},
                "county_fips": {YEAR: COUNTY},
            }
        },
    }


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--iterations", type=int, default=20)
    arguments = parser.parse_args()

    import_start = time.perf_counter()
    from policyengine_us import Simulation

    import_seconds = time.perf_counter() - import_start

    iterations = []
    results = []
    for index in range(arguments.iterations):
        # Vary earnings so no iteration can reuse another's cached result.
        start = time.perf_counter()
        simulation = Simulation(situation=situation(50_000 + 1_000 * index))
        constructed = time.perf_counter()
        net_income = float(simulation.calculate("household_net_income", YEAR)[0])
        done = time.perf_counter()
        iterations.append(
            {
                "construct_seconds": constructed - start,
                "calculate_seconds": done - constructed,
                "total_seconds": done - start,
            }
        )
        results.append(net_income)

    totals = [iteration["total_seconds"] for iteration in iterations]
    print(
        json.dumps(
            {
                "iterations": len(iterations),
                "import_seconds": round(import_seconds, 3),
                "first_iteration_seconds": round(totals[0], 3),
                "remaining_mean_seconds": round(
                    sum(totals[1:]) / max(len(totals) - 1, 1), 3
                ),
                "total_seconds": round(sum(totals), 3),
                "construct_total_seconds": round(
                    sum(i["construct_seconds"] for i in iterations), 3
                ),
                "calculate_total_seconds": round(
                    sum(i["calculate_seconds"] for i in iterations), 3
                ),
                "net_income_first": results[0],
                "net_income_last": results[-1],
                "per_iteration_seconds": [round(total, 3) for total in totals],
            },
            indent=2,
        )
    )


if __name__ == "__main__":
    main()
