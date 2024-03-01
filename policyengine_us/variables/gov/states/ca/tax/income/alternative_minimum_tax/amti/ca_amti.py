from policyengine_us.model_api import *


class ca_amti(Variable):
    value_type = float
    entity = TaxUnit
    label = "California alternative minimum taxable income"
    defined_for = StateCode.CA
    unit = USD
    definition_period = YEAR
    reference = "https://www.ftb.ca.gov/forms/2022/2022-540-p.pdf"

    def formula(tax_unit, period, parameters):
        filing_status = tax_unit("filing_status", period)
        p = parameters(period).gov.states.ca.tax.income.amt.exemption
        p_us = parameters(period).gov.irs.income.amt.capital_gains

        amti_before_ded = tax_unit("ca_pre_exemption_amti", period)
        separate = filing_status == filing_status.possible_values.SEPARATE
        # Calculation from Schedule 540 P Line 21 Separate calculation
        # line 1 - total amti
        # Line 2
        maximum_exemption = p.amti.threshold.upper[filing_status]
        # Line 3
        reduced_amti = max_(amti_before_ded - maximum_exemption, 0)
        # Line 4
        reduced_amti_rate = reduced_amti * p_us.capital_gain_excess_tax_rate
        # Line 5
        separate_amti_calc = min_(reduced_amti_rate, p.amount[filing_status])

        # line 21
        separate_amti_eligible = separate & (reduced_amti > 0)
        separate_amti = separate_amti_eligible * separate_amti_calc
        return amti_before_ded + separate_amti
