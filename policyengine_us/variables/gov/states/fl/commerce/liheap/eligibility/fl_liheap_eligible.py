from policyengine_us.model_api import *
from policyengine_us.variables.gov.hhs.tax_unit_fpg import fpg


class fl_liheap_eligible(Variable):
    value_type = bool
    entity = SPMUnit
    definition_period = YEAR
    label = "Florida LIHEAP regular home energy eligibility"
    defined_for = StateCode.FL
    reference = (
        "https://www.law.cornell.edu/uscode/text/42/8624#b_2_B",
        "https://www.law.cornell.edu/regulations/florida/Fla-Admin-Code-Ann-R-73C-26-022",
        "https://www.law.cornell.edu/regulations/florida/Fla-Admin-Code-Ann-R-73C-26-023",
        # PDF pages 4-5, 8, 45
        "https://liheapch.acf.gov/docs/2026/state-plans/FL_Plan_2026.pdf#page=4",
        # PDF pages 8-9
        "https://liheapch.acf.gov/docs/2025/state-plans/FL_Plan_2025.pdf#page=8",
        # PDF pages 4, 8, 23, 39, 41, 43, 47-48, 50-51
        "https://liheapch.acf.gov/sites/default/files/webfiles/docs/2023/manuals/FL_PolicyManual_2023.pdf#page=4",
        # PDF pages 12-13
        "https://www.pbcgov.com/pubInf/Agenda/20260106/3E2.pdf#page=12",
    )

    def formula(spm_unit, period, parameters):
        p = parameters(period).gov.states.fl.commerce.liheap.eligibility
        p_hhs = parameters(period).gov.hhs.liheap
        size = spm_unit("fl_liheap_household_size", period)
        income = spm_unit("fl_liheap_countable_income", period)
        # The matrices print the maximum income value in whole dollars. Manual
        # 1200.03A (page 51) and contract G(8)a (page 12) use 30 days of income
        # annualized or the applicant's most current economic situation,
        # "whichever is lower"; annual income stands in for both. The portal
        # instead compares one month with monthly maximums rounded to whole
        # dollars, which differ from this annual value by at most $6 a year
        # either way ($2,680 for one person is $5 more lenient than
        # 32,155 / 12 = 2,679.58; $3,504 for two is $1 stricter).
        limit = np.floor(spm_unit("fl_liheap_income_limit", period) + 0.5)
        state_group = spm_unit.household("state_group_str", period)
        guideline = fpg(size, state_group, period, parameters, year_lag=p.fpg_year_lag)
        # 42 U.S.C. 8624(b)(2)(B) bars excluding a household on income below 110%
        # of the poverty guideline. The 60% SMI limit falls below that floor from
        # household size 15 in FY2026 and the 2027 carry-forward. The FY2026 plan
        # assurances (page 45) and contract G(8)e (page 13) repeat the rule.
        floor = np.round(guideline * p_hhs.fpg_floor, 2)
        income_eligible = (income <= limit) | (income < floor)
        categorical = spm_unit("fl_liheap_categorically_eligible", period)
        heating_expense = spm_unit("heating_expense", period)
        heat_in_rent = spm_unit("heat_expense_included_in_rent", period)
        subsidized = spm_unit("receives_housing_assistance", period) | (
            spm_unit.household("is_in_public_housing", period)
        )
        # The nonsubsidized rent flag represents a verified landlord heating
        # arrangement. Actual verification and account ownership are absent
        # from existing inputs. In subsidized heat-in-rent housing, a positive
        # heating expense represents the household's verified excess charge.
        # Outside rent, has_heating_expense (true by default when the primary
        # fuel's bill is positive) is the obligation, and an explicit false is
        # respected.
        # Source conflict: manual 900.01A (page 39) allows "non-subsidized rent
        # that includes utilities", but 1100.04B(1) (page 47) asks for a
        # landlord statement that "Home energy costs are not included in their
        # rent". This follows 900.01A, 100.01 (page 4) and FY2025 plan item
        # 2.3's utilities-in-rent answer (page 9); the same FY2025 item repeats
        # the landlord statement under Renters (page 8), and the FY2026 plan
        # answers No to all three renter rows (page 8).
        responsible = where(
            heat_in_rent,
            ~subsidized | (heating_expense > 0),
            spm_unit("has_heating_expense", period),
        )
        heating_type = spm_unit("heating_type", period)
        types = heating_type.possible_values
        # An unspecified fuel qualifies only when heat is included in rent.
        fuel_qualifies = (heating_type != types.NONE) & (
            heat_in_rent | (heating_type != types.UNSPECIFIED)
        )
        # The one non-crisis benefit per 12 months (R. 73C-26.022(2)(a)) is a
        # Home Energy benefit for heating or cooling (manual 200 P and Q, page
        # 8), and electricity is a home energy type (R. 73C-26.022(6)). An
        # applicant responsible for all or part of its home heating and cooling
        # costs is eligible (700.01 E, page 23; 900.08 A, page 43). So a
        # household with any reported heating type, including a home without
        # heating or one with heat in subsidized rent, qualifies when it pays
        # its own electricity bill for cooling. UNSPECIFIED does not. Cooling
        # wholly in the rent with no obligation of its own pays nothing, as
        # R. 73C-26.023(4) provides.
        cooling_only = (
            (heating_type != types.UNSPECIFIED)
            & spm_unit("has_cooling_expense", period)
            & (spm_unit("pre_subsidy_electricity_expense", period) > 0)
        )
        return (
            (size > 0)
            & (income_eligible | categorical)
            & ((responsible & fuel_qualifies) | cooling_only)
        )
