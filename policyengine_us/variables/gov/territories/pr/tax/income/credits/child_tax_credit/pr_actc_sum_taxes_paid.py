from policyengine_us.model_api import *


class pr_actc_sum_taxes_paid(Variable):
    value_type = int
    entity = TaxUnit
    label = ""
    definition_period = YEAR
    reference = ""

    def formula(tax_unit, period, parameters):
        total = 0.5 * person("self_employment_tax", period) + 0.5 * tax_unit("additional_medicare_tax", period) + tax_unit("pr_withheld_income", period)
