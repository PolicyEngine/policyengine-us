from policyengine_us.model_api import *


class commodity_supplemental_food_program_eligible(Variable):
    value_type = bool
    entity = Person
    definition_period = YEAR
    label = "Commodity Supplemental Food Program eligible"

    def formula(person, period, parameters):
        p = parameters(period).gov.usda.csfp
        # CFR defines CSFP income similarly to WIC income.
        # Assume resources are counted at the SPM unit level.
        fpg = person.spm_unit("school_meal_fpg_ratio", period)
        age = person("age", period)

        age_eligible = age >= p.min_age
        federal_income_eligible = fpg <= p.fpg_limit
        tx_income_eligible = person("tx_dta_csfp_income_eligible", period)
        state_code = person.household("state_code", period)
        in_tx = state_code == StateCode.TX
        income_eligible = where(
            in_tx, tx_income_eligible, federal_income_eligible
        )
        return age_eligible & income_eligible
