from policyengine_us.model_api import *


class filer_meets_additional_senior_deduction_identification_requirements(
    Variable
):
    value_type = bool
    entity = TaxUnit
    definition_period = YEAR
    label = (
        "Filer meets additional senior deduction identification requirements"
    )
    reference = "https://www.finance.senate.gov/imo/media/doc/finance_committee_legislative_text_title_vii.pdf#page=3"

    def formula(tax_unit, period, parameters):
        # Both head and spouse in the tax unit must have valid SSN card type to be eligible for the CTC
        person = tax_unit.members
        is_head_or_spouse = person("is_tax_unit_head_or_spouse", period)
        eligible_ssn_card_type = person(
            "meets_additional_senior_deduction_identification_requirements",
            period,
        )
        ineligible_head_or_spouse = is_head_or_spouse & ~eligible_ssn_card_type
        return tax_unit.sum(ineligible_head_or_spouse) == 0
