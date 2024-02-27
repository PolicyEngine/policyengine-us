from policyengine_us.model_api import *


class ri_standard_deduction_applicable_percentage(Variable):
    value_type = float
    entity = TaxUnit
    label = "Rhode Island standard deduction applicable percentage"
    unit = USD
    definition_period = YEAR
    reference = (
        "https://tax.ri.gov/sites/g/files/xkgbur541/files/2021-11/2021-tax-rate-and-worksheets.pdf"
        "https://tax.ri.gov/sites/g/files/xkgbur541/files/2022-12/2022%20Tax%20Rate%20and%20Worksheets.pdf"
    )
    defined_for = StateCode.RI

    def formula(tax_unit, period, parameters):
        p = parameters(
            period
        ).gov.states.ri.tax.income.deductions.standard.phase_out

        agi = tax_unit("ri_agi", period)

        excess_agi = max_(agi - p.start, 0)

        excess_agi_step = np.ceil(excess_agi / p.increment)

        return max_(1 - p.percentage * excess_agi_step, 0)
