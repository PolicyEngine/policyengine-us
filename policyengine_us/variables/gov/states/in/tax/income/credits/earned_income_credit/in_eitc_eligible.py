from policyengine_us.model_api import *
from policyengine_us.variables.gov.states.tax.income.credits.eitc_helpers import (
    calculate_eitc_demographic_eligibility,
    calculate_eitc_like_amount,
)


class in_eitc_eligible(Variable):
    value_type = bool
    entity = TaxUnit
    label = "Indiana earned income tax credit eligibility status"
    unit = USD
    definition_period = YEAR
    reference = "https://iga.in.gov/laws/2021/ic/titles/6#6-3.1-21"
    defined_for = StateCode.IN

    def formula(tax_unit, period, parameters):
        p = parameters(period).gov.states["in"].tax.income
        # check federal eitc receipt
        gets_federal_eitc = tax_unit("eitc", period) > 0
        if not p.credits.earned_income.decoupled:
            return gets_federal_eitc
        if period.start.year >= 2023:
            frozen_eitc = parameters.gov.irs.credits.eitc("2023-01-01")
            child_count = tax_unit("eitc_child_count", period)
            demographic_eligible = calculate_eitc_demographic_eligibility(
                tax_unit, period, frozen_eitc, child_count
            )
            filer_identification_eligible = tax_unit(
                "filer_meets_eitc_identification_requirements", period
            )
            investment_income_eligible = (
                tax_unit("eitc_relevant_investment_income", period)
                <= frozen_eitc.phase_out.max_investment_income
            )
            frozen_federal_eitc = calculate_eitc_like_amount(
                tax_unit,
                period,
                parameters,
                child_count,
                demographic_eligible,
                filer_identification_eligible,
                separate_filer_eligible=frozen_eitc.eligibility.separate_filer,
                eitc_parameters=frozen_eitc,
                investment_income_eligible=investment_income_eligible,
            )
            return frozen_federal_eitc > 0
        # if Indiana EITC is decoupled from federal EITC
        # ... check separate filing status
        filing_status = tax_unit("filing_status", period)
        separate = filing_status == filing_status.possible_values.SEPARATE
        # ... check age eligibility for childless taxpayers
        is_childless = tax_unit("eitc_child_count", period) == 0
        min_age = p.credits.earned_income.childless.min_age
        max_age = p.credits.earned_income.childless.max_age
        age_head = tax_unit("age_head", period)
        age_spouse = tax_unit("age_spouse", period)
        head_age_eligible = (age_head >= min_age) & (age_head <= max_age)
        spouse_age_eligible = (age_spouse >= min_age) & (age_spouse <= max_age)
        married = filing_status == filing_status.possible_values.JOINT
        age_eligible = where(
            married, head_age_eligible | spouse_age_eligible, head_age_eligible
        )
        childless_age_eligible = where(is_childless, age_eligible, True)
        # ... check investment income eligibility
        invinc = tax_unit("eitc_relevant_investment_income", period)
        invinc_limit = p.credits.earned_income.investment_income_limit
        invinc_eligible = invinc <= invinc_limit
        # ... determine Indiana EITC eligibility status
        in_eligible = ~separate & childless_age_eligible & invinc_eligible
        return gets_federal_eitc & in_eligible
