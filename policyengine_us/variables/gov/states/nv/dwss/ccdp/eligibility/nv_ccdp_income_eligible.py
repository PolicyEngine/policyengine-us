from policyengine_us.model_api import *
from policyengine_us.variables.gov.hhs.tax_unit_fpg import fpg


class nv_ccdp_income_eligible(Variable):
    value_type = bool
    entity = SPMUnit
    label = "Eligible for Nevada CCDP based on income"
    definition_period = MONTH
    defined_for = StateCode.NV
    reference = (
        "https://www.dss.nv.gov/siteassets/dwss.nv.gov/content/care/CC_PT_06-25_ANNUAL_INCOME_CHANGES_10.02.2025.pdf#page=1",
        "https://dwss.nv.gov/uploadedFiles/dwssnvgov/content/Care/CC%20PT%2007-23%20Annual%20Income%20Ceiling%20Increase%20(Public%20Distribution).pdf#page=1",
        # PDF pages 50-51
        "https://dwss.nv.gov/uploadedFiles/dwssnvgov/content/Care/Amended%20State%20Plan.pdf#page=50",
        "https://www.dss.nv.gov/siteassets/dwss.nv.gov/content/care/Child_Care_Manual_July_2024.pdf#page=75",
        "https://dwss.nv.gov/uploadedFiles/dwssnvgov/content/Home/Features/2022-2024%20Child%20Care%20PrePrint%20Draft(1).pdf#page=45",
        # PDF pages 1-2
        "https://nwlc.org/wp-content/uploads/2020/02/nevada-childcare-subsidy2019_v1.pdf#page=1",
    )

    def formula(spm_unit, period, parameters):
        p = parameters(period).gov.states.nv.dwss.ccdp
        # MS 316 compares monthly income, rounded to the nearest dollar, with the
        # chart for the household's size.
        countable_income = spm_unit("nv_ccdp_monthly_countable_income", period)
        monthly_smi = spm_unit("nv_ccdp_smi", period)
        enrolled = spm_unit("nv_ccdp_enrolled", period)
        # New applicants face smi_intake and enrolled families face smi_renewal, both
        # dated. From October 1, 2024 they are 41% and 49% of SMI, which match the
        # published charts (CC PT 06-25 and the October 2026 transmittal). From July 1,
        # 2022 through September 2024 both were 85%: the FFY 2022-2024 plan builds the
        # July 2022 limits on the fiscal year 2023 table (smi_year_lag), and CC PT
        # 07-23 prints the October 2023 ceiling. Since October 2024 a separate federal protection
        # (45 CFR 98.21(a)(1)(ii)) bars terminating a family mid-certification until
        # income exceeds 85% SMI, but we don't track certification periods at the
        # moment, so the 85% mid-period ceiling is not modeled.
        # MS 216.4.3.1 (Foster) and MS 216.4.4.1 (CPS) treat a foster or CPS
        # child as a household of one and do NOT count the traditional
        # household's income ("Income received by the traditional household is
        # not countable"). Nevada applies this income exclusion only to
        # foster/CPS children (not to all children), so we don't model it at the
        # moment: a foster/CPS child in a higher-income household may be denied
        # by this income test even though the program would serve them at 100%
        # subsidy. Their copay is still waived and their need-for-care is met via
        # the protective-care pathway in nv_ccdp_copay / nv_ccdp_activity_eligible.
        share = where(enrolled, p.income.smi_renewal, p.income.smi_intake)
        income_limit = monthly_smi * share
        # The charts from October 2024 print each limit as the nearest dollar.
        if p.chart_rounds_to_nearest_dollar:
            income_limit = np.floor(np.round(income_limit, 2) + 0.5)
        fpg_intake = p.income.fpg_intake
        if fpg_intake.in_effect:
            # From October 2018 through June 2022 most new applicants faced 130% of
            # the poverty guideline. Nevada took up each year's guideline on October 1,
            # and the draft FFY 2022-2024 plan prints the October 2020 limits as the
            # nearest dollar ($1,868 a month for two, from $1,867.67). NWLC reports that families
            # with a child in foster care or protective services and homeless
            # families still qualified at 85% of SMI. Families in contracted slots
            # or wrap-around care did too, but we don't track those at the moment.
            year = period.start.year
            program_year = year if period.start.month >= 10 else year - 1
            size = spm_unit("spm_unit_size", period.this_year)
            state_group = spm_unit.household("state_group_str", period.this_year)
            monthly_fpg = (
                fpg(size, state_group, f"{program_year}-10-01", parameters)
                / MONTHS_IN_YEAR
            )
            fpg_limit = np.floor(np.round(monthly_fpg * fpg_intake.rate, 2) + 0.5)
            person = spm_unit.members
            in_protective_care = person("nv_ccdp_eligible_child", period) & (
                person("is_in_foster_care", period)
                | person("receives_or_needs_protective_services", period.this_year)
            )
            is_homeless = spm_unit.household("is_homeless", period.this_year)
            keeps_smi_limit = enrolled | spm_unit.any(in_protective_care) | is_homeless
            income_limit = where(keeps_smi_limit, income_limit, fpg_limit)
        return countable_income <= income_limit
