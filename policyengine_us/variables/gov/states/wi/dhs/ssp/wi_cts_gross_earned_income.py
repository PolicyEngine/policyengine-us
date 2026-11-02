from policyengine_us.model_api import *


class wi_cts_gross_earned_income(Variable):
    value_type = float
    entity = Person
    label = "Wisconsin CTS individual gross earned income"
    definition_period = MONTH
    unit = USD
    reference = (
        # PDF pages 12-13
        "https://www.govinfo.gov/content/pkg/CFR-1997-title45-vol2/pdf/CFR-1997-title45-vol2-sec233-20.pdf#page=12",
        "https://www.dhs.wisconsin.gov/publications/p23131-25-01.pdf#page=31",
    )

    def formula(person, period, parameters):
        # NOTE: AFDC counts wages "prior to any deductions for taxes or for any
        # other purposes" (45 CFR 233.20(a)(6)(iii)-(iv), 1997), so pre-tax
        # health premiums stay in the CTS wage count. Federal SSI excludes them
        # (POMS SI 00820.102 C.2), and the ssi variable keeps that treatment.
        sources = parameters(period).gov.ssa.ssi.income.sources.earned
        return max_(add(person, period, sources), 0)
