from policyengine_us.model_api import *


class ca_federal_capped_cdcc(Variable):
    value_type = float
    entity = TaxUnit
    label = "Capped child/dependent care credit replicated to include California limitations"
    unit = USD
    definition_period = YEAR
    reference = "https://www.ftb.ca.gov/forms/2020/2020-3506-instructions.html"
    defined_for = StateCode.CA

    def formula(tax_unit, period, parameters):
        cdcc = tax_unit("ca_federal_cdcc", period)
        p = parameters(period).gov.irs.credits
        # follow Credit Limit Worksheet in 2022 Form 2441 instructions:
        itaxbc = tax_unit("income_tax_before_credits", period)  # WS Line1
        # Excess Advance PTC Repayment (Form 8962) assumed zero in above line
        offset = tax_unit("foreign_tax_credit", period)
        # Partner Additional Reporting Year Tax (Form 8978) assumed zero above
        cap = max_(itaxbc - offset, 0)  # WS Line 2
        return min_(cdcc, cap)  # WS Line 3
