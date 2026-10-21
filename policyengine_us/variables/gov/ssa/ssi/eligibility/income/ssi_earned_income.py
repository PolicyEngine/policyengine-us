from policyengine_us.model_api import *


class ssi_earned_income(Variable):
    value_type = float
    entity = Person
    label = "SSI earned income"
    unit = USD
    definition_period = YEAR
    reference = "https://secure.ssa.gov/poms.nsf/lnx/0500820102"
    documentation = (
        "Earned income for SSI, excluding health insurance premiums paid "
        "through pretax payroll salary reductions under a qualified "
        "cafeteria plan. The disjoint after-tax premium inputs do not "
        "reduce SSI wages."
    )

    def formula(person, period, parameters):
        sources = parameters(period).gov.ssa.ssi.income.sources.earned
        earned_income = add(person, period, sources)
        if "employment_income" not in sources:
            return earned_income
        # POMS SI 00820.102C.2 excludes salary-reduction premiums from
        # wages; C.4 counts ordinary payroll deductions. Limit the exclusion
        # to wages so it cannot reduce self-employment income.
        wages = max_(person("employment_income", period), 0)
        pretax_premiums = max_(person("pre_tax_health_insurance_premiums", period), 0)
        return earned_income - min_(wages, pretax_premiums)
