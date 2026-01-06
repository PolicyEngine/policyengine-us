from policyengine_us.model_api import *


class la_fitap(Variable):
    value_type = float
    entity = SPMUnit
    label = "Louisiana FITAP"
    unit = USD
    definition_period = MONTH
    reference = "https://ldh.la.gov/page/fitap"
    defined_for = "la_fitap_eligible"

    def formula(spm_unit, period, parameters):
        p = parameters(period).gov.states.la.dcfs.fitap.benefit
        flat_grant = spm_unit("la_fitap_flat_grant", period)
        countable_income = spm_unit("la_fitap_countable_income", period)

        # Benefit = flat grant minus countable income
        benefit = max_(flat_grant - countable_income, 0)

        # Benefits below minimum are not issued
        return where(benefit >= p.minimum, benefit, 0)
