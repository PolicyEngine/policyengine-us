from policyengine_us.model_api import *


class ct_property_tax_credit(Variable):
    value_type = float
    entity = TaxUnit
    label = "Connecticut property tax credit"
    unit = USD
    definition_period = YEAR
    reference = "https://portal.ct.gov/-/media/DRS/Forms/2021/Income/CT-1040-Online-Booklet_1221.pdf#page=30"
    defined_for = "ct_property_tax_credit_eligible"

    def formula(tax_unit, period, parameters):
        agi = tax_unit("ct_agi", period)
        filing_status = tax_unit("filing_status", period)
        p = parameters(period).gov.states.ct.tax.income.credits.property_tax
        real_estate_taxes = add(tax_unit, period, ["real_estate_taxes"])
        max_credit = min_(real_estate_taxes, p.cap)
        excess = max_(agi - p.reduction.start[filing_status], 0)
        total_increments = np.ceil(
            excess / p.reduction.increment[filing_status]
        )
        reduction_percent = p.reduction.rate * total_increments
        reduction_amount = max_credit * reduction_percent
        return max_(max_credit - reduction_amount, 0)
