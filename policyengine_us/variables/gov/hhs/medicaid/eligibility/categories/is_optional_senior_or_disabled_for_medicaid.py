from policyengine_us.model_api import *


class is_optional_senior_or_disabled_for_medicaid(Variable):
    value_type = bool
    entity = Person
    label = "Seniors or disabled people not meeting SSI rules"
    documentation = (
        "Whether this person can claim Medicaid through the State's optional pathway "
        "for seniors or people with disabilities."
    )
    definition_period = YEAR
    reference = "https://www.law.cornell.edu/uscode/text/42/1396a#m"

    def formula(person, period, parameters):
        # ── Gather income & assets ───────────────────────────────────────────────
        personal_income = person("ssi_countable_income", period)  # annual $
        personal_assets = person("ssi_countable_resources", period)  # $ stock
        tax_unit = person.tax_unit
        income = tax_unit.sum(
            personal_income
        )  # annual $ (individual or couple)
        assets = tax_unit.sum(personal_assets)

        # ── Flags & state info ──────────────────────────────────────────────────
        is_senior_or_disabled = person("is_ssi_aged_blind_disabled", period)
        is_joint = person.tax_unit("tax_unit_is_joint", period)  # bool
        state = person.household("state_code_str", period)
        state_group = person.household(
            "state_group_str", period
        )  # CONTIGUOUS_US / AK / HI

        # --- Parameters -----------------------------------------------------------
        ma = parameters(
            period
        ).gov.hhs.medicaid.eligibility.categories.senior_or_disabled
        fpg = parameters(period).gov.hhs.fpg  # this is the node you showed

        # 1️⃣ Income disregard  (stored monthly → convert to annual)
        income_disregard = where(
            is_joint,
            ma.income.disregard.couple[state] * MONTHS_IN_YEAR,
            ma.income.disregard.individual[state] * MONTHS_IN_YEAR,
        )

        # pull the 1‑person line directly
        fpg_1 = fpg.first_person[state_group]

        # build the 2‑person line: first + additional
        fpg_2 = (
            fpg.first_person[state_group] + fpg.additional_person[state_group]
        )

        # percent‑of‑FPG limit
        limit_pct = where(
            is_joint,
            ma.income.limit.couple[state],
            ma.income.limit.individual[state],
        )

        # choose 1‑ vs 2‑person poverty guideline
        fpg_annual = where(is_joint, fpg_2, fpg_1)
        income_limit = limit_pct * fpg_annual

        income_limit = limit_pct * fpg_annual  # annual $ cap

        # 3️⃣ Asset limit (unchanged, still a fixed $ stock)
        asset_limit = where(
            is_joint,
            ma.assets.limit.couple[state],
            ma.assets.limit.individual[state],
        )

        # ── Eligibility test ───────────────────────────────────────────────────
        under_limits = (income - income_disregard < income_limit) & (
            assets < asset_limit
        )
        return is_senior_or_disabled & under_limits
