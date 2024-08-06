from policyengine_us import Microsimulation
from policyengine_core.periods import YEAR
from policyengine_us.variables.household.demographic.person.immigration_status import (
    ImmigrationStatus,
)
import numpy as np


def run_simulation():
    sim = Microsimulation()

    print("ImmigrationStatus Enum values:")
    for status in ImmigrationStatus:
        print(f"  {status.name}: {status.value}")

    CURRENT_YEAR = "2024"

    # Define our test cases
    test_cases = [
        ImmigrationStatus.LEGAL_PERMANENT_RESIDENT,
        ImmigrationStatus.REFUGEE,
        ImmigrationStatus.ASYLEE,
        ImmigrationStatus.DEPORTATION_WITHHELD,
        ImmigrationStatus.CUBAN_HAITIAN_ENTRANT,
        ImmigrationStatus.CONDITIONAL_ENTRANT,
        ImmigrationStatus.PAROLED_ONE_YEAR,
        ImmigrationStatus.UNDOCUMENTED,
    ]

    population_size = sim.calculate("age", CURRENT_YEAR).size

    # Modify a subset of the population for each test case
    immigration_statuses = np.full(
        population_size, ImmigrationStatus.CITIZEN.name, dtype=object
    )
    for i, status in enumerate(test_cases):
        start = i * 100
        end = start + 100
        immigration_statuses[start:end] = status.name
        print(f"Setting indices {start}-{end} to {status.name}")

    sim.set_input("immigration_status_str", CURRENT_YEAR, immigration_statuses)

    # Debug print
    check_immediately = sim.calculate("immigration_status_str", CURRENT_YEAR)
    print("Unique values in immigration_status_str immediately after setting:")
    print(np.unique(check_immediately))

    check_status = sim.calculate("immigration_status", CURRENT_YEAR)
    print(np.unique(check_status))

    immigration_status_values = sim.calculate(
        "immigration_status", CURRENT_YEAR
    )
    print("\nUnique values in immigration_status:")
    unique_values, counts = np.unique(
        immigration_status_values, return_counts=True
    )
    for value, count in zip(unique_values, counts):
        print(f"  {ImmigrationStatus(value).name}: {count}")

    print("\nChecking set immigration statuses:")
    for i, status in enumerate(test_cases):
        start = i * 100
        print(f"  Test case {i+1}:")
        print(f"    Status string at index {start}: {check_status_str[start]}")
        print(
            f"    Status enum at index {start}: {ImmigrationStatus(check_status[start]).name}"
        )

    # Add this section to print out all unique values
    print("\nUnique values in immigration_status_str:")
    unique_values = np.unique(check_status_str)
    for value in unique_values:
        print(f"  {value}")

    print("\nUnique values in immigration_status:")
    unique_values = np.unique(check_status)
    for value in unique_values:
        print(f"  {value}")

    # Print out the ImmigrationStatus Enum for reference
    print("\nValid ImmigrationStatus values:")
    for status in ImmigrationStatus:
        print(f"  {status.name}: {status.value}")

    # Set all individuals as aged, blind, or disabled for this test
    sim.set_input(
        "is_ssi_aged_blind_disabled",
        CURRENT_YEAR,
        np.ones(population_size, dtype=bool),
    )

    # Calculate results
    results = {}
    for variable in [
        "immigration_status",
        "is_ssi_qualified_noncitizen",
        "is_ssi_eligible_individual",
        "is_ssi_aged_blind_disabled",
        "is_ssi_eligible_spouse",
        "ssi_amount_if_eligible",
        "ssi_countable_income",
        "meets_ssi_resource_test",
        "uncapped_ssi",
    ]:
        results[variable] = sim.calculate(variable, CURRENT_YEAR)

    # Print results for our test cases
    for i, status in enumerate(test_cases):
        start = i * 100
        print(f"Test case {i+1}:")

        immigration_status = results["immigration_status"][start]
        print(f"  Immigration Status: {immigration_status}")
        print(
            f"  Qualified Noncitizen: {results['is_ssi_qualified_noncitizen'][start]}"
        )
        print(
            f"  Aged/Blind/Disabled: {results['is_ssi_aged_blind_disabled'][start]}"
        )
        print(
            f"  SSI Eligible Spouse: {results['is_ssi_eligible_spouse'][start]}"
        )
        print(
            f"  SSI Eligible Individual: {results['is_ssi_eligible_individual'][start]}"
        )
        print(
            f"  Meets Resource Test: {results['meets_ssi_resource_test'][start]}"
        )
        print(
            f"  SSI Amount If Eligible: ${results['ssi_amount_if_eligible'][start]:.2f}"
        )
        print(
            f"  SSI Countable Income: ${results['ssi_countable_income'][start]:.2f}"
        )
        print(f"  Uncapped SSI: ${results['uncapped_ssi'][start]:.2f}")
        print()


if __name__ == "__main__":
    run_simulation()
