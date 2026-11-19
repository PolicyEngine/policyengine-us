from policyengine_us.model_api import *


class nm_modified_gross_income(Variable):
    value_type = float
    entity = TaxUnit
    label = "New Mexico modified gross income"
    unit = USD
    documentation = (
        "All income of the taxpayer, spouse and dependents, undiminished by "
        "losses and from whatever source, for the New Mexico rebates and "
        "credits on Schedule PIT-RC. Each listed source counts at zero or "
        "more: a person-level source is floored for each person before the "
        "tax unit sums it, so one person's loss does not reduce another "
        "person's income, and a source defined for the tax unit or a larger "
        "group is floored for the tax unit."
    )
    definition_period = YEAR
    reference = (
        "https://nmonesource.com/nmos/nmsa/en/item/4340/index.do#!fragment/zoupio-_Toc140503656",
        "https://www.law.cornell.edu/regulations/new-mexico/N-M-Admin-Code-SS-3.3.1.10",
        "https://taxsim.nber.org/historical_state_tax_forms/NM/2025/NM_PIT_RC_INST.PDF#page=4",
    )
    defined_for = StateCode.NM

    def formula(tax_unit, period, parameters):
        # Per NM Admin Code 3.3.1.10(B):
        # "zero is the lowest amount which may be reported for any item
        # in computing 'modified gross income'"
        # "The loss from one business or activity shall not reduce
        # the income from another business or activity."
        # PIT-RC line 8: you "may not offset the loss of one business, farm,
        # or rental against the profit of another business, farm, or rental
        # or against any other source of income."
        sources = parameters(period).gov.states.nm.tax.income.modified_gross_income
        person = tax_unit.members
        total = 0
        for source in sources:
            if tax_unit.entity.get_variable(source).entity.is_person:
                # Each person's amount is floored, so a spouse's or
                # dependent's loss does not reduce another member's income.
                total += tax_unit.sum(max_(person(source, period), 0))
            else:
                # Sources defined for the tax unit (tax_unit_social_security,
                # other_net_gain, section_911_excluded_income) or for a larger
                # group (tanf, whose SPM unit amount add apportions to the
                # tax unit by its members) are floored for the tax unit.
                total += max_(add(tax_unit, period, [source]), 0)
        return total
