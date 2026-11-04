from policyengine_us.model_api import *


class mt_elderly_homeowner_or_renter_credit_qualifying_occupancy_months(Variable):
    value_type = int
    entity = Person
    label = "Months occupying a Montana dwelling as an owner, renter, or lessee, for the Montana elderly homeowner/renter credit"
    documentation = (
        "Months of the year, from 0 to 12, this person occupied one or more "
        "Montana dwellings as an owner, renter, or lessee. Another household "
        "member's property tax bill does not establish that status. 12 for "
        "the head and spouse of a tax unit that pays rent or is billed "
        "property tax; otherwise the months recorded in "
        "mt_elderly_homeowner_or_renter_credit_unbilled_occupancy_months, "
        "which defaults to 0. Record a rent-free lessee or owner there, not "
        "here: an input to this variable for one person sets everyone "
        "else's months to 0. The microdata put a household's rent and "
        "property tax on the household reference person, so by default a "
        "co-resident owner or renter in another tax unit fails this test."
    )
    unit = "month"
    definition_period = YEAR
    defined_for = StateCode.MT
    reference = (
        # MCA 15-30-2338(1)(c), (2): occupied one or more dwellings in Montana
        # "as an owner, renter, or lessee for at least 6 months"
        "https://mca.legmt.gov/bills/mca/title_0150/chapter_0300/part_0230/section_0380/0150-0300-0230-0380.html",
        "https://mca.legmt.gov/bills/2009/mca/15/30/15-30-2338.htm",
        # 2025 instructions: the claimant attests "You occupied a Montana
        # residence as a renter, owner, or lessee for at least six months
        # during the tax year"
        "https://revenue.mt.gov/files/forms/Montana-Individual-Income-Tax-Return-Form-2-Instructions/2025_Montana_Individual_Income_Tax_Return_Form_2_Instructions.pdf#page=44",
    )

    def formula(person, period, parameters):
        # Rent paid and property tax billed are the return's (Schedule 2EC
        # lines 23 and 24, "the property tax you were billed" and "the rent
        # that you paid"), so they show that the head and spouse occupy the
        # home as renters or owners. Annual amounts carry no months; like
        # the household's state, they are taken to cover the whole year.
        # A tax unit with neither shows no such status: the household's bill
        # in another member's name can count as rent only for a claimant
        # who is otherwise eligible (ARM 42.4.302(2)(b)), so it cannot
        # establish the status here. An occupant who holds the home as a
        # lessee or owner without either amount is recorded through a
        # separate input, so recording one person leaves everyone else's
        # months to follow their own rent and bill.
        # The microdata put a household's rent and property tax on its
        # reference person, so an older co-owner or co-renter filing in
        # another tax unit (a partner, sibling or parent) gets 0 months
        # unless the input is supplied, and the credit is understated.
        # Tenure facts for other adults are tracked in
        # https://github.com/PolicyEngine/microcosm/issues/1514
        rent = add(person.tax_unit, period, ["rent"])
        property_tax = person.tax_unit(
            "mt_elderly_homeowner_or_renter_credit_property_tax_billed", period
        )
        documented = (rent > 0) | (property_tax > 0)
        head_or_spouse = person("is_tax_unit_head_or_spouse", period)
        documented_months = where(head_or_spouse & documented, MONTHS_IN_YEAR, 0)
        unbilled_months = person(
            "mt_elderly_homeowner_or_renter_credit_unbilled_occupancy_months",
            period,
        )
        return min_(max_(documented_months, unbilled_months), MONTHS_IN_YEAR)
