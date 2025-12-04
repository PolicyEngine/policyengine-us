from policyengine_us.model_api import *


class msp_countable_income(Variable):
    value_type = float
    entity = Person
    unit = USD
    label = "Medicare Savings Program countable monthly income"
    definition_period = MONTH
    reference = (
        "https://www.medicare.gov/basics/costs/help/medicare-savings-programs",
        "https://www.medicareinteractive.org/understanding-medicare/"
        "cost-saving-programs/medicare-savings-programs-qmb-slmb-qi/"
        "medicare-savings-program-income-and-asset-limits",
    )

    def formula(person, period, parameters):
        # MSP uses a MAGI-like income definition
        # SSI and certain other income is excluded but not modeled here
        yearly_agi = person.tax_unit("adjusted_gross_income", period.this_year)
        monthly_income = yearly_agi / MONTHS_IN_YEAR
        return max_(monthly_income, 0)
