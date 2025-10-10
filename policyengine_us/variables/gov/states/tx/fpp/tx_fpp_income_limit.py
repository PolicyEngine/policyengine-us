from policyengine_us.model_api import *


class tx_fpp_income_limit(Variable):
    value_type = float
    entity = SPMUnit
    label = "Texas Family Planning Program income limit"
    unit = USD
    definition_period = YEAR
    reference = (
        "https://www.healthytexaswomen.org/healthcare-programs/family-planning-program/fpp-who-can-apply",
        "https://www.hhs.texas.gov/sites/default/files/documents/texas-womens-health-programs-report-2024.pdf",
    )
    defined_for = StateCode.TX

    def formula(spm_unit, period, parameters):
        # Get household size and state group for FPG calculation
        size = spm_unit("spm_unit_size", period)
        state_group = spm_unit.household("state_group_str", period)

        # Get FPG parameters
        p_fpg = parameters(period).gov.hhs.fpg
        fpg_first = p_fpg.first_person[state_group]
        fpg_additional = p_fpg.additional_person[state_group]

        # Calculate base FPG for household size
        base_fpg = fpg_first + fpg_additional * max_(size - 1, 0)

        # Get FPP percentage (250% = 2.5)
        fpp_percentage = parameters(period).gov.states.tx.fpp.fpg_percentage

        # Return annual income limit
        return base_fpg * fpp_percentage
