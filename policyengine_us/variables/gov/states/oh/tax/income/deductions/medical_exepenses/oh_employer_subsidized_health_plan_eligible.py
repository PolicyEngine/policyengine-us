from policyengine_us.model_api import *


class oh_employer_subsidized_health_plan_eligible(Variable):
    value_type = bool
    entity = TaxUnit
    label = "Ohio filer eligible for an employer-subsidized health plan"
    definition_period = YEAR
    reference = (
        "https://codes.ohio.gov/ohio-revised-code/section-5747.01",  # R.C. 5747.01(A)(10)(a)
        "https://dam.assets.ohio.gov/image/upload/v1767095693/tax.ohio.gov/forms/ohio_individual/individual/2025/it1040-booklet.pdf#page=41",  # Worksheet lines 1 and 3
    )
    defined_for = StateCode.OH

    def formula(tax_unit, period, parameters):
        person = tax_unit.members
        # Enrolled in, or offered, employer coverage.
        has_employer_coverage = person("has_esi", period) | person(
            "offered_aca_disqualifying_esi", period
        )
        contribution = person(
            "employer_contribution_to_health_insurance_premiums_category",
            period,
        )
        status = contribution.possible_values
        employer_pays = (contribution == status.SOME) | (contribution == status.ALL)
        # The plan must be maintained by the taxpayer's or the spouse's
        # employer, so a dependent's own coverage does not count.
        head_or_spouse = person("is_tax_unit_head_or_spouse", period)
        return tax_unit.any(head_or_spouse & (has_employer_coverage | employer_pays))
