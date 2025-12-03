from policyengine_us.model_api import *


class msp_countable_income(Variable):
    value_type = float
    entity = Person
    unit = USD
    label = "Medicare Savings Program countable income"
    definition_period = MONTH
    documentation = (
        "Monthly countable income for Medicare Savings Program eligibility. "
        "Based on modified adjusted gross income (MAGI)."
    )
    reference = "https://www.cms.gov/medicare/costs/medicare-savings-programs"

    def formula(person, period, parameters):
        # Use adjusted gross income divided by 12 for monthly income
        # AGI is a tax_unit level variable
        agi = person.tax_unit("adjusted_gross_income", period.this_year)
        return agi / MONTHS_IN_YEAR
