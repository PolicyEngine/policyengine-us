from policyengine_us.model_api import *


class de_income_tax_before_non_refundable_credits(Variable):
    value_type = float
    entity = TaxUnit
    label = "Delaware personal income tax before refundable credits for combined separate filing status"
    unit = USD
    definition_period = YEAR
    defined_for = StateCode.DE

    def formula(tax_unit, period, parameters):
        p = parameters(period).gov.states.de.tax.income.credits
        exemptions_count = tax_unit("exemptions_count", period)
        # The instruction says If you are married and filing a combined separate return (Filing Status 4),
        # split the total between Columns A and B in increments of $110.
        # for example, if a tax unit has a head, a spouse and a child,
        # the total between column A and column B would be 110 * 3 =330
        # then what will the split result be ?
        return p.personal_credits.personal * exemptions_count
