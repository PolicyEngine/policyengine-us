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
        # Sum filers directly: a supplied tax-unit net_capital_gains does
        # not enter federal AGI, and removing dependents from a rounded
        # aggregate can lose a filer's smaller gain. The person-level
        # source also respects capital_gains supplied directly to AGI.
        person = tax_unit.members
        not_dependent = ~person("is_tax_unit_dependent", period)
        own_gains = person("capital_gains", period) + max_(
            0, person("non_sch_d_capital_gains", period)
        )
        # A federal net capital loss stays negative after the loss limit,
        # so that limit cannot affect Missouri's positive-gain subtraction.
        federally_reported_capital_gains = max_(
            0, tax_unit.sum(not_dependent * own_gains)
        )
        p = parameters(period).gov.states.mo.tax.income.subtractions.net_capital_gain
        return federally_reported_capital_gains * p.rate
