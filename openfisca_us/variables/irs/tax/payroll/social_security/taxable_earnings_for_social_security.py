from openfisca_us.model_api import *


class taxable_earnings_for_social_security(Variable):
    value_type = float
    entity = Person
    label = "Taxable gross earnings for OASDI FICA"
    definition_period = YEAR
    unit = USD

    def formula(person, period, parameters):
        irs = parameters(period).irs
        max_earnings = irs.payroll.social_security.max_taxable_earnings
        return min_(max_earnings, person("payroll_tax_gross_wages", period))
