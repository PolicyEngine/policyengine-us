from policyengine_us.model_api import *


def create_increase_taxable_earnings_for_social_security() -> Reform:
    class taxable_earnings_for_social_security(Variable):
        value_type = float
        entity = Person
        label = "Taxable gross earnings for OASDI FICA"
        definition_period = YEAR
        unit = USD
        reference = (
            "https://www.cbo.gov/budget-options/60955",
            "https://www.ssa.gov/OACT/solvency/provisions_tr2025/charts/chart_run418.html",
        )

        def formula(person, period, parameters):
            earnings = person("payroll_tax_gross_wages", period)
            p = parameters(period).gov
            cap = p.irs.payroll.social_security.cap
            secondary_threshold = max_(
                p.contrib.cbo.payroll.secondary_earnings_threshold, cap
            )
            base_taxable = min_(earnings, cap)
            # The bases meet without overlapping once the cap closes the donut.
            secondary_taxable = max_(0, earnings - secondary_threshold)
            return base_taxable + secondary_taxable

    class social_security_taxable_self_employment_income(Variable):
        value_type = float
        entity = Person
        label = "Taxable self-employment income for computing Social Security tax"
        definition_period = YEAR
        unit = USD
        reference = (
            "https://www.cbo.gov/budget-options/60955",
            "https://www.law.cornell.edu/uscode/text/26/1402#b",
            "https://www.ssa.gov/OACT/solvency/provisions_tr2025/charts/chart_run418.html",
        )

        def formula(person, period, parameters):
            earnings = person("taxable_self_employment_income", period)
            wages = person("payroll_tax_gross_wages", period)
            p = parameters(period).gov
            cap = p.irs.payroll.social_security.cap
            secondary_threshold = max_(
                p.contrib.cbo.payroll.secondary_earnings_threshold, cap
            )
            # Wages fill the combined base first, both below the cap and
            # above the secondary threshold. Only the remaining SE is taxed.
            base_taxable = min_(earnings, max_(0, cap - wages))
            secondary_taxable = max_(0, earnings - max_(0, secondary_threshold - wages))
            return base_taxable + secondary_taxable

    class reform(Reform):
        def apply(self):
            self.update_variable(taxable_earnings_for_social_security)
            self.update_variable(social_security_taxable_self_employment_income)

    return reform


def create_increase_taxable_earnings_for_social_security_reform(
    parameters, period, bypass: bool = False
):
    if bypass:
        return create_increase_taxable_earnings_for_social_security()

    threshold = parameters.gov.contrib.cbo.payroll.secondary_earnings_threshold
    # Inspect dated overrides, as in the CA Proposition 3 reform, rather
    # than only the simulation's start instant or a fixed lookahead window.
    if any(np.isfinite(value.value) for value in threshold.values_list):
        return create_increase_taxable_earnings_for_social_security()
    else:
        return None


increase_taxable_earnings_for_social_security = (
    create_increase_taxable_earnings_for_social_security_reform(None, None, bypass=True)
)
