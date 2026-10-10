from policyengine_us.model_api import *


class ssi_engaged_in_sga(Variable):
    value_type = bool
    entity = Person
    label = "Income less than the SGA limit"
    definition_period = YEAR
    reference = (
        "https://www.ssa.gov/OP_Home/cfr20/416/416-0971.htm",
        "https://secure.ssa.gov/poms.nsf/lnx/0410505010",
    )
    documentation = (
        "Whether non-blind work earnings exceed the SGA limit. Payroll "
        "health insurance premiums remain in these earnings, including "
        "pretax salary reductions excluded from SSI payment income."
    )

    def formula(person, period, parameters):
        income = person("ssi_earned_income", period)
        # POMS DI 10505.010A counts payroll insurance premiums for SGA.
        # Restore exactly the wage-limited premium exclusion made by
        # ssi_earned_income, preserving the prior gross work-earnings base.
        sources = parameters(period).gov.ssa.ssi.income.sources.earned
        if "employment_income" in sources:
            wages = max_(person("employment_income", period), 0)
            pretax_premiums = max_(
                person("pre_tax_health_insurance_premiums", period), 0
            )
            income = income + min_(wages, pretax_premiums)
        monthly_income = income / MONTHS_IN_YEAR
        p = parameters(period).gov.ssa.sga

        # SGA does not apply to blind individuals
        is_blind = person("is_blind", period)

        return (monthly_income > p.non_blind) & ~is_blind
