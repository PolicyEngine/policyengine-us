from policyengine_us.model_api import *
from numpy import ceil


class ri_exemptions(Variable):
    value_type = float
    entity = TaxUnit
    label = "Rhode Island exemptions"
    unit = USD
    definition_period = YEAR
    reference = "https://tax.ri.gov/sites/g/files/xkgbur541/files/2022-12/2022%20Tax%20Rate%20and%20Worksheets.pdf"
    defined_for = StateCode.RI

    def formula(tax_unit, period, parameters):
        p = parameters(period).gov.states.ri.tax.income.exemption

        exemptions = tax_unit("exemptions", period)

        exemption_amount = exemptions * p.amount

        agi = tax_unit("ri_agi", period)

        excess_agi = max_(0, agi - p.reduction.start)

        increments = ceil(excess_agi / p.reduction.increment)

        percent_reduction = min_(p.reduction.percentage * increments, 1)

        return exemption_amount * (1 - percent_reduction)
