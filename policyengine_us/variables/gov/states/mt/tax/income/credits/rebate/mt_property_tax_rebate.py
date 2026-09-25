from policyengine_us.model_api import *


class mt_property_tax_rebate(Variable):
    value_type = float
    entity = TaxUnit
    label = "Montana property tax rebate"
    unit = USD
    definition_period = YEAR
    reference = "https://mtrevenue.gov/wp-content/uploads/dlm_uploads/2023/12/Form_2_2023_Instructions.pdf#page=5"
    defined_for = StateCode.MT

    def formula(tax_unit, period, parameters):
        # Modeling limitation: this does not encode the statutory eligibility
        # conditions for the rebate (principal residence; at least 7 months of
        # ownership and occupancy during the year; property taxes billed and
        # paid; a timely rebate claim). Revisit if the rebate is ever wired
        # into a benefit-side channel where those conditions would bind.
        p = parameters(period).gov.states.mt.tax.income.credits.rebate.property
        person = tax_unit.members
        mt_property_tax = person("real_estate_taxes", period)
        tax_unit_mt_property_tax = tax_unit.sum(mt_property_tax)
        return min_(p.amount, tax_unit_mt_property_tax)
