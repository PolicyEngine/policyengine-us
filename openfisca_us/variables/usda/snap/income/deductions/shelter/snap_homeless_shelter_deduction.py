from openfisca_us.model_api import *


class snap_homeless_shelter_deduction(Variable):
    value_type = float
    entity = SPMUnit
    definition_period = YEAR
    label = "Homeless shelter deduction"
    documentation = "Homeless shelter deduction"
    reference = (
        "https://www.law.cornell.edu/cfr/text/7/273.9#d_6_i",
        "United States Code, Title 7, Section 2014(e)(6)(D)",
    )
    unit = USD

    def formula(spm_unit, period, parameters):
        is_homeless = spm_unit.household("is_homeless", period)
        deduction = parameters(period).usda.snap.homeless_shelter_deduction
        return (is_homeless * deduction) * 12
