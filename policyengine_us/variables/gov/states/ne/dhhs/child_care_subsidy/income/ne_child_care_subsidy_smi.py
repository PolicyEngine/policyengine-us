from policyengine_us.model_api import *
from policyengine_us.variables.gov.hhs.hhs_smi import smi


class ne_child_care_subsidy_smi(Variable):
    value_type = float
    entity = SPMUnit
    unit = USD
    definition_period = MONTH
    label = "Nebraska Child Care Subsidy monthly state median income"
    defined_for = StateCode.NE
    reference = (
        "https://dhhs.ne.gov/Guidance%20Docs/Title%20392%20-%20Child%20Care%20Subsidy.pdf#page=6",
        "https://nebraskalegislature.gov/laws/statutes.php?statute=68-1206",
    )

    def formula(spm_unit, period, parameters):
        # Nebraska publishes updated subsidy standards each October,
        # matching the federal fiscal-year State Median Income tables.
        # Months before October therefore continue to use the prior
        # year's SMI, mirroring the poverty-guideline vintage.
        size = spm_unit("spm_unit_size", period.this_year)
        state = spm_unit.household("state_code_str", period.this_year)
        year = period.start.year
        if period.start.month >= 10:
            instant_str = f"{year}-10-01"
        else:
            instant_str = f"{year - 1}-10-01"
        return smi(size, state, instant_str, parameters) / MONTHS_IN_YEAR
