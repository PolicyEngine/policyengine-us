from policyengine_us.model_api import *


class pa_tax_forgiveness_eligible_share(Variable):
    value_type = float
    entity = TaxUnit
    label = "Share of Pennsylvania tax on which tax forgiveness can be claimed"
    documentation = (
        "The share of the return's Pennsylvania income tax that belongs to a "
        "head or spouse who can claim Tax Forgiveness. It is one unless a "
        "filer can be claimed as a dependent on another return. When one "
        "spouse can be claimed, the spouses must file separate Pennsylvania "
        "returns and each spouse's Tax Forgiveness is determined separately, "
        "so it applies only to the tax on the eligible spouse's own income. "
        "Each spouse's tax is approximated by that spouse's share of the "
        "spouses' Pennsylvania taxable income, leaving out amounts recorded "
        "only for the tax unit."
    )
    unit = "/1"
    definition_period = YEAR
    defined_for = StateCode.PA
    reference = (
        # 2025 PA-40 Schedule SP instructions, Section I: "When one spouse is
        # claimed as a dependent on another person's federal income tax
        # return, otherwise qualifying married taxpayers must file separately."
        "https://www.pa.gov/content/dam/copapwp-pagov/en/revenue/documents/formsandpublications/formsforindividuals/pit/documents/2025/2025_pa-40sp.pdf#page=5",
        # "Each spouse's tax forgiveness, if any, must be determined separately."
        "https://www.pa.gov/agencies/revenue/forms-and-publications/pa-personal-income-tax-guide/tax-forgiveness",
    )

    def formula(tax_unit, period, parameters):
        person = tax_unit.members
        filer = person("is_tax_unit_head_or_spouse", period)
        eligible = person("pa_tax_forgiveness_eligible", period)
        # Each filer's own Pennsylvania taxable income: federal gross income
        # less the person-level amounts Pennsylvania does not tax.
        sources = parameters(period).gov.states.pa.tax.income.nontaxable_income_sources
        person_sources = [
            source
            for source in sources
            if tax_unit.entity.get_variable(
                source, check_existence=True
            ).entity.is_person
        ]
        nontaxable = add(person, period, person_sources)
        own = max_(0, person("irs_gross_income", period) - nontaxable) * filer
        total = tax_unit.sum(own)
        eligible_income = tax_unit.sum(own * eligible)
        # With no taxable income there is no tax; split evenly.
        eligible_count = tax_unit.sum(filer & eligible)
        filer_count = max_(tax_unit.sum(filer), 1)
        share = where(
            total > 0,
            eligible_income / where(total > 0, total, 1),
            eligible_count / filer_count,
        )
        filer_is_dependent = tax_unit("head_or_spouse_is_dependent_elsewhere", period)
        return where(filer_is_dependent, share, 1)
