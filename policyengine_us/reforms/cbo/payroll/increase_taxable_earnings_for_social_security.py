from policyengine_us.model_api import *


def create_increase_taxable_earnings_for_social_security() -> Reform:
    class taxable_earnings_for_social_security(Variable):
        value_type = float
        entity = Person
        label = "Taxable gross earnings for OASDI FICA"
        definition_period = YEAR
        unit = USD

        def formula(person, period, parameters):
            cap = parameters(period).gov.irs.payroll.social_security.cap
            upper_threshold = parameters(
                period
            ).gov.contrib.cbo.payroll.taxable_earnings_upper_threshold
            return min_(cap, person("payroll_tax_gross_wages", period)) + max_(
                0, person("payroll_tax_gross_wages", period) - upper_threshold
            )

    class reform(Reform):
        def apply(self):
            self.update_variable(taxable_earnings_for_social_security)

    return reform


def create_increase_taxable_earnings_for_social_security_reform(
    parameters, period, bypass: bool = False
):
    if bypass:
        return create_increase_taxable_earnings_for_social_security()

    p = parameters(period).gov.contrib.cbo.payroll

    if p.taxable_earnings_upper_threshold < 9999999999999999999999999:
        return create_increase_taxable_earnings_for_social_security()
    else:
        return None


increase_taxable_earnings_for_social_security = (
    create_increase_taxable_earnings_for_social_security_reform(
        None, None, bypass=True
    )
)
