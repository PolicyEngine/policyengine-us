from policyengine_us.model_api import *


class income_tax_before_refundable_credits(Variable):
    value_type = float
    entity = TaxUnit
    definition_period = YEAR
    unit = USD
    label = "Federal income tax before refundable credits"
    documentation = "Income tax liability (including other taxes) after non-refundable credits are used, but before refundable credits are applied"

    def formula(tax_unit, period, parameters):
        if parameters(
            period
        ).gov.contrib.ubi_center.flat_tax.abolish_federal_income_tax:
            return 0
        else:
            added_components = add(
                tax_unit,
                period,
                [
                    "income_tax_before_credits",
                    "net_investment_income_tax",
                    "recapture_of_investment_credit",
                    "unreported_payroll_tax",
                    "qualified_retirement_penalty",
                ],
            )
            subtracted_components = add(
                tax_unit, period, ["income_tax_capped_non_refundable_credits"]
            )
            return added_components - subtracted_components
