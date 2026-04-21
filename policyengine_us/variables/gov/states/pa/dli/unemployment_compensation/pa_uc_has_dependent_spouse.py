from policyengine_us.model_api import *


class pa_uc_has_dependent_spouse(Variable):
    value_type = bool
    entity = Person
    label = "Has a dependent spouse for Pennsylvania unemployment compensation"
    definition_period = YEAR
    reference = (
        "https://www.pa.gov/content/dam/copapwp-pagov/en/dli/documents/uc/uc_law.pdf#page=159",
    )
    defined_for = StateCode.PA

    def formula(person, period, parameters):
        # § 404(e)(3): a dependent spouse is a legally married spouse who was
        # "living with and being wholly or chiefly supported by" the claimant.
        # Proxy: the claimant is married and the spouse has no employment
        # income (mirrors NJ's dependency allowance logic). A person flagged
        # as a tax-unit dependent cannot be the dependent spouse.
        # Attributed only to the claimant (head of tax unit) to avoid
        # double-counting if multiple adults file UC claims.
        tax_unit = person.tax_unit
        tax_unit_married = tax_unit("tax_unit_married", period)
        is_spouse = tax_unit.members("is_tax_unit_spouse", period)
        is_dep = tax_unit.members("is_tax_unit_dependent", period)
        # Spouse has no employment income and is not also flagged as dependent.
        members_employment = tax_unit.members("employment_income", period)
        spouse_employment = tax_unit.sum(members_employment * is_spouse)
        spouse_is_dependent = tax_unit.sum(is_spouse & is_dep) > 0
        has_dependent_spouse = (
            tax_unit_married & (spouse_employment == 0) & ~spouse_is_dependent
        )
        is_head = person("is_tax_unit_head", period)
        return has_dependent_spouse & is_head
