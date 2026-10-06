from policyengine_us.model_api import *


class mt_elderly_homeowner_or_renter_credit_gross_rent(Variable):
    value_type = float
    entity = TaxUnit
    label = "Montana gross rent for the elderly homeowner/renter credit"
    unit = USD
    definition_period = YEAR
    defined_for = StateCode.MT
    reference = (
        # § 15-30-2337(5): gross rent; § 15-30-2340(2): a claimant who rents
        # the homestead
        "https://mca.legmt.gov/bills/mca/title_0150/chapter_0300/part_0230/section_0370/0150-0300-0230-0370.html",
        "https://mca.legmt.gov/bills/mca/title_0150/chapter_0300/part_0230/section_0400/0150-0300-0230-0400.html",
        # ARM 42.4.302(2)(b): property taxes billed may be used "as rent if
        # the property occupied by the claimant is in a name other than the
        # claimant"
        "https://www.law.cornell.edu/regulations/montana/Mont-Admin-r-42.4.302",
        # 2025 Schedule 2EC lines 24 and 25
        "https://revenue.mt.gov/files/forms/Montana-Individual-Income-Tax-Return-Form-2/2025_Montana_Individual_Income_Tax_Return_Form_2.pdf#page=10",
        # 2025 instructions, lines 23 and 24: "If the property occupied by
        # you is in a name other than your own, the property taxes billed for
        # that property can qualify as rent only."
        "https://revenue.mt.gov/files/forms/Montana-Individual-Income-Tax-Return-Form-2-Instructions/2025_Montana_Individual_Income_Tax_Return_Form_2_Instructions.pdf#page=47",
    )

    def formula(tax_unit, period, parameters):
        p = parameters(
            period
        ).gov.states.mt.tax.income.credits.elderly_homeowner_or_renter
        # Schedule 2EC line 24: "the rent that you paid".
        rent = add(tax_unit, period, ["rent"])
        # A claimant billed no property tax lives in a home in another
        # member's name. Its property tax "can qualify as rent only" (2025
        # instructions, line 23; ARM 42.4.302(2)(b)): it goes on line 24, not
        # line 23, so line 25 counts 15% of it. The rule offers that bill as
        # a measure of the claimant's rent for the same home, not an
        # addition to rent paid: read as an addition, every renter could add
        # the landlord's property tax to their rent. So line 24 is the larger
        # of the rent paid and the property tax billed to the household's
        # other members, dependents included. With the claimant billed
        # nothing, that is the household's whole property tax. The
        # household's other members are the only owners the model can see.
        claimant_property_tax = tax_unit(
            "mt_elderly_homeowner_or_renter_credit_property_tax_billed", period
        )
        in_another_name = claimant_property_tax <= 0
        person = tax_unit.members
        head = person("is_tax_unit_head", period)
        household_property_tax = tax_unit.sum(
            add(person.household, period, ["real_estate_taxes"]) * head
        )
        property_tax_as_rent = where(
            in_another_name & p.property_tax_in_another_name_as_rent,
            household_property_tax,
            0,
        )
        return max_(rent, property_tax_as_rent)
