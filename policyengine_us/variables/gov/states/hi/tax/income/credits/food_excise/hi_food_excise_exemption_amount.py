from policyengine_us.model_api import *


class hi_food_excise_exemption_amount(Variable):
    value_type = float
    entity = TaxUnit
    label = "Exemption amount for Hawaii Food/Excise Tax Credit"
    definition_period = YEAR
    defined_for = StateCode.HI

    def formula(tax_unit, period, parameters):
        p = parameters(period).gov.states.hi.tax.income.credits.food_excise_tax

        income = tax_unit("adjusted_gross_income", period)
        # Count exemptions as number of people
        #   The legal code defines exemptions as Hawaii exemptions,
        #   which normally include additional exemptions for aged and
        #   disabled people, but excludes those additional exemptions
        #   for this program.
        exemptions = tax_unit("exemptions_count", period)
        # Reduce number of exemptions by the number of minor children
        minor_children = tax_unit(
            "hi_food_excise_credit_minor_child_count", period
        )
        claimable_exemptions = exemptions - minor_children
        # Determine amount per exemption based on income and filing status
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
