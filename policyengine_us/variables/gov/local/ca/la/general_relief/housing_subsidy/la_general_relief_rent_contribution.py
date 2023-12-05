from policyengine_us.model_api import *


class la_general_relief_rent_contribution(Variable):
    value_type = float
    entity = SPMUnit
    unit = USD
    label = "Los Angeles County General Relief rent contribution"
    definition_period = MONTH
    defined_for = "la_general_relief_eligible"
    reference = "https://drive.google.com/file/d/1Oc7UuRFxJj-eDwTeox92PtmRVGnG9RjW/view?usp=sharing"

    def formula(spm_unit, period, parameters):
        married = add(spm_unit, period, ["is_married"])
        p = parameters(period).gov.local.ca.la.general_relief
        # If filers are receiving the housing subsidy
        # they are obligate to commit an amount of their GR towards rent
        # which is deducted here and added to the housing subsidy amount
        receive_housing_subsidy = (
            spm_unit("la_general_relief_housing_subsidy", period) > 0
        )
        rent_contributions = where(
            married,
            p.housing_subsidy.rent_contribution.married,
            p.housing_subsidy.rent_contribution.single,
        )

        return where(receive_housing_subsidy, rent_contributions, 0)
