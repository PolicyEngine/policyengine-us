from policyengine_us.model_api import *


class ky_ssp_eligible(Variable):
    value_type = bool
    entity = Person
    label = "Eligible for Kentucky State Supplementary Payment"
    definition_period = MONTH
    defined_for = StateCode.KY
    reference = (
        "https://apps.legislature.ky.gov/law/kar/titles/921/002/015/",
        "https://apps.legislature.ky.gov/law/statutes/statute.aspx?id=7671",
    )

    def formula(person, period, parameters):
        # 921 KAR 2:015 §4(1) — Group 2 pathway. An eligible individual must
        # meet SSI categorical criteria (ABD, resources, immigration) and
        # have income below the state standard. Actual SSI receipt is NOT
        # required: §4(1)(b) only requires "insufficient income to meet the
        # payment standards established in Section 9". §3(3) makes SSI
        # application mandatory if potentially eligible, but non-receipt
        # with income below the state standard still qualifies.
        categorically_eligible = person("is_ssi_eligible", period)
        # §4(1)(c): age ≥ 18 required for all four categories (PCH, CIS, FCH,
        # Caretaker).
        is_adult = person("is_adult", period)
        category = person("ky_ssp_category", period)
        in_qualifying_category = category != category.possible_values.NONE
        # §4(1)(b): insufficient income to meet the standard in §9.
        countable_income = person("ssi_countable_income", period)
        payment_standard = person("ky_ssp_payment_standard", period)
        income_below_standard = countable_income < payment_standard
        return (
            categorically_eligible
            & is_adult
            & in_qualifying_category
            & income_below_standard
        )
