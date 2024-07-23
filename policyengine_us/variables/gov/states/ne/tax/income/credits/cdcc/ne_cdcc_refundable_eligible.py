from policyengine_us.model_api import *


class ne_cdcc_refundable_eligible(Variable):
    value_type = bool
    entity = TaxUnit
    label = "Eligible for the Nebraska refundable CDCC"
    unit = USD
    definition_period = YEAR
    reference = (
        "https://revenue.nebraska.gov/files/doc/tax-forms/2021/f_2441n.pdf"
        "https://revenue.nebraska.gov/sites/revenue.nebraska.gov/files/doc/Form_2441N_Ne_Child_and_Dependent_Care_Expenses_8-618-2022_final_2.pdf"
    )
    defined_for = StateCode.NE

    def formula(tax_unit, period, parameters):
        p = parameters(period).gov.states.ne.tax.income.credits.cdcc.refundable
        us_agi = tax_unit("adjusted_gross_income", period)
        return us_agi < p.income_limit
