from policyengine_us.model_api import *


class nc_lieap_eligible(Variable):
    value_type = bool
    entity = SPMUnit
    definition_period = YEAR
    label = "North Carolina LIEAP regular heating eligibility"
    defined_for = StateCode.NC
    reference = (
        # Section 300.08 (page 9), Section 300.10 A.2.b (pages 15-16) and Section
        # 300.11 (pages 17-18).
        "https://policies.ncdhhs.gov/wp-content/uploads/EP-300-5.1.2026.pdf#page=9",
    )

    def formula(spm_unit, period, parameters):
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
        gross = add(spm_unit, period, ["nc_lieap_gross_income_person", "tanf"])
        gross_eligible = ~nonqualified | (gross / MONTHS_IN_YEAR <= limit)
        # EP-300.08 accepts the applicant's statement of vulnerability. Public
        # heat-in-rent housing requires excess heating charges paid within the
        # prior 12 months at the current address, not merely a positive fuel bill.
        # Section 8 remains a private arrangement. Institutional status and
        # the agency's vendor/account checks are outside this calculation.
        heat = spm_unit("has_heating_expense", period)
        included_rent = spm_unit("heat_expense_included_in_rent", period)
        public_housing = spm_unit.household("is_in_public_housing", period)
        excess_paid = spm_unit("nc_lieap_has_paid_excess_heating_costs", period)
        vulnerable = where(included_rent, public_housing & excess_paid, heat)
        resource_eligible = True
        if p.resource_test:
            # The special population differs from the income limit's on purpose.
            # Section 300.09 (page 10) gives the 150% income limit to households
            # with a member aged 60 or over or a disabled person "receiving
            # services through the Division of Aging and Adult Services", so
            # nc_lieap_income_limit tests age or the DAAS input only. Section
            # 300.11 (page 17) gives the higher resource limit to households
            # "with member aged 60 or older or disabled", with no DAAS
            # condition, so a generally disabled member also qualifies here.
            # The manual does not say whether an ineligible alien can confer
            # either limit. The income limit looks only at members counted in
            # the eligible household size, the unit the Section 300.09 tables
            # are keyed to. The resource test looks at every member because
            # Section 300.11 (page 18) counts ineligible aliens' assets in the
            # household's total resources.
            special = spm_unit.any(
                (person("age", period) >= p.elderly_age)
                | person("is_usda_disabled", period)
                | person("nc_lieap_is_daas_disabled", period)
            )
            resource_limit = where(special, p.special_resource_limit, p.resource_limit)
            # EP-300.11 deducts outstanding withdrawals and already-counted income
            # only from bank accounts; those offsets cannot reduce nonbank cash.
            # Include ineligible members' assets without income-style proration.
            countable_banks = max_(
                person("bank_account_assets", period)
                - max_(person("nc_lieap_bank_account_exclusions", period), 0),
                0,
            )
            nonbank = max_(person("nc_lieap_nonbank_resources", period), 0)
            resource_eligible = (
                spm_unit.sum(countable_banks + nonbank) <= resource_limit
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
