from policyengine_us.model_api import *


PERSON_LEVEL_MEDICAID_MAGI_ADDITIONS = ["tax_exempt_interest_income"]

# Tax-unit MAGI additions with a person-level equivalent that gives each
# member their own amount, a tax unit dependent's included.
TAX_UNIT_MEDICAID_MAGI_ADDITIONS_WITH_PERSON_LEVEL_EQUIVALENTS = {
    "filer_tax_exempt_social_security": "tax_exempt_social_security_person",
}


class medicaid_magi_person(Variable):
    value_type = float
    entity = Person
    label = "Person-level Medicaid MAGI"
    unit = USD
    documentation = (
        "Each person's MAGI-based income: their Medicaid AGI plus the MAGI "
        "additions. Social Security benefits not in AGI are each person's "
        "own, so a tax unit dependent's benefits count in the dependent's "
        "MAGI, which medicaid_household_income adds only when the dependent "
        "is required to file, and never in the head's or spouse's. Other "
        "additions recorded only for the tax unit are divided between the "
        "head and spouse."
    )
    definition_period = YEAR
    reference = (
        "https://www.law.cornell.edu/uscode/text/42/1396a#e_14_G",
        "https://www.law.cornell.edu/uscode/text/26/36B#d_2",
        "https://www.law.cornell.edu/cfr/text/42/435.603#e",
    )

    def formula(person, period, parameters):
        agi = person("medicaid_adjusted_gross_income_person", period)
        additions = parameters(period).gov.hhs.medicaid.income.modification
        equivalents = TAX_UNIT_MEDICAID_MAGI_ADDITIONS_WITH_PERSON_LEVEL_EQUIVALENTS
        person_level_additions = [
            equivalents.get(addition, addition)
            for addition in additions
            if addition in PERSON_LEVEL_MEDICAID_MAGI_ADDITIONS
            or addition in equivalents
        ]
        tax_unit_level_additions = [
            addition
            for addition in additions
            if addition not in PERSON_LEVEL_MEDICAID_MAGI_ADDITIONS
            and addition not in equivalents
        ]
        filing_status = person.tax_unit("filing_status", period)
        frac = where(
            filing_status == filing_status.possible_values.JOINT,
            0.5,
            1.0,
        )
        shared_additions = (
            person("is_tax_unit_head_or_spouse", period)
            * add(person.tax_unit, period, tax_unit_level_additions)
            * frac
        )
        return max_(
            0,
            agi + add(person, period, person_level_additions) + shared_additions,
        )
