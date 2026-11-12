from policyengine_us.model_api import *


class commodity_supplemental_food_program_eligible(Variable):
    value_type = bool
    entity = Person
    definition_period = YEAR
    label = "Commodity Supplemental Food Program eligible"

    def formula(person, period, parameters):
        p = parameters(period).gov.usda.csfp
        # CFR defines CSFP income similarly to WIC income.
        # Assume resources are counted at the SPM unit level.
        fpg = person.spm_unit("school_meal_fpg_ratio", period)
        age = person("age", period)

        age_eligible = age >= p.min_age
        federal_income_eligible = fpg <= p.fpg_limit
        tx_income_eligible = person("tx_dta_csfp_income_eligible", period)
        state_code = person.household("state_code", period)
        in_tx = state_code == StateCode.TX
        in_ks = state_code == StateCode.KS
        in_ma = state_code == StateCode.MA
        in_il = state_code == StateCode.IL
        income_eligible = where(in_tx, tx_income_eligible, federal_income_eligible)
        # Kansas CSFP State Plan (effective 2025-04-11), page 4, under the
        # 7 CFR 247.9(b)(1) state option: participation in a listed program
        # bypasses the income limit only. The helper is monthly and
        # participation in any month of the year qualifies. Read each month
        # explicitly: a year read of a monthly boolean takes December only, and
        # an annual aggregate request is not supported under Microsimulation.
        first_month = period.first_month
        ks_monthly_flags = [
            person("ks_dcf_csfp_categorically_eligible", first_month.offset(m))
            for m in range(MONTHS_IN_YEAR)
        ]
        ks_categorically_eligible = np.any(ks_monthly_flags, axis=0)
        income_eligible = income_eligible | ks_categorically_eligible
        ks_county_eligible = person.household("ks_dcf_csfp_county_eligible", period)
        ma_county_eligible = person.household("ma_dese_csfp_county_eligible", period)
        il_county_eligible = person.household("il_dhs_csfp_county_eligible", period)
        county_eligible = select(
            [in_ks, in_ma, in_il],
            [ks_county_eligible, ma_county_eligible, il_county_eligible],
            default=True,
        )
        return age_eligible & income_eligible & county_eligible
