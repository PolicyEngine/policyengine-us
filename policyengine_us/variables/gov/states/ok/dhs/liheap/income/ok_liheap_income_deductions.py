from policyengine_us.model_api import *


class ok_liheap_income_deductions(Variable):
    value_type = float
    entity = Person
    definition_period = YEAR
    unit = USD
    label = "Oklahoma LIHEAP personal income deductions"
    defined_for = StateCode.OK
    reference = (
        # OAC 340:20-1-11(a)(4), (c): these person deductions apply to
        # ineligible-member deeming and eligible members' net income.
        # OAC 340:50-7-31(a)(3)(A)(v)-(vi) lists health insurance and
        # Medicare premiums as allowable medical expenses.
        "https://prod-ok-administrativerules.tecuity.com/api/BlobStorageGetFile?storageContainer=TitleHtml&name=Title_340.html",
        "https://oklahoma.gov/content/dam/ok/en/okdhs/documents/searchcenter/okdhsformresults/c-7.pdf",
    )

    def formula(person, period, parameters):
        p = parameters(period).gov.states.ok.dhs.liheap.income.deductions
        earned = person("ok_liheap_countable_earned_income", period)
        # Annualization assumes earnings and expenses are spread over the
        # year. An unused earned allowance cannot offset unearned income.
        earned_deduction = min_(earned, p.earned_income * MONTHS_IN_YEAR)
        medical_eligible = (person("age", period) >= p.medical_age_threshold) | person(
            "is_disabled", period
        )
        # is_disabled approximates the incorporated SNAP disability test.
        # Countable income nets the Part B premium from Social Security,
        # floored at zero, so only the premium that Social Security does not
        # cover is deducted here; no premium dollar is counted twice.
        part_b_premium = person("medicare_part_b_premium", period)
        social_security = max_(person("social_security", period), 0)
        unnetted_part_b_premium = max_(part_b_premium - social_security, 0)
        other_premiums = max_(
            person("health_insurance_premiums_without_medicare_part_b", period), 0
        )
        other_expenses = max_(person("other_medical_expenses", period), 0)
        medical_expenses = other_expenses + other_premiums + unnetted_part_b_premium
        medical_deduction = medical_expenses * medical_eligible
        child_support = person("child_support_expense", period)
        # The SPM-level actual CCS copay is deducted separately once.
        return earned_deduction + medical_deduction + child_support
