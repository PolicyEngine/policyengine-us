from policyengine_us.model_api import *


class oh_long_term_care_insurance_premiums(Variable):
    value_type = float
    entity = Person
    label = "Ohio long-term care insurance premiums for the unreimbursed medical care deduction"
    unit = USD
    definition_period = YEAR
    reference = (
        "https://codes.ohio.gov/ohio-revised-code/section-5747.01",  # R.C. 5747.01(A)(10)
        "https://dam.assets.ohio.gov/image/upload/v1767095693/tax.ohio.gov/forms/ohio_individual/individual/2025/it1040-booklet.pdf#page=41",  # Worksheet
    )
    documentation = (
        "Long-term care insurance premiums for the Ohio unreimbursed medical "
        "care deduction, less the part of the person's federal self-employed "
        "health insurance deduction that took them. That deduction already "
        "reduced federal adjusted gross income, Ohio's starting point, so the "
        "same premiums are not deducted twice. The federal deduction is taken "
        "from medical insurance premiums first, as "
        "itemized_medical_expenses_excluded_premiums does."
    )
    defined_for = StateCode.OH

    def formula(person, period, parameters):
        premiums = person("long_term_health_insurance_premiums", period)
        self_employed_deduction = max_(
            0, person("self_employed_health_insurance_ald_person", period)
        )
        # The part of the deduction left after the person's medical insurance
        # premiums (Form 7206 line 1) took long-term care premiums (line 2).
        medical_part = min_(
            person("self_employed_health_insurance_premiums", period),
            self_employed_deduction,
        )
        long_term_care_part = self_employed_deduction - medical_part
        return max_(premiums - long_term_care_part, 0)
