from policyengine_us.model_api import *


class social_security_taxable_self_employment_income(Variable):
    value_type = float
    entity = Person
    label = "Taxable self-employment income for computing Social Security tax"
    definition_period = YEAR
    unit = USD
    reference = "https://www.law.cornell.edu/uscode/text/26/1402#b"

    def formula(person, period, parameters):
        p = parameters(period).gov.irs.payroll.social_security
        # Reforms may tax wages above the current-law cap. They cannot
        # leave negative room for self-employment earnings.
        cap_minus_earnings = max_(
            0,
            p.cap - person("taxable_earnings_for_social_security", period),
        )
        # Deduct SS payroll taxable wages and salaries.
        return min_(
            person("taxable_self_employment_income", period),
            cap_minus_earnings,
        )
