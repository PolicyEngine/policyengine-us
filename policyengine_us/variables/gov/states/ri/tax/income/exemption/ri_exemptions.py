from policyengine_us.model_api import *


class ri_exemptions(Variable):
    value_type = float
    entity = TaxUnit
    label = "Rhode Island exemptions"
    unit = USD
    definition_period = YEAR
    reference = "https://tax.ri.gov/sites/g/files/xkgbur541/files/2022-12/2022%20Tax%20Rate%20and%20Worksheets.pdf"
    defined_for = StateCode.RI

    def formula(tax_unit, period, parameters):
        p = parameters(period).gov.states.ri.tax.income.exemption.phase_out

        exemptions = tax_unit("tax_unit_size", period)

        exemptions_amount = exemptions * p.amount

        agi = tax_unit("adjusted_gross_income", period)

        excess_agi = agi - p.start

        excess_agi_step = excess_agi / p.reduction.increment

        return p.reduction.percentage.calc(excess_agi_step) * exemptions_amount
