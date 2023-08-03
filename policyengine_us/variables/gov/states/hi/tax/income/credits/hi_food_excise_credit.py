from policyengine_us.model_api import *


class hi_food_excise_credit(Variable):
    value_type = float
    entity = TaxUnit
    label = "Hawaii food and excise tax credit"
    defined_for = StateCode.HI
    unit = USD
    definition_period = YEAR
    reference = "https://www.capitol.hawaii.gov/hrscurrent/Vol04_Ch0201-0257/HRS0235/HRS_0235-0055_0085.htm"

    def formula(tax_unit, period, parameters):
        # First we need to grab the parameter path
        p = parameters(period).gov.states.hi.tax.income.credits.food_excise_tax
        # Take the tax unit income
        income = tax_unit("adjusted_gross_income", period)
        # Take the filing status
        filing_status = tax_unit("filing_status", period)
        status = filing_status.possible_values
        # Take the number of exemptions
        exemptions = tax_unit("exemptions", period)
        dependent_on_another_return = tax_unit("dsi", period)
        # Determine the amount per exemption based on income
        amount_per_exemption = select(
            [
                filing_status == status.SINGLE,
                filing_status == status.JOINT,
                filing_status == status.HEAD_OF_HOUSEHOLD,
                filing_status == status.SEPARATE,
                filing_status == status.WIDOW,
            ],
            [
                p.amount.single.calc(income),
                p.amount.joint.calc(income),
                p.amount.head_of_household.calc(income),
                p.amount.separate.calc(income),
                p.amount.widow.calc(income),
            ],
        )
        # dsi does not influence minor child's total
        exemption_total = (
            exemptions * amount_per_exemption
        ) * ~dependent_on_another_return

        person = tax_unit.members
        is_child = person("is_child", period)
        minor_child = person("age", period) < p.minor_child.age_threshold

        # add public_support_received
        public_support_received = person("public_support_received", period)
        minor_child_total = p.minor_child.amount * tax_unit.sum(
            is_child & minor_child & public_support_received
        )

        return exemption_total + minor_child_total
