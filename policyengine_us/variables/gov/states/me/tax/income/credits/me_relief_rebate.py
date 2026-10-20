from policyengine_us.model_api import *


class me_relief_rebate(Variable):
    value_type = float
    entity = TaxUnit
    label = "Maine Relief Rebate"
    defined_for = "me_relief_rebate_eligible"
    unit = USD
    definition_period = YEAR
    reference = (
        "https://www.maine.gov/governor/mills/relief-checks",
        # P.L. 2021, c. 635, Part L, section L-3.
        "https://www.legislature.maine.gov/legis/bills/getPDF.asp?item=3&paper=HP1482&snum=130#page=176",
    )

    def formula(tax_unit, period, parameters):
        p = parameters(period).gov.states.me.tax.income.credits.relief_rebate
        # P.L. 2021, c. 635, Part L-3 pays each eligible resident who "may not
        # be claimed as a dependent on another taxpayer's return".
        dependent_filer = tax_unit("head_or_spouse_is_dependent_elsewhere", period)
        recipients = where(
            dependent_filer,
            tax_unit("head_spouse_count_not_dependent_elsewhere", period),
            tax_unit("head_spouse_count", period),
        )
        return recipients * p.amount
