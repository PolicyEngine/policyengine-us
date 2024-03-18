from policyengine_us.model_api import *


class oh_lump_sum_retirement_credit_eligible(Variable):
    value_type = bool
    entity = TaxUnit
    label = "Eligible for the Ohio lump sum retirement income credit"
    definition_period = YEAR
    reference = "https://tax.ohio.gov/static/forms/ohio_individual/individual/2021/pit-it1040-booklet.pdf#page=20"
    defined_for = StateCode.OH

    def formula(tax_unit, period, parameters):
        p = parameters(
            period
        ).gov.states.oh.tax.income.credits.retirement.lump_sum
        modified_agi = tax_unit("oh_modified_agi", period)
        distribution_received = (
            tax_unit("form_4972_lumpsum_distributions", period) > 0
        )
        agi_eligible = modified_agi < p.income_limit
        return distribution_received & agi_eligible
