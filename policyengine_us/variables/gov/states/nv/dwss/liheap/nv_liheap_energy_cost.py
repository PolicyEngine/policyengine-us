from policyengine_us.model_api import *


class nv_liheap_energy_cost(Variable):
    value_type = float
    entity = SPMUnit
    definition_period = YEAR
    unit = USD
    label = "Nevada LIHEAP energy cost"
    documentation = (
        "Annual primary heating and electric energy costs used for the Fixed "
        "Annual Credit."
    )
    defined_for = StateCode.NV
    reference = (
        "https://www.leg.state.nv.us/nrs/nrs-702.html#NRS702Sec260",
        "https://dss.nv.gov/uploadedFiles/dwssnvgov/content/Energy/FY%202026%20EAP%20Manual%2008.2025%20ADA.pdf#page=60",
        "https://www.dss.nv.gov/contentassets/b3bcdb93ea2d4b3f8dc252451a34cbe4/2027-eap-state-manual--08.25.26-1.pdf#page=60",
    )

    def formula(spm_unit, period, parameters):
        # Annual bills stand in for the prior 12 months of vendor energy
        # dollar usage. The primary heating bill and the electricity bill are
        # included; heating_expense already reads the electricity bill when
        # the home heats with electricity or solar, so it is not added again.
        heating_type = spm_unit("heating_type", period)
        types = heating_type.possible_values
        electric_heat = (heating_type == types.ELECTRICITY) | (
            heating_type == types.SOLAR
        )
        heating = spm_unit("heating_expense", period)
        electricity = spm_unit("pre_subsidy_electricity_expense", period)
        return heating + where(electric_heat, 0, electricity)
