from policyengine_us.model_api import *
from policyengine_us.variables.gov.hhs.tax_unit_fpg import fpg


class fl_liheap_eligible(Variable):
    value_type = bool
    entity = SPMUnit
    definition_period = YEAR
    label = "Florida LIHEAP regular heating eligibility"
    defined_for = StateCode.FL
    reference = (
        "https://www.law.cornell.edu/uscode/text/42/8624",
        # PDF pages 5, 8, 45
        "https://liheapch.acf.gov/docs/2026/state-plans/FL_Plan_2026.pdf#page=5",
        # PDF pages 4, 23, 39, 41, 43, 47-48, 50-51
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
        # 1200.03A (page 51) and contract G(8)a annualize 30 days of income
        # against it; the portal instead compares one month with monthly
        # maximums rounded to whole dollars, which differ from this annual
        # value by at most $6 a year either way ($2,680 for one person is $5
        # more lenient than 32,155 / 12 = 2,679.58; $3,504 for two is $1
        # stricter).
        limit = np.floor(spm_unit("fl_liheap_income_limit", period) + 0.5)
        state_group = spm_unit.household("state_group_str", period)
        guideline = fpg(size, state_group, period, parameters, year_lag=p.fpg_year_lag)
        # 42 U.S.C. 8624(b)(2)(B), the FY2026 plan assurances (page 45) and
        # contract G(8)e bar excluding a household on income below 110% of the
        # poverty level; from 15 people this floor exceeds the FY2026 limit.
        income_eligible = (income <= limit) | (income < guideline * p_hhs.fpg_floor)
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
        return (
            (size > 0) & (income_eligible | categorical) & responsible & fuel_qualifies
        )
