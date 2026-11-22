from policyengine_us.model_api import *


class ny_real_property_tax_credit_claimant(Variable):
    value_type = bool
    entity = TaxUnit
    label = "Claimant of the household's New York real property tax credit"
    definition_period = YEAR
    reference = (
        "https://www.nysenate.gov/legislation/laws/TAX/606",  # (e)(6)
        # 2024 IT-214-I: "Only one credit is allowed per household."
        "https://www.tax.ny.gov/pdf/2024/inc/it214i_2024.pdf#page=1",
    )
    defined_for = StateCode.NY

    def formula(tax_unit, period, parameters):
        rptc = parameters(period).gov.states.ny.tax.income.credits.real_property_tax
        # 606(e)(6)(B): from 2025 "only one credit per qualified taxpayer shall
        # be allowed", so each tax unit claims its own credit. The household
        # gross income switch marks the household rules of Part RR of Chapter
        # 59 of the Laws of 2025 (see ny_real_property_tax_credit_potential).
        if not rptc.uses_household_gross_income:
            return np.ones(tax_unit.count, dtype=bool)
        # 606(e)(6)(A): through 2024 "only one credit per household and per
        # qualified taxpayer shall be allowed". Qualifying members divide it
        # equally unless they file "a written agreement ... setting forth a
        # different division"; the 2024 IT-214-I line 33 lets them "divide the
        # amount any way you want". As a modeling convention, the household's
        # credit goes to the tax unit whose potential claim is largest. A tie
        # goes to the tax unit holding the household head, and otherwise to
        # the tax unit whose head comes first in the simulation's person
        # order.
        person = tax_unit.members
        candidate = person("is_tax_unit_head", period)
        claim = person.tax_unit("ny_real_property_tax_credit_potential", period)
        largest = person.household.max(where(candidate, claim, -np.inf))
        tied = candidate & (claim >= largest)
        holds_household_head = person.tax_unit.any(person("is_household_head", period))
        # get_rank sorts by members_position, so rank 0 goes to the first tied
        # tax unit holding the household head, or, if none does, to the tied
        # tax unit whose head comes first in the simulation's person order.
        rank = person.get_rank(
            person.household, where(holds_household_head, 0, 1), condition=tied
        )
        return tax_unit.any(tied & (rank == 0))
