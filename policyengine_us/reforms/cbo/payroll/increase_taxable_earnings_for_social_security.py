from policyengine_us.model_api import *


def create_increase_taxable_earnings_for_social_security() -> Reform:
    class taxable_earnings_for_social_security(Variable):
        value_type = float
        entity = Person
        label = "Taxable gross earnings for OASDI FICA"
        definition_period = YEAR
        unit = USD

        def formula(person, period, parameters):
            earnings = person("payroll_tax_gross_wages", period)
            p = parameters(period).gov
            base_taxable = min_(earnings, p.irs.payroll.social_security.cap)
            secondary_taxable = max_(
                0,
                earnings - p.contrib.cbo.payroll.secondary_earnings_threshold,
            )
            return base_taxable + secondary_taxable

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

    if p.secondary_earnings_threshold < np.inf:
        return create_increase_taxable_earnings_for_social_security()
    else:
        return None


increase_taxable_earnings_for_social_security = (
    create_increase_taxable_earnings_for_social_security_reform(
        None, None, bypass=True
    )
)
