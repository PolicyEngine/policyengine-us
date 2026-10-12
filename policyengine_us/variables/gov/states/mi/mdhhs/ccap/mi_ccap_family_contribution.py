from policyengine_us.model_api import *
from policyengine_us.variables.gov.states.mi.mdhhs.ccap.mi_ccap_star_rating import (
    MICCAPStarRating,
)
from policyengine_us.variables.gov.states.mi.mdhhs.ccap.mi_ccap_provider_type import (
    MICCAPProviderType,
)


class mi_ccap_family_contribution(Variable):
    value_type = float
    entity = SPMUnit
    unit = USD
    label = "Michigan CDC family contribution per two-week pay period"
    definition_period = MONTH
    defined_for = StateCode.MI
    reference = (
        "https://mdhhs-pres-prod.michigan.gov/olmweb/EX/RF/Public/RFT/270.pdf#page=3",
        "https://mdhhs-pres-prod.michigan.gov/olmweb/ex/BP/Public/BEM/706.pdf#page=2",
    )

    def formula(spm_unit, period, parameters):
        # RFT 270 / BEM 706: the family contribution is a flat dollar amount
        # per child per two-week pay period, based on the family income band,
        # and capped at a per-family limit. It is waived for income-waived
        # children and for income-eligible children at a 3 Star (or higher)
        # provider.
        p = parameters(period).gov.states.mi.mdhhs.ccap
        fc = p.family_contribution
        countable_income = spm_unit("mi_ccap_countable_income", period)
        size = spm_unit("mi_ccap_program_group_size", period)

        # Look up the income band index (0-6) from the per-size scale.
        bands = p.income.scale.band_thresholds
        band = select(
            [
                size == 1,
                size == 2,
                size == 3,
                size == 4,
                size == 5,
                size == 6,
                size == 7,
                size == 8,
                size == 9,
            ],
            [
                bands.size_1.calc(countable_income),
                bands.size_2.calc(countable_income),
                bands.size_3.calc(countable_income),
                bands.size_4.calc(countable_income),
                bands.size_5.calc(countable_income),
                bands.size_6.calc(countable_income),
                bands.size_7.calc(countable_income),
                bands.size_8.calc(countable_income),
                bands.size_9.calc(countable_income),
            ],
            default=bands.size_10.calc(countable_income),
        )
        per_child_fc = fc.per_child[band]
        family_limit = fc.family_limit[band]

        # The family contribution is waived entirely for income-waived groups.
        income_waived = spm_unit("mi_ccap_income_waived", period)

        # BEM 706 / RFT 270 p.3: the contribution is also waived per child when
        # the child attends a licensed provider (center or family/group home) at
        # the star waiver threshold or higher. License-exempt providers have no
        # Great Start to Quality rating, so their income-eligible children
        # always pay regardless of any star rating on the record.
        person = spm_unit.members
        is_eligible_child = person("mi_ccap_eligible_child", period)
        provider_type = person("mi_ccap_provider_type", period)
        is_licensed = provider_type != MICCAPProviderType.LICENSE_EXEMPT
        star_rating = person("mi_ccap_star_rating", period)
        star_level = select(
            [
                star_rating == MICCAPStarRating.STAR_1,
                star_rating == MICCAPStarRating.STAR_2,
                star_rating == MICCAPStarRating.STAR_3,
                star_rating == MICCAPStarRating.STAR_4,
                star_rating == MICCAPStarRating.STAR_5,
            ],
            [1, 2, 3, 4, 5],
        )
        star_waived = is_licensed & (star_level >= fc.star_waiver_threshold)
        child_pays = is_eligible_child & ~star_waived
        num_paying_children = spm_unit.sum(child_pays)
        total_fc = per_child_fc * num_paying_children
        capped_fc = min_(total_fc, family_limit)
        return where(income_waived, 0, capped_fc)
