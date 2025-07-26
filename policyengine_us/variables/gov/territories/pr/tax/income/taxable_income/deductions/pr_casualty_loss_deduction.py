from policyengine_us.model_api import *


class pr_casualty_loss_deduction(Variable):
    value_type = float
    entity = TaxUnit
    label = "Puerto Rico casualty loss deduction"
    unit = USD
    definition_period = YEAR
    reference = "https://law.justia.com/codes/puerto-rico/title-thirteen/subtitle-17/part-ii/chapter-1005/subchapter-c/30135/"  # (10)
    defined_for = StateCode.PR

    def formula(tax_unit, period, parameters):
        p = parameters(
            period
        ).gov.territories.pr.tax.income.taxable_income.deductions.casualty_loss
        loss = add(tax_unit, period, ["casualty_loss"])
        filing_status = tax_unit("filing_status", period)

        return (
            where(
                filing_status == filing_status.possible_values.SEPARATE,
                p.separate_percentage,
                1,
            )
            * loss
        )
