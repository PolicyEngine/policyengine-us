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
        p = parameters(period).gov.states.ri.tax.income.exemption

        exemptions_count = tax_unit("exemptions_count", period)

        exemption_amount = exemptions_count * p.amount

        # Modified Federal AGI
        mod_agi = tax_unit("ri_agi", period)

        excess_agi = max_(0, mod_agi - p.reduction.start)

        increments = np.ceil(excess_agi / p.reduction.increment)

        reduction_rate = min_(p.reduction.rate * increments, 1)

        return exemption_amount * (1 - reduction_rate)
