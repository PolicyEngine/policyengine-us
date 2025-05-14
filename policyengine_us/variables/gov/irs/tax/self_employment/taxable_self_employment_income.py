from policyengine_us.model_api import *


class taxable_self_employment_income(Variable):
    value_type = float
    entity = Person
    label = "Taxable self-employment income"
    definition_period = YEAR
    unit = USD
    reference = "https://www.law.cornell.edu/uscode/text/26/1402#a"

    def formula(person, period, parameters):
        SEI_SOURCES = [
            "self_employment_income",
            "farm_income",
            "s_corp_self_employment_income",
        ]
        gross_sei = add(person, period, SEI_SOURCES)
        p = parameters(period).gov.irs
        combined_rate = (
            p.self_employment.rate.social_security
            + p.self_employment.rate.medicare
        )
        deduction_rate = p.ald.misc.employer_share * combined_rate
        net_sei = gross_sei * (1 - deduction_rate)
        # exclude net self-employment income below the reporting threshold.
        return where(
            net_sei < p.self_employment.net_earnings_exemption, 0, net_sei
        )
