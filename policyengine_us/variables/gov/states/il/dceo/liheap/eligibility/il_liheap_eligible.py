from policyengine_us.model_api import *


class il_liheap_eligible(Variable):
    value_type = bool
    entity = SPMUnit
    label = "Eligible for Illinois LIHEAP"
    definition_period = YEAR
    defined_for = "il_liheap_income_eligible"
    reference = "https://dceo.illinois.gov/communityservices/utilitybillassistance.html"

    def formula(spm_unit, period, parameters):
        p = parameters(period).gov.states.il.dceo.liheap.eligibility

        # For renters with heat included in rent, check additional requirement
        heat_in_rent = spm_unit("heat_expense_included_in_rent", period)
        rent = add(spm_unit, period, ["rent"])
        income = add(spm_unit, period, ["irs_gross_income"])

        # If heat is included in rent, rent must exceed threshold percentage of income
        rent_threshold = income * p.rent_rate
        rent_threshold_met = rent > rent_threshold

        return ~heat_in_rent | rent_threshold_met
