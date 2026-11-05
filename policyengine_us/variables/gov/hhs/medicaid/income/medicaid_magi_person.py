from policyengine_us.model_api import *


class medicaid_magi_person(Variable):
    value_type = float
    entity = Person
    label = "Person-level Medicaid MAGI"
    unit = USD
    documentation = (
        "Each person's MAGI-based income: their Medicaid AGI plus the MAGI "
        "additions. A person-level addition, such as tax-exempt interest, is "
        "the person's own; an addition recorded only for the tax unit is "
        "divided equally between the head and spouse. The head's and "
        "spouse's amounts add up to their return's MAGI before any floor. "
        "This amount is not floored at zero, so one household member's loss "
        "offsets the others' income in medicaid_household_income, which "
        "floors the household's total."
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
        total = agi
        for addition in additions:
            variable = person.entity.get_variable(addition, check_existence=True)
            if variable.entity.is_person:
                total = total + person(addition, period)
            else:
                amount = person.tax_unit(addition, period)
                total = total + amount * filer_share(person, period, 0 * amount)
        return total
