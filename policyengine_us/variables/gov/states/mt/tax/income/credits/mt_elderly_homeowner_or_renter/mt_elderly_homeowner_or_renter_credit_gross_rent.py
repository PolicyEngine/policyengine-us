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
        # ARM 42.4.302(5) before its 2017 restructuring, in force from
        # 8/20/2004: "Property taxes billed are allowable as rent if the
        # property occupied by an eligible claimant is in a name other than
        # the claimant."
        "https://web.archive.org/web/20080624004125/http://www.mtrules.org/gateway/RuleNo.asp?RN=42.4.302",
        # 2025 Schedule 2EC lines 24 and 25
        "https://revenue.mt.gov/files/forms/Montana-Individual-Income-Tax-Return-Form-2/2025_Montana_Individual_Income_Tax_Return_Form_2.pdf#page=10",
        # 2025 instructions, lines 23 and 24: "If the property occupied by
        # you is in a name other than your own, the property taxes billed for
        # that property can qualify as rent only."
        "https://revenue.mt.gov/files/forms/Montana-Individual-Income-Tax-Return-Form-2-Instructions/2025_Montana_Individual_Income_Tax_Return_Form_2_Instructions.pdf#page=47",
    )

    def formula(tax_unit, period, parameters):
        # Schedule 2EC line 24: "the rent that you paid".
        rent = add(tax_unit, period, ["rent"])
        # The model treats a tax unit billed no property tax, dependents
        # included, as living in a home in another household member's name.
        # Its property tax "can qualify as rent only" (2025 instructions,
        # line 23; ARM 42.4.302(2)(b)): it goes on line 24, not line 23, so
        # line 25 counts 15% of it. With the tax unit billed nothing, "the
        # property taxes billed for that property" are the household's whole
        # property tax.
        # The rule says the claimant "may use" the bill. The model reads that
        # as a choice between two measures of what it costs to occupy one
        # home, not an addition to the rent paid, and takes the larger. Using
        # the bill only when no rent is paid, since gross rent is rent
        # "actually paid" (§ 15-30-2337(5)), is another defensible reading;
        # the two differ only when a claimant pays a household member less
        # rent than that member's bill.
        # Owners outside the household, such as a landlord, are not visible
        # here, and real_estate_taxes is not limited to the residence and
        # one acre.
        claimant_property_tax = tax_unit(
            "mt_elderly_homeowner_or_renter_credit_property_tax_billed", period
        )
        person = tax_unit.members
        head = person("is_tax_unit_head", period)
        household_property_tax = tax_unit.sum(
            add(person.household, period, ["real_estate_taxes"]) * head
        )
        property_tax_as_rent = where(
            claimant_property_tax <= 0, household_property_tax, 0
        )
        return max_(rent, property_tax_as_rent)
