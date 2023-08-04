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
        # Take the AGI
        income = tax_unit("adjusted_gross_income", period)
        # Minor children receiving public support will receive full credit regardles of AGI
        person = tax_unit.members
        public_support_received = person("public_support_received", period)
        is_child = person("is_child", period)
        minor = person("age", period) < p.minor_child.age_threshold
        eligible_minor_child = is_child & minor & public_support_received
        minor_children = tax_unit.sum(eligible_minor_child)
        minor_child_total = p.minor_child.amount * minor_children
        # Take the number of exemptions
        exemptions = tax_unit("exemptions", period)
        # Reduce number of exemptions by the number of minor children
        claimable_exemptions = exemptions - minor_children
        # Determine the amount per exemption based on income
        # and filing status
        filing_status = tax_unit("filing_status", period)
        status = filing_status.possible_values
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
        exemption_amount = claimable_exemptions * amount_per_exemption
        # Filer can not be a dependent on another return
        dependent_on_another_return = tax_unit("dsi", period)
        return ~dependent_on_another_return * (
            exemption_amount + minor_child_total
        )
