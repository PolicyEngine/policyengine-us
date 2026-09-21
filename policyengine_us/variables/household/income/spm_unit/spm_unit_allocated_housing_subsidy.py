from policyengine_us.model_api import *


class spm_unit_allocated_housing_subsidy(Variable):
    value_type = float
    entity = SPMUnit
    label = "Housing subsidy allocated to the SPM unit before its resource cap"
    definition_period = YEAR
    unit = USD
    reference = "https://www2.census.gov/programs-surveys/supplemental-poverty-measure/datasets/spm/spm_techdoc.pdf#page=14"

    def formula(spm_unit, period, parameters):
        # Census prorates the household subsidy by each SPM unit's member
        # share. This allocation is a measurement step; it does not move the
        # underlying program award or change another family's eligibility.
        simulation = spm_unit.simulation
        household_subsidy = simulation.calculate(
            "housing_assistance", period, map_to="household"
        )
        return simulation.map_result(household_subsidy, "household", "spm_unit")
