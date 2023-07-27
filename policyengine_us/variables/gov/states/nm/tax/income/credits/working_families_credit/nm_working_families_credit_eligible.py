from policyengine_us.model_api import *


class nm_working_families_credit_eligible(Variable):
    value_type = bool
    entity = TaxUnit
    label = "Eligible for New Mexico working families credit"
    definition_period = YEAR
    reference = "https://klvg4oyd4j.execute-api.us-west-2.amazonaws.com/prod/PublicFiles/34821a9573ca43e7b06dfad20f5183fd/856ebf4b-3814-49dd-8631-ebe579d6a42b/Personal%20Income%20Tax.pdf"  # 7-2-18.15
    defined_for = StateCode.NM

    def formula(tax_unit, period, parameters):
        # Eligibility mirrors the federal EITC while
        # allowing for filers aged 18-65 to recieve the credit
        person = tax_unit.members
        has_child = tax_unit("tax_unit_children", period) > 0
        age = person("age", period)
        # Relative parameter reference break branching in some states that
        # modify EITC age limits.
        p = parameters.gov.irs.credits.eitc(period)
        age_eligible = parameters(
            period
        ).gov.states.nm.tax.income.credits.working_families_tax.age_eligibility.calc(
            age
        )
        invinc = tax_unit("eitc_relevant_investment_income", period)
        invinc_disqualified = invinc > p.phase_out.max_investment_income
        demographic_eligible = has_child | tax_unit.any(age_eligible)
        # Define eligibility before considering separate filer limitation.
        eligible = demographic_eligible & ~invinc_disqualified
        # This parameter is true if separate filers are eligible.
        if p.eligibility.separate_filer:
            return eligible
        # If separate filers are not eligible, check if the filer is separate.
        filing_status = tax_unit("filing_status", period)
        separate = filing_status == filing_status.possible_values.SEPARATE
        return eligible & ~separate
