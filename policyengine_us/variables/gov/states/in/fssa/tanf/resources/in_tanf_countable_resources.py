from policyengine_us.model_api import *


class in_tanf_countable_resources(Variable):
    value_type = float
    entity = SPMUnit
    label = "Indiana TANF countable resources"
    unit = USD
    definition_period = MONTH
    defined_for = StateCode.IN
    reference = (
        "https://www.in.gov/fssa/dfr/tanf-cash-assistance/about-tanf/",
        "https://iga.in.gov/laws/2023/ic/titles/12",
        "https://casetext.com/regulation/indiana-administrative-code/title-470-division-of-family-resources/article-103-tanf-program",
    )

    def formula(spm_unit, period, parameters):
        p = parameters(period).gov.states["in"].fssa.tanf.resources

        # Start with total SPM unit assets
        # Note: This includes liquid assets like cash, bank accounts, stocks, bonds
        total_assets = spm_unit("spm_unit_assets", period.this_year)

        # Get household vehicle value (annualized)
        vehicle_value = spm_unit.household(
            "household_vehicles_value", period.this_year
        )

        # Vehicle exclusion per 470 IAC 10.3-3-6
        # One vehicle is excluded up to equity value limit
        # Indiana excludes one vehicle up to $20,000 in equity
        excluded_vehicle_value = min_(
            vehicle_value, p.vehicle_equity_exclusion
        )

        # Calculate countable resources
        # Total assets already includes vehicles, so subtract the excluded portion
        return max_(total_assets - excluded_vehicle_value, 0)
