from policyengine_us.model_api import *


class az_senior_exemption(Variable):
    value_type = float
    entity = TaxUnit
    label = "Arizona senior exemption"
    unit = USD
    definition_period = YEAR
    defined_for = StateCode.AZ

    def formula(tax_unit, period, parameters):
        p = parameters(period).gov.states.az.tax.income.exemptions

        payment_eligible = (
            tax_unit("care_and_support_payment", period) > p.min_payment
        )
        eligibility = payment_eligible.astype(int)

        return p.amount.senior * eligibility
