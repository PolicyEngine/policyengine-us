from policyengine_us.model_api import *


class mt_elderly_homeowner_or_renter_credit_selected_claimant(Variable):
    value_type = bool
    entity = TaxUnit
    label = "Selected claimant for the Montana Elderly Homeowner/Renter Credit"
    definition_period = YEAR
    defined_for = StateCode.MT
    reference = (
        # § 15-30-2341(1): one claimant per household
        "https://mca.legmt.gov/bills/mca/title_0150/chapter_0300/part_0230/section_0410/0150-0300-0230-0410.html",
        # § 15-30-2337(5), (7), (10): gross rent, household, property tax
        # billed
        "https://mca.legmt.gov/bills/mca/title_0150/chapter_0300/part_0230/section_0370/0150-0300-0230-0370.html",
        # ARM 42.4.302 (implementing § 15-30-2341): property tax billed to
        # another counts as rent; married couples living apart receive only
        # one credit per year
        "https://www.law.cornell.edu/regulations/montana/Mont-Admin-r-42.4.302",
        # 2025 Schedule 2EC attestation: "I am the only member of my
        # household claiming this credit"
        "https://revenue.mt.gov/files/forms/Montana-Individual-Income-Tax-Return-Form-2/2025_Montana_Individual_Income_Tax_Return_Form_2.pdf#page=10",
        # 2025 instructions: the attestation, the household definition and
        # the joint filers' claimant
        "https://revenue.mt.gov/files/forms/Montana-Individual-Income-Tax-Return-Form-2-Instructions/2025_Montana_Individual_Income_Tax_Return_Form_2_Instructions.pdf#page=45",
        # 2025 instructions, lines 23 and 24: "the property tax you were
        # billed" and "the rent that you paid"
        "https://revenue.mt.gov/files/forms/Montana-Individual-Income-Tax-Return-Form-2-Instructions/2025_Montana_Individual_Income_Tax_Return_Form_2_Instructions.pdf#page=47",
    )

    def formula(tax_unit, period, parameters):
        # "Only one claimant per household in a claim period ... is entitled
        # to relief" (§ 15-30-2341(1)). Neither the statute nor ARM 42.4.302
        # says which member claims. Every eligible tax unit in a household has
        # the same gross and net household income, so their credits differ
        # only by Schedule 2EC line 26: property tax billed plus 15% of rent,
        # before the $1,150 cap. The model counts each tax unit's own
        # property tax and rent, following the form's wording ("the property
        # tax you were billed", "the rent that you paid"; property in
        # another's name "can qualify as rent only"). The statute instead
        # defines both for the homestead (§ 15-30-2337(5), (10)), which would
        # give the one claimant the household's whole property tax and rent;
        # that reading is not modeled. We select the tax unit whose credit is
        # largest, the claim a household would choose. get_rank ranks the
        # candidates in each household 0, 1, 2, ..., so exactly one has rank
        # 0; its stable sort gives a tie to the first in member order. A
        # joint return is one tax unit and one claim; the 2025 instructions
        # name the spouse listed as the taxpayer as the claimant when both
        # qualify, and the model holds that credit on the tax unit head.
        # ARM 42.4.302(3)(a) also allows married couples living apart only
        # one credit a year; a separated spouse in another tax unit is not
        # linked to the other spouse, so that limit is not modeled.
        person = tax_unit.members
        head = person("is_tax_unit_head", period)
        eligible = person("mt_elderly_homeowner_or_renter_credit_eligible", period)
        credit = person(
            "mt_elderly_homeowner_or_renter_credit_pre_one_claimant", period
        )
        candidate = head & eligible
        rank = person.get_rank(person.household, -credit, condition=candidate)
        return tax_unit.any(candidate & (rank == 0))
