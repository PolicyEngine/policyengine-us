from policyengine_us.model_api import *


class pa_ccw_income_eligible(Variable):
    value_type = bool
    entity = SPMUnit
    label = "Eligible for Pennsylvania CCW based on income"
    definition_period = MONTH
    defined_for = StateCode.PA
    reference = "https://www.pacodeandbulletin.gov/secure/pacode/data/055/chapter3042/055_3042.pdf#page=14"

    def formula(spm_unit, period, parameters):
        p = parameters(period).gov.states.pa.dhs.ccw.eligibility
        adjusted_income = spm_unit("pa_ccw_adjusted_income", period.this_year)
        fpg = spm_unit("spm_unit_fpg", period.this_year)
        smi = spm_unit("hhs_smi", period.this_year)
        enrolled = spm_unit("pa_ccw_enrolled", period)
        initial_limit = fpg * p.initial_income_limit
        # Between redeterminations, enrolled families use 85% SMI only.
        # The 235% FPIG cap applies at redetermination (55 Pa. Code 3042.31).
        continuous_limit = smi * p.continuous_smi_limit
        income_limit = where(enrolled, continuous_limit, initial_limit)
        return adjusted_income <= income_limit
