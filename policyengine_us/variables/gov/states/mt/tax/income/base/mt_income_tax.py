from policyengine_us.model_api import *


class mt_income_tax(Variable):
    value_type = float
    entity = TaxUnit
    label = "Montana income tax"
    unit = USD
    definition_period = YEAR
    defined_for = StateCode.MT

    def formula(tax_unit, period, parameters):
        filing_separately = tax_unit("mt_files_separately", period)
        itax_indiv = add(tax_unit, period, ["mt_income_tax_indiv"])
        itax_joint = tax_unit("mt_income_tax_joint", period)
        income_tax = where(filing_separately, itax_indiv, itax_joint)
        # The 2021 income tax rebate is a one-time payment based on the return's
        # liability. Subtract it here, after the separate-vs-joint election, so
        # it reduces the tax once per return without being clipped per column or
        # changing which election minimizes tax (taxsim #1189).
        rebate = tax_unit("mt_income_tax_rebate", period)
        return income_tax - rebate
