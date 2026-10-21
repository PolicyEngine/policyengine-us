from policyengine_us.model_api import *


class ok_liheap_income_deductions(Variable):
    value_type = float
    entity = Person
    definition_period = YEAR
    unit = USD
    label = "Oklahoma LIHEAP personal income deductions"
    defined_for = StateCode.OK
    reference = (
        # OAC 340:20-1-11(a)(4), (c), 340:50-5-4 and 340:50-7-31(a)(3)(A)(v)-(vi):
        # these person deductions apply to ineligible-member deeming and
        # eligible members' net income.
        "https://prod-ok-administrativerules.tecuity.com/api/BlobStorageGetFile?storageContainer=TitleHtml&name=Title_340.html",
        "https://oklahoma.gov/content/dam/ok/en/okdhs/documents/searchcenter/okdhsformresults/c-7.pdf",
    )

    def formula(person, period, parameters):
        p = parameters(period).gov.states.ok.dhs.liheap.income.deductions
        earned = person("ok_liheap_countable_earned_income", period)
        # Annualization assumes earnings and expenses are spread over the
        # year. An unused earned allowance cannot offset unearned income.
        earned_deduction = min_(earned, p.earned_income * MONTHS_IN_YEAR)
        # OAC 340:20-1-11(c)(1) deducts medical expenses of "persons 60 years of
        # age and older or persons considered disabled, per OAC 340:50-5-4".
        # 340:50-5-4(a) restates the 7 CFR 271.2 elderly or disabled member: age
        # 60 ((a)(1), is_usda_elderly) or benefit receipt (is_usda_disabled). The
        # veteran flags that is_usda_disabled reads stand in for (a)(6)-(9), so an
        # aid-and-attendance or housebound veteran ((a)(7)) is entered as
        # is_permanently_disabled_veteran. Categories with no input ((a)(3)-(5)
        # and (a)(10)-(11), such as government disability retirement and interim
        # assistance) are not modeled.
        medical_eligible = person("is_usda_elderly", period) | person(
            "is_usda_disabled", period
        )
        # Allowable expenses follow SNAP's list in 340:50-7-31(a)(3)(A), applied
        # by analogy and without its $35 threshold: health premiums paid after
        # tax or through payroll, the whole Medicare Part B premium, and other
        # medical costs. The Part B premium counts only for a member with
        # medicare_enrolled, and a nonzero health_insurance_premiums input
        # replaces the non-Medicare and Part B split.
        medical_expenses = max_(person("snap_allowable_medical_expenses", period), 0)
        medical_deduction = medical_expenses * medical_eligible
        child_support = person("child_support_expense", period)
        # The SPM-level actual CCS copay is deducted separately once.
        return earned_deduction + medical_deduction + child_support
