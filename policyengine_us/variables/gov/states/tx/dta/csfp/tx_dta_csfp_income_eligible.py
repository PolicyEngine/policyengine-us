from policyengine_us.model_api import *


class tx_dta_csfp_income_eligible(Variable):
    value_type = bool
    entity = Person
    definition_period = YEAR
    label = "Texas Commodity Supplemental Food Program income eligible"
    defined_for = StateCode.TX

    def formula(person, period, parameters):
        p = parameters(period).gov.states.tx.dta.csfp
        fpg = person.spm_unit("school_meal_fpg_ratio", period)
        return fpg <= p.fpg_limit
