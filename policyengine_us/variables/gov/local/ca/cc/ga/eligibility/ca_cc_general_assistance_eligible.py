from policyengine_us.model_api import *


class ca_cc_general_assistance_eligible(Variable):
    value_type = bool
    entity = SPMUnit
    label = "Eligible for Contra Costa County General Assistance"
    definition_period = MONTH
    defined_for = "in_cc"
    reference = "https://ehsd.org/aging-and-adult-services/general-assistance/"

    def formula(spm_unit, period, parameters):
        has_eligible_person = (
            add(spm_unit, period, ["ca_cc_general_assistance_eligible_person"]) > 0
        )
        # General Assistance serves adults without dependent children; families
        # with children are directed to CalWORKs. A dependent child is a minor
        # (is_child) who is also a tax-unit dependent. In practice every minor is
        # a tax-unit dependent (only adults can be a tax-unit head or spouse), so
        # this currently equals the count of minor children in the unit.
        person = spm_unit.members
        is_dependent_child = person("is_child", period.this_year) & person(
            "is_tax_unit_dependent", period.this_year
        )
        no_dependent_children = spm_unit.sum(is_dependent_child) == 0
        income_eligible = spm_unit("ca_cc_general_assistance_income_eligible", period)
        return has_eligible_person & no_dependent_children & income_eligible
