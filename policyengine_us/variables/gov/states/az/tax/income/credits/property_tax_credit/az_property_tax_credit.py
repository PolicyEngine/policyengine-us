from policyengine_us.model_api import *


class az_property_tax_credit(Variable):
    value_type = float
    entity = TaxUnit
    label = "Arizona Property Tax Credit"
    unit = USD
    definition_period = YEAR
    defined_for = "az_property_tax_credit_eligible"

    def formula(tax_unit, period, parameters):
        person = tax_unit.members
        p = parameters(period).gov.states.az.tax.income.property_tax_credits
        income = tax_unit("az_property_tax_credit_income", period)

        filing_status = tax_unit("filing_status", period)
        status = filing_status.possible_values

        return select(
            [
                filing_status == status.SINGLE,
                filing_status == status.HEAD_OF_HOUSEHOLD,
                filing_status == status.JOINT,
                filing_status == status.SEPARATE,
                filing_status == status.WIDOW,
            ],
            [
                p.amount.single.calc(income),
                p.amount.head_of_household.calc(income),
                p.amount.joint.calc(income),
                p.amount.separate.calc(income),
                p.amount.widow.calc(income),
            ],
        )

        return property_tax_credits
