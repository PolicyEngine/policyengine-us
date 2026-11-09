from policyengine_us.model_api import *


class medicaid_eligibility_health_insurance_premiums(Variable):
    value_type = float
    entity = Person
    label = "Health insurance premiums counted for Medicaid eligibility"
    unit = USD
    definition_period = YEAR
    reference = (
        "https://www.ecfr.gov/current/title-42/section-435.121#p-435.121(f)",
        "https://www.ecfr.gov/current/title-42/section-435.831",
    )
    documentation = (
        "Person-level non-pretax health insurance premiums that Medicaid "
        "eligibility tests deduct, such as 209(b) and medically needy "
        "spend-down. Matches medical_expense_health_insurance_premiums but "
        "counts the Medicare Part B premium before the state's Medicaid "
        "buy-in (medicare_part_b_premium_before_buy_in), because the buy-in "
        "starts only once Medicaid finds the person eligible."
    )

    def formula(person, period, parameters):
        direct = person("health_insurance_premiums", period)
        non_medicare = person(
            "health_insurance_premiums_without_medicare_part_b", period
        )
        part_b_enrolled = person("medicare_part_b_enrolled", period)
        medicare_part_b = (
            person("medicare_part_b_premium_before_buy_in", period) * part_b_enrolled
        )
        decomposed = non_medicare + medicare_part_b
        return where(direct != 0, direct, decomposed)
