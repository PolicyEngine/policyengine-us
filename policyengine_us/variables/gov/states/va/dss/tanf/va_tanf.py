from policyengine_us.model_api import *


class va_tanf(Variable):
    value_type = float
    entity = SPMUnit
    label = "VA TANF"
    unit = USD
    definition_period = YEAR
    defined_for = "va_tanf_eligibility"

    def formula(spm_unit, period, parameters):
        # the calculated payment
        up_tanf_eligibility = spm_unit("va_up_tanf_eligibility", period)
        grant_standard = spm_unit("va_tanf_grant_standard", period)
        up_grant_standard = spm_unit("va_tanf_up_grant_standard", period)
        grant = where(up_tanf_eligibility, up_grant_standard, grant_standard)
        countable_income = spm_unit("va_tanf_countable_income", period)
        payment = max_(grant - countable_income, 0)

        # compute the minimum and maximum payment
        p = parameters(period).gov.states.va.dss.tanf
        minimum = p.va_tanf_minimum_payment * MONTHS_IN_YEAR
        county = spm_unit.household("county_str", period)
        if_group3 = county in p.localities.group3
        maximum = (
            where(
                up_tanf_eligibility,
                where(
                    if_group3,
                    p.up_grant_standard.group3.max,
                    p.up_grant_standard.group2.max,
                ),
                where(
                    if_group3,
                    p.grant_standard.group3.max,
                    p.grant_standard.group2.max,
                ),
            )
            * MONTHS_IN_YEAR
        )

        return min_(where(payment >= minimum, payment, 0), maximum)
