from policyengine_us.model_api import *


class ok_liheap_deemed_income(Variable):
    value_type = float
    entity = TaxUnit
    definition_period = YEAR
    unit = USD
    label = "Oklahoma LIHEAP income deemed from ineligible tax unit members"
    defined_for = StateCode.OK
    reference = (
        # OAC 340:20-1-11(a)(4): contribution after personal deductions and
        # need enters eligible members' income before the gross test.
        "https://prod-ok-administrativerules.tecuity.com/api/BlobStorageGetFile?storageContainer=TitleHtml&name=Title_340.html",
        # Schedule IX-A and IX-B.
        # PDF pages 4-5
        "https://oklahoma.gov/content/dam/ok/en/okdhs/documents/searchcenter/okdhsformresults/c-1.pdf#page=4",
    )

    def formula(tax_unit, period, parameters):
        p = parameters(period).gov.states.ok.dhs
        person = tax_unit.members
        ineligible = ~person("ok_liheap_immigration_eligible", period)
        size = tax_unit.sum(ineligible)
        income = tax_unit.sum(person("ok_liheap_countable_income", period) * ineligible)
        deductions = tax_unit.sum(
            person("ok_liheap_income_deductions", period) * ineligible
        )
        # Tax-unit membership within the SPM unit represents the ineligible
        # adult(s) and their co-resident, tax-claimable ineligible dependents.
        # Actual claiming, multiple possible claimants and separate returns
        # can differ. Spouses count as adults, not as tax dependents. Eligible
        # members never enlarge this need group or contribute income here.
        # Existing is_adult (age 18+) approximates the schedule distinction.
        has_adult = tax_unit.any(person("is_adult", period) & ineligible)
        lookup_size = max_(size, 1)
        monthly_need = where(
            has_adult,
            p.tanf.income.need_standard.calc(lookup_size),
            p.liheap.income.deeming.child_only_need_standard.calc(lookup_size),
        )
        need = where(size > 0, monthly_need * MONTHS_IN_YEAR, 0)
        return max_(income - deductions - need, 0)
