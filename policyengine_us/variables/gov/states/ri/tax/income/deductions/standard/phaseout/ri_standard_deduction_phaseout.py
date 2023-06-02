from policyengine_us.model_api import *


class ri_standard_deduction_phaseout(Variable):
    value_type = float
    entity = TaxUnit
    label = "Rhode Island standard deduction phaseout"
    unit = USD
    definition_period = YEAR
    reference = (
        "https://tax.ri.gov/sites/g/files/xkgbur541/files/2022-12/ADV_2022_40_Inflation_Adjustments.pdf"
        "https://tax.ri.gov/sites/g/files/xkgbur541/files/2022-12/2022%20Tax%20Rate%20and%20Worksheets.pdf"
    )
    defined_for = StateCode.RI

    def formula(tax_unit, period, parameters):
        p = parameters(period).gov.states.ri.tax.income.deductions.standard
        filing_status = tax_unit("filing_status", period)

        agi = tax_unit("adjusted_gross_income", period)

        excess_agi = max_(0, agi - p.phaseout.start_values)

        excess_agi_step = excess_agi / p.phaseout.increment_values

        excess_agi_percentage = p.phaseout.percentage_threshold[excess_agi_step]

        deduction_amount = excess_agi_percentage * p.amount[filing_status]
        
        return max_(0, deduction_amount)
