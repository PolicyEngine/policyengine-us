from policyengine_us.model_api import *


class hi_food_excise_exemption_amount(Variable):
    value_type = float
    entity = TaxUnit
    label = "Exemption amount for the hawaii food excise credit"
    definition_period = YEAR
    defined_for = StateCode.HI

    def formula(tax_unit, period, parameters):
        p = parameters(period).gov.states.hi.tax.income.credits.food_excise_tax

        person = tax_unit.members
        public_support_over_half = person(
            "hi_food_excise_credit_child_receiving_public_support", period
        )
        is_child = person("is_child", period)
        minor = person("age", period) < p.minor_child.age_threshold
        eligible_minor_child = is_child & minor & public_support_over_half
        minor_children = tax_unit.sum(eligible_minor_child)

        income = tax_unit("adjusted_gross_income", period)
        # Count exemptions as number of people.
        # The legal code defines exemptions as Hawaii exemptions,
        # which normally include additional exemptions for aged and disabled people,
        # but excludes those additional exemptions for this program.
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

        return claimable_exemptions * amount_per_exemption
