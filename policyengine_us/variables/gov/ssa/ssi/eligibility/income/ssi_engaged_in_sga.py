from policyengine_us.model_api import *


class ssi_engaged_in_sga(Variable):
    value_type = bool
    entity = Person
    label = "Income less than the SGA limit"
    definition_period = YEAR
    reference = (
        "https://www.ssa.gov/OP_Home/cfr20/416/416-0971.htm",
        "https://secure.ssa.gov/poms.nsf/lnx/0410505010",
        "https://secure.ssa.gov/poms.nsf/lnx/0410505015",
        "https://secure.ssa.gov/poms.nsf/lnx/0410510012",
    )
    documentation = (
        "Whether non-blind work earnings exceed the SGA limit. Work earnings "
        "are wages plus the net of the business earned-income sources, "
        "floored at zero: losses net across businesses but never reduce "
        "wages. Payroll health insurance premiums remain in these earnings, "
        "including pretax salary reductions excluded from SSI payment income."
    )

    def formula(person, period, parameters):
        sources = parameters(period).gov.ssa.ssi.income.sources.earned
        business_sources = [
            source for source in sources if source != "employment_income"
        ]
        business_net = add(person, period, business_sources) if business_sources else 0
        # POMS DI 10505.015 D.3: a self-employment loss does not reduce total
        # earnings when the individual also has wages. Losses still net
        # between businesses (20 CFR 404.1081(c), POMS DI 10510.012 B), so
        # only a net business loss is added back. This assumes
        # ssi_earned_income already holds that business net. A situation that
        # supplies ssi_earned_income directly and also a business source adds
        # the loss back to an amount that never subtracted it.
        restored_loss = max_(-business_net, 0)
        income = person("ssi_earned_income", period) + restored_loss
        # POMS DI 10505.010A counts payroll insurance premiums for SGA.
        # Restore exactly the wage-limited premium exclusion made by
        # ssi_earned_income, preserving the prior gross work-earnings base.
        # With ssi_earned_income computed, income is wages plus the business
        # net floored at zero.
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
