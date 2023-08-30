from policyengine_us.model_api import *


class az_property_tax_credit(Variable):
    value_type = float
    entity = TaxUnit
    label = "Arizona Property Tax Credit"
    unit = USD
    definition_period = YEAR
    defined_for = StateCode.AZ

    def formula(tax_unit, period, parameters):
        person = tax_unit.members
        p = parameters(period).gov.states.az.tax.income.property_tax_credits
        income = tax_unit("property_tax_credits_income", period)

        age = person("age", period)
        age_qualifies = age >= p.min_age

        head = person('is_tax_unit_head', period)

        filing_status = tax_unit("filing_status", period)
        status = filing_status.possible_values

        property_tax_credits = select(
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

        return head * age_qualifies * property_tax_credits
