from policyengine_us.model_api import *


class de_elder_disabled_income_exclusion(Variable):
    value_type = float
    entity = TaxUnit
    label = "Delaware blind or disabled exemption"
    unit = USD
    definition_period = YEAR   
    defined_for = StateCode.DE

    def formula(tax_unit, period, parameters):
        # First get their filing status.
        filing_status = tax_unit("filing_status", period)

        # Determine whether spouse is eligible.
        # single = filing_status == filing_status.possible_values.SINGLE
        # separate = filing_status == filing_status.possible_values.SEPARATE

        # Then get the DE blind ir disabled exemptions part of the parameter tree.
        p = parameters(period).gov.states.de.tax.income.substractions.elderly_disabled

        # Get the individual disabled status.
        disabled_head = tax_unit("disabled_head", period)

        # Get the individual filer's age.
        # age_head = tax_unit("age_head", period)

        # Determine if individual age is eligible.
        # age_head_eligible = (age_head >= p.aged).astype(int)

        # Get the individual filer's income.
        income_head = tax_unit("income_head", period)

        # Determine if filer income is eligible.
        income_threshod = p.minimum_income[filing_status]
        income_head_eligible = (income_head <= income_threshod).astype(int)

        # Get the individual filer's substraction result from Line 10.
        # substraction_head = tax_unit("substraction_head", period)

        # Determine if head of household (filer) is eligible.
        # substraction_head_eligible = (substraction_head <= p.substrsaction_result).astype(int)

        # Check if the individual's eligiblity.
        head_eligible = (disabled_head | income_head_eligible).astype(int)
        # head_eligible = (disabled_head | age_head_eligible | income_head_eligible | substraction_head_eligible).astype(int)

        # Calculate total blind exemption.
        return head_eligible * p.exclusion_amount[filing_status]
