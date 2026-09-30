from policyengine_us.model_api import *


class nc_lieap_eligible(Variable):
    value_type = bool
    entity = SPMUnit
    definition_period = YEAR
    label = "North Carolina LIEAP regular heating eligibility"
    defined_for = StateCode.NC
    reference = "https://policies.ncdhhs.gov/wp-content/uploads/EP-300-5.1.2026.pdf#page=9,15,16,17,18"

    def formula_2026(spm_unit, period, parameters):
        p = parameters(period).gov.states.nc.ncdhhs.lieap
        person = spm_unit.members
        size = spm_unit("nc_lieap_household_size", period)
        limit = np.floor(
            spm_unit("nc_lieap_income_limit", period) / MONTHS_IN_YEAR + 0.5
        )
        income = spm_unit("nc_lieap_income", period) / MONTHS_IN_YEAR
        # Non-qualified members' income must first pass an unprorated gross test
        # using eligible household size (300.10 A.2.b), before the net proration.
        nonqualified = spm_unit.any(~person("is_citizen_or_legal_immigrant", period))
        sources = parameters(period).gov.usda.snap.income.sources.unearned_spm_unit
        gross = add(spm_unit, period, ["nc_lieap_gross_income_person"]) + add(
            spm_unit, period, sources
        )
        gross_eligible = ~nonqualified | (gross / MONTHS_IN_YEAR <= limit)
        # Positive heat costs approximate a separate bill. For public housing with
        # heat in rent, a positive reported heat bill approximates an excess charge.
        # Private heat-in-rent households do not qualify. Institutions, utility
        # account ownership, and the exact public-housing excess history are gaps.
        heat = spm_unit("heating_expense", period) > 0
        included_rent = spm_unit("heat_expense_included_in_rent", period)
        public_housing = spm_unit.household("is_in_public_housing", period)
        vulnerable = heat & (~included_rent | public_housing)
        resource_eligible = True
        if p.resource_test:
            special = spm_unit.any(
                (person("age", period) >= p.elderly_age)
                | person("is_usda_disabled", period)
            )
            resource_limit = where(special, p.special_resource_limit, p.resource_limit)
            # Bank balances approximate the countable cash/checking/savings total;
            # cash on hand and offsets for income already counted are not available.
            resource_eligible = (
                add(spm_unit, period, ["bank_account_assets"]) <= resource_limit
            )
        # The plan marks SNAP categorical eligibility but does not define a waiver
        # of the manual's financial tests. Automatic reenrollment/prior-year awards,
        # tribal administration, and discretionary supplements are not modeled.
        return (
            (size > 0)
            & (income <= limit)
            & gross_eligible
            & vulnerable
            & resource_eligible
        )
