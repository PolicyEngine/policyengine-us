from policyengine_us.model_api import *


class va_tanf(Variable):
    value_type = float
    entity = SPMUnit
    label = "VA TANF"
    unit = USD
    definition_period = MONTH
    defined_for = "va_tanf_eligibility"
    reference = "https://www.dss.virginia.gov/files/division/bp/tanf/manual/300_11-20.pdf#page=47"

    def formula(spm_unit, period, parameters):
        # the calculated payment
        up_tanf_eligibility = spm_unit("va_up_tanf_eligibility", period)
        grant_standard = spm_unit("va_tanf_grant_standard", period)
        up_grant_standard = spm_unit("va_tanf_up_grant_standard", period)
        grant = where(up_tanf_eligibility, up_grant_standard, grant_standard)
        countable_income = spm_unit("va_tanf_countable_income", period)
        payment = max_(grant - countable_income, 0)

        # compute the maximum payment
        p = parameters(period).gov.states.va.dss.tanf
        # Access July 2020 base values
        p_payment = parameters.gov.states.va.dss.tanf.payment(f"2020-10-01")
        county = spm_unit.household("county_str", period)
        if_group3 = np.isin(county, p.localities.group3)
        up_tanf_base_max = where(
            if_group3,
            p_payment.up_grant_standard.group3.max,
            p_payment.up_grant_standard.group2.max,
        )
        tanf_base_max = where(
            if_group3,
            p_payment.grant_standard.group3.max,
            p_payment.grant_standard.group2.max,
        )
        base_max = where(
            up_tanf_eligibility,
            up_tanf_base_max,
            tanf_base_max,
        )
        maximum = np.ceil(base_max * p.standard_multiplier)

        return min_(payment, maximum)
