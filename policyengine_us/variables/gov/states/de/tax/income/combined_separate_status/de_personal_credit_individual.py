from policyengine_us.model_api import *


class de_personal_credit_individual(Variable):
    value_type = float
    entity = TaxUnit
    label = "Delaware individual personal credit for combined separate filing status"
    unit = USD
    definition_period = YEAR
    reference = "https://revenuefiles.delaware.gov/2022/PIT-RES_TY22_2022-02_Instructions.pdf#page=8"
    defined_for = StateCode.DE

    def formula(tax_unit, period, parameters):
        person = tax_unit.members
        p = parameters(
            period
        ).gov.states.de.tax.income.credits.personal_credits
        # To calculate the number of dedpents, we need the variable
        # "exemptions_count" and "head_spouse_count" from the tax_Unit level
        exemptions_count = tax_unit("exemptions_count", period)
        head_spouse_count = tax_unit("head_spouse_count", period)
        # Regular personal credit
        regular_personal_credit = select(
            [
                person("is_tax_unit_spoue", period),
                person("is_tax_unit_head", period),
            ],
            [p.personal, (exemptions_count - head_spouse_count) * p.personal],
            default=0,
        )
        # Aged personal credit
        aged_personal_credit = p.aged.cal(person("age", period))
        return regular_personal_credit + aged_personal_credit
