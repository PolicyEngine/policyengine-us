from policyengine_us.model_api import *


class ca_amti_adjustments(Variable):
    value_type = float
    entity = TaxUnit
    label = "California AMTI adjustment"
    defined_for = StateCode.CA
    unit = USD
    definition_period = YEAR
    reference = "https://www.ftb.ca.gov/forms/2022/2022-540-p.pdf"

    def formula(tax_unit, period, parameters):
        # Line 1 -14
        p = parameters(period).gov.states.ca.tax.income.amt
        itemized_ded = tax_unit("ca_itemized_deductions", period)
        standard_ded = tax_unit("ca_standard_deduction", period)
        # Assuming that tax filer claimed itemized deducions if above standard ded amount
        itemizes = itemized_ded > standard_ded
        itemized_sources = add(tax_unit, period, p.amti.sources)
        # Line 6
        deductions = where(itemizes, itemized_sources, standard_ded)
        # Line 7
        investment_ded = tax_unit("ca_investment_interest_deduction", period)
        # line 14
        return investment_ded + deductions
