from policyengine_us.model_api import *


class va_refundable_eitc_if_claimed(Variable):
    value_type = float
    entity = TaxUnit
    label = "Virginia refundable earned income tax credit if claimed"
    unit = USD
    definition_period = YEAR
    reference = "https://www.tax.virginia.gov/sites/default/files/vatax-pdf/2022-760-instructions.pdf#page=32"
    defined_for = StateCode.VA

    def formula(tax_unit, period, parameters):
        federal_eitc = tax_unit("eitc", period)
        p = parameters(period).gov.states.va.tax.income.credits.eitc.match
        # Va. Code 58.1-339.8(B)(1): the credit "shall not be allowed against
        # such tax of a dependent"; as for the low-income credit, either
        # spouse being claimed bars a joint return.
        dependent_filer = tax_unit("head_or_spouse_is_dependent_elsewhere", period)
        return where(dependent_filer, 0, p.refundable * federal_eitc)
