from policyengine_us.model_api import *


class oh_uninsured_unreimbursed_medical_care_expenses(Variable):
    value_type = float
    entity = Person
    label = "Ohio unreimbursed medical and health care expense deduction for uninsured expenses"
    unit = USD
    definition_period = YEAR
    reference = (
        "https://tax.ohio.gov/static/forms/ohio_individual/individual/2022/it1040-sd100-instruction-booklet.pdf#page=18",  # Line 36
        "https://tax.ohio.gov/static/forms/ohio_individual/individual/2022/it1040-sd100-instruction-booklet.pdf#page=27",
        "https://codes.ohio.gov/ohio-revised-code/section-5747.01",  # R.C. 5747.01(10)
    )
    defined_for = StateCode.OH

    def formula(person, period, parameters):
        not_medicare_eligible = ~person("is_medicare_eligible", period)
        employer_premium_contribution = person(
            "employer_contribution_to_health_insurance_premiums_category",
            period,
        )
        status = employer_premium_contribution.possible_values
        health_insurance_premiums = person("health_insurance_premiums", period)
        # Premiums only count if the employer paid none.
        eligible_health_insurance_premiums = health_insurance_premiums * (
            employer_premium_contribution == status.NONE
        )
        return not_medicare_eligible * eligible_health_insurance_premiums
