from policyengine_us.model_api import *


class sc_retirement_deduction_survivors(Variable):
    value_type = float
    entity = Person
    label = "South Carolina retirement deduction for survivors"
    defined_for = StateCode.SC
    unit = USD
    reference = (
        "https://www.scstatehouse.gov/code/t12c006.php",  # SECTION 12-6-1170(A)(1), (A)(3), (C)(1)
        "https://dor.sc.gov/sites/dor/files/policies/RR21-13.pdf#page=11",
        "https://dor.sc.gov/sites/dor/files/policies/RR22-11.pdf#page=39",
        "https://dor.sc.gov/sites/dor/files/forms/SC1040Instr_2021.pdf",
        "https://dor.sc.gov/forms-site/Forms/IITPacket_2021.pdf#page=17",
    )
    definition_period = YEAR

    def formula(person, period, parameters):
        p = parameters(period).gov.states.sc.tax.income.subtractions.retirement
        # Line 1: a surviving spouse applies the deduction "in the same manner
        # that the deduction applied to the deceased spouse" (12-6-1170(A)(3)),
        # so the survivor takes the maximum for the age the deceased spouse
        # would have reached.
        deceased_spouse_age = person("deceased_spouse_age", period)
        max_deduction_allowed = p.cap.calc(deceased_spouse_age)
        # Source conflict: the 2021 SC1040 worksheet (line p-3, line 2)
        # reduces this maximum by the military retirement deduction, but
        # 12-6-1170(C)(1) and RR22-11 exclude a military retiree's surviving
        # spouse from that reduction. Following the statute, no reduction
        # applies in any year (candidate
        # us-sc:2021-survivor-offset-surviving-spouse).
        # Line 4: only the head's and spouse's survivor benefits are in the
        # filer's federal AGI; a dependent reports their own on their own
        # return. The deduction passes only to the original owner's surviving
        # spouse, not to other beneficiaries of an inherited account.
        head_or_spouse = person("is_tax_unit_head_or_spouse", period)
        surviving_spouse = person("is_surviving_spouse", period)
        retirement_income_survivors = (
            person("pension_survivors", period) * head_or_spouse * surviving_spouse
        )
        return min_(retirement_income_survivors, max_deduction_allowed)
