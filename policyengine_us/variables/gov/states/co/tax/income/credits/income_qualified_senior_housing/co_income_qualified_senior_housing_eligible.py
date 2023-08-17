from policyengine_us.model_api import *


class co_income_qualified_senior_housing_eligible(Variable):
    value_type = float
    entity = TaxUnit
    label = "Eligible for Colorado Income Qualified Senior Housing Income Tax Credit"
    unit = USD
    definition_period = YEAR
    reference = (
        "https://tax.colorado.gov/income-qualified-senior-housing-income-tax-credit",
        "https://tax.colorado.gov/sites/tax/files/documents/DR_104_Book_2022.pdf#page=17",
    )
    defined_for = StateCode.CO

    def formula(tax_unit, period, parameters):
        p = parameters(
            period
        ).gov.states.co.tax.income.credits.income_qualified_senior_housing

        filing_status = tax_unit("filing_status", period)
        filing_statuses = filing_status.possible_values
        single = filing_status == filing_statuses.SINGLE
        joint = filing_status == filing_statuses.JOINT
        hoh = filing_status == filing_statuses.HEAD_OF_HOUSEHOLD
        widow = filing_status == filing_statuses.WIDOW
        separate = filing_status == filing_statuses.SEPARATE

        age_head = tax_unit("age_head", period)
        age_spouse = tax_unit("age_spouse", period)
        # WILL BE DELETED LATER
        # select(
        #     [
        #         single,
        #         hoh,
        #         widow,
        #         separate,
        #         joint,
        #     ],
        #     [
        #         0,
        #         0,
        #         0,
        #         tax_unit("age_spouse", period),
        #         tax_unit("age_spouse", period),
        #     ],
        # )

        birth_year_head = period.start.year - age_head
        birth_year_spouse = period.start.year - age_spouse

        head_eligible = birth_year_head <= p.birth_year_limit
        spouse_eligible = birth_year_spouse <= p.birth_year_limit
        age_eligible = head_eligible | spouse_eligible

        # Second condition (considered TRUE automatically)
        # Were you (or was your spouse) a full-year or part-year resident of Colorado for 2022?

        agi = tax_unit("adjusted_gross_income", period)
        max_income = p.income_threshold
        agi_eligible = agi <= max_income

        # May need Pavel to check on condition FOUR using the second reference link.
        # Gonna check back after discussion.

        return age_eligible & agi_eligible
