from policyengine_us.model_api import *


class az_property_tax_credit_capital_gains(Variable):
    value_type = float
    entity = Person
    label = "Arizona property tax credit capital gains and losses"
    unit = USD
    definition_period = YEAR
    documentation = (
        "A household member's gains and losses from the sale or exchange of "
        "property for the Arizona property tax credit (Form 140PTC Part 1 line D): "
        "the year's gains and losses combined, including capital gain "
        "distributions, with a net loss counted only up to the per-member limit. "
        "No prior-year capital loss carryover is used: the long-term carryover "
        "that long_term_capital_gains nets is added back, including unused "
        "losses transferred by a terminating estate or trust. Short-term inputs "
        "must contain only the current year's net gains and losses, without "
        "Schedule D line 6 carryovers; no short-term carryover memo is modeled."
    )
    reference = [
        "https://www.law.cornell.edu/regulations/arizona/Ariz-Admin-Code-SS-R15-2C-502",
        "https://azdor.gov/sites/default/files/2023-03/RULINGS_INDV_2012_itr12-1.pdf#page=2",
        "https://azdor.gov/sites/default/files/document/FORMS_INDIVIDUAL_2025_140PTCi.pdf#page=4",
        "https://www.law.cornell.edu/uscode/text/26/852#b_3_B",
        "https://www.law.cornell.edu/uscode/text/26/1212#b_1_B",
        "https://www.law.cornell.edu/cfr/text/26/1.642(h)-1",
    ]
    defined_for = StateCode.AZ

    def formula(person, period, parameters):
        p = parameters(period).gov.states.az.tax.income.credits.property_tax
        # A.A.C. R15-2C-502(C)(3): "Income from capital gains is the net capital
        # gains and losses for each member of the household. Net losses are
        # limited to $1,500 for each household member." The limit applies to
        # each member separately, not to the return as the federal limit does.
        # Capital gain distributions reported without Schedule D are long-term
        # capital gains (26 U.S.C. 852(b)(3)(B)), so they are combined with the
        # member's other gains and losses before the limit.
        # ITR 12-1 item (7): a prior-year capital loss carryover cannot reduce
        # the year's gains. long_term_capital_gains includes the long-term
        # carryover (26 U.S.C. 1212(b)(1)(B)) as a loss, as Schedule D line 15
        # does, so it is added back to give the year's own net gain or loss.
        # Reg. 1.642(h)-1(a) transfers a terminating estate/trust's unused
        # capital loss as a carryover. Max's d1107 ruling (2026-10-09) keeps
        # final Form 1041 K-1 box 11 code D losses in this addback.
        carryover = max_(0, person("long_term_capital_loss_carryover", period))
        net_capital_gain = (
            add(person, period, ["capital_gains", "non_sch_d_capital_gains"])
            + carryover
        )
        return max_(net_capital_gain, -p.capital_loss_limit)
