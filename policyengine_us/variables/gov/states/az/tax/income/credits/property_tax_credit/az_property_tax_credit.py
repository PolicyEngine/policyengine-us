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
        income = tax_unit("adjusted_gross_income", period)

        age = person("age", period)
        age_qualifies = age >= p.min_age

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
                p.single.calc(income),
                p.household.calc(income),
                p.joint.calc(income),
                p.separate.calc(income),
                p.widow.calc(income),
            ],
        )

        return age_qualifies * property_tax_credits
