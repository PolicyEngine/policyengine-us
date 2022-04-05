from openfisca_us.model_api import *


class payroll_taxable_self_employment_income(Variable):
    value_type = float
    entity = Person
    label = "Taxable self-employment income"
    definition_period = YEAR
    unit = USD
    reference = "https://www.law.cornell.edu/uscode/text/26/1402#a"

    def formula(person, period, parameters):
        irs = parameters(period).irs
        combined_rate = (
            irs.payroll.social_security.rate.self_employment
            + irs.payroll.medicare.rate.self_employment
        )
        deduction_rate = irs.ald.misc.employer_share * combined_rate
        base = max_(person("sey", period), 0)
        return base * (1 - deduction_rate)
