from policyengine_us.model_api import *


class az_parents_grandparents_exemption(Variable):
    value_type = float
    entity = TaxUnit
    label = "Arizona parents and grandparents exemption"
    unit = USD
    definition_period = YEAR
    defined_for = StateCode.AZ

    def formula(tax_unit, period, parameters):
        p = parameters(
            period
        ).gov.states.az.tax.income.exemptions.parent_grandparent
        person = tax_unit.members

        parent = person("is_parent_of_filer_or_spouse", period)
        grandparent = person("is_grandparent_of_filer_or_spouse", period)

        age = person("age", period)
        age_eligible = age >= p.min_age

        ratio = person(
            "share_of_care_and_support_costs_paid_by_tax_filer", period
        )
        ratio_eligible = ratio >= p.cost_rate

        total_exemption_count = (
            (parent | grandparent) & age_eligible & ratio_eligible
        )

        return p.amount * tax_unit.sum(total_exemption_count)
