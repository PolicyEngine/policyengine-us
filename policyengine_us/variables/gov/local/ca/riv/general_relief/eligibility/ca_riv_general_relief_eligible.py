from policyengine_us.model_api import *


class ca_riv_general_relief_eligible(Variable):
    value_type = bool
    entity = SPMUnit
    label = "Eligible for the Riverside County General Relief"
    definition_period = MONTH
    defined_for = "in_riv"

    def formula(spm_unit, period, parameters):
        p = parameters(period).gov.local.ca.riv.general_relief
        age = spm_unit.members("monthly_age", period)
        # Adults with dependent children under certain age are NOT eligible for GA.
        # They should apply for CalWORKs (California's TANF) instead.
        age_eligible = spm_unit.all(age >= p.age_threshold)

        immigration_status_eligible = (
            add(
                spm_unit,
                period,
                ["ca_riv_general_relief_immigration_status_eligible"],
            )
            > 0
        )
        meets_work_requirements = (
            add(
                spm_unit,
                period,
                ["ca_riv_general_relief_meets_work_requirements"],
            )
            > 0
        )
        property_eligible = spm_unit(
            "ca_riv_general_relief_property_eligible", period
        )
        income_eligible = spm_unit(
            "ca_riv_general_relief_income_eligible", period
        )

        return (
            age_eligible
            & immigration_status_eligible
            & property_eligible
            & income_eligible
            & meets_work_requirements
        )
