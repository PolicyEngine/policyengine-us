from policyengine_us.model_api import *


class de_nonrefundable_eitc(Variable):
    value_type = float
    entity = Person
    label = "Delaware individual nonrefundable earned income credit"
    unit = USD
    definition_period = YEAR
    reference = "https://revenuefiles.delaware.gov/2021/TY21_PIT-RSS_2021-01_PaperInteractive.pdf#page=1"
    defined_for = StateCode.DE

    def formula(tax_unit, period, parameters):
        """
        In the case of spouses who file a joint federal return, but who elect to file separate or
        combined separate returns for Delaware, the credit may only be applied against the tax
        imposed on the spouse with the higher taxable income reported on Line 22
        """
        person = tax_unit.members
        p = parameters(
            period
        ).gov.states.de.tax.income.credits.personal_credits
        return p.personal
