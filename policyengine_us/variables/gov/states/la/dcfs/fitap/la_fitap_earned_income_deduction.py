from policyengine_us.model_api import *


class la_fitap_earned_income_deduction(Variable):
    value_type = float
    entity = Person
    label = "Louisiana FITAP earned income deduction"
    unit = USD
    definition_period = MONTH
    reference = "https://ldh.la.gov/page/fitap"
    defined_for = StateCode.LA

    def formula(person, period, parameters):
        p = parameters(period).gov.states.la.dcfs.fitap.income.deductions
        gross_earned = person("tanf_gross_earned_income", period)

        # Per FITAP rules: deductions only apply to employed members
        is_employed = gross_earned > 0

        # NOTE: The $900 time-limited deduction is only available for
        # the first 6 months of employment. PolicyEngine cannot track
        # employment duration, so we apply it assuming qualification.
        standard_deduction = p.standard
        time_limited_deduction = p.time_limited
        total_deduction = standard_deduction + time_limited_deduction

        return where(is_employed, total_deduction, 0)
