from policyengine_us.model_api import *


class ca_amti_total_adjustments(Variable):
    value_type = float
    entity = TaxUnit
    label = "California total adjustments and preferences for the AMTI calculation"
    defined_for = StateCode.CA
    unit = USD
    definition_period = YEAR
    reference = "https://www.ftb.ca.gov/forms/2022/2022-540-p.pdf"

    def formula(tax_unit, period, parameters):
        p = parameters(period).gov.states.ca.tax.income.alternative_minimum_tax

        # line 14
        return where(
            tax_unit("ca_itemized_deductions", period) > 0,
            add(tax_unit, period, p.amti_sources)
            - tax_unit(
                "ca_standard_deduction", period
            ),  # if itemized, line 1 = 0
            add(
                tax_unit, period, p.amti_sources
            ),  # if not itemized, sum up line 1-6
        )
