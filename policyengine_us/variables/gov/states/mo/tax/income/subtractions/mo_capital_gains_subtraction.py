from policyengine_us.model_api import *


class mo_capital_gains_subtraction(Variable):
    value_type = float
    entity = TaxUnit
    label = "Missouri capital gains subtraction"
    unit = USD
    definition_period = YEAR
    documentation = (
        "Income reported as a capital gain for federal income tax purposes: "
        "the positive amount on the filers' federal Form 1040 line 7a, which "
        "is their Schedule D net capital gain with capital gain distributions "
        "(or the distributions alone). A tax unit dependent's gains and "
        "losses are on the dependent's own return, so they are left out, as "
        "they are left out of federal adjusted gross income."
    )
    reference = (
        "https://www.revisor.mo.gov/main/OneSection.aspx?section=143.121&bid=57543",
        "https://dor.mo.gov/faq/taxation/individual/capital-gains-subtraction.html",
        "https://dor.mo.gov/forms/MO-1040%20Instructions_2025.pdf#page=16",
    )
    defined_for = StateCode.MO

    def formula(tax_unit, period, parameters):
        # RSMo 143.121.3(14)(a) subtracts income reported as a capital gain
        # for federal income tax purposes, to the extent included in federal
        # AGI. The Department of Revenue reads that as Form 1040 line 7a, and
        # says capital losses do not qualify.
        federally_reported_capital_gains = max_(
            0, tax_unit("filer_loss_limited_net_capital_gains", period)
        )
        p = parameters(period).gov.states.mo.tax.income.subtractions.net_capital_gain
        return federally_reported_capital_gains * p.rate
