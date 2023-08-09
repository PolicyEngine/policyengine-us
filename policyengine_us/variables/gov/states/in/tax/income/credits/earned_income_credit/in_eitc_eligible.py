from policyengine_us.model_api import *


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
        gets_federal_eitc = tax_unit("earned_income_tax_credit", period) > 0
        if not p.credits.earned_income.decoupled:
            return gets_federal_eitc
        # if Indiana EITC is decoupled from federal EITC
        # ... check separate filing status
        filing_status = tax_unit("filing_status", period)
        separate = filing_status.possible_values.SEPARATE
        # ... check age eligibility for childless taxpayers
        is_childless = tax_unit("eitc_child_count", period) == 0
        age_head = tax_unit("age_head", period)
        age_spouse = tax_unit("age_spouse", period)
        married = filing_status.possible_values.JOINT
        head_age_eligible = (age_head >= 25) & (age_head <= 64)
        spouse_age_eligible = (age_spouse >= 25) & (age_spouse <= 64)
        childless_age_eligible = where(
            is_childless, head_age_eligible | spouse_age_eligible, True
        )
        # ... check investment income eligibility
        invinc = tax_unit("eitc_relevant_investment_income", period)
        invinc_eligible = invinc <= 3800
        # ... determine Indiana EITC eligibility status
        in_eligible = ~separate & childless_age_eligible & invinc_eligible
        return gets_federal_eitc & in_eligible
