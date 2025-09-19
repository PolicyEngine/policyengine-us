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

        minor_child_include = p.minor_child.in_effect
        # Count exemptions as number of people
        #   The legal code defines exemptions as Hawaii exemptions,
        #   which normally include additional exemptions for aged and
        #   disabled people, but excludes those additional exemptions
        #   for this program.
        # Determine amount per exemption based on income and filing status
        filing_status = tax_unit("filing_status", period)
        amount_per_exemption = select_filing_status_value(
            filing_status, p.amount, income
        )
        exemptions = tax_unit("exemptions_count", period)
        if p.minor_child.in_effect:
            # Reduce number of exemptions by the number of minor children
            minor_children = tax_unit(
                "hi_food_excise_credit_minor_child_count", period
            )
            claimable_exemptions = exemptions - minor_children
        else:
            claimable_exemptions = exemptions
        return claimable_exemptions * amount_per_exemption
