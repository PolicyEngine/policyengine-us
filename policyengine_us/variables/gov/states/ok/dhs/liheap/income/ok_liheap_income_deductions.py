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
        # Use the existing nonpremium aggregate without overlapping detailed
        # medical inputs; Medicare/premium treatment remains deferred.
        medical_deduction = (
            max_(person("other_medical_expenses", period), 0) * medical_eligible
        )
        child_support = person("child_support_expense", period)
        # The SPM-level actual CCS copay is deducted separately once.
        return earned_deduction + medical_deduction + child_support
