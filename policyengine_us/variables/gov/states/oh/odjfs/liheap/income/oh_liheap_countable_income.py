from policyengine_us.model_api import *


class oh_liheap_countable_income(Variable):
    value_type = float
    entity = SPMUnit
    definition_period = YEAR
    unit = USD
    label = "Ohio HEAP annual countable household income"
    defined_for = StateCode.OH
    reference = (
        # Sections E-2.2-2.3 and Appendix XXIII, pages 7-8 and 73-74.
        "https://irp.cdn-website.com/aa88b0b1/files/uploaded/2022-24%20ATTACHMENT%202022-2023%20EAP%20Guidelines%20%281%29.pdf#page=7",
        # Current income-source checklist, pages 5-6.
        "https://dam.assets.ohio.gov/image/upload/v1769700600/development.ohio.gov/individual/energyassistance/DETAILED_MODEL_PLAN_LIHEAP__10_01_2025.pdf#page=5",
        # Current application deductions and excluded VA disabilities, page 7.
        "https://www.clevelandohio.gov/sites/clevelandohio/files/aging/Home%20repair%20Applications/2025-2026_HEAP_application_B_W.pdf#page=7",
    )

    def formula(spm_unit, period, parameters):
        p = parameters(period).gov.states.oh.odjfs.liheap.income
        person = spm_unit.members
        dependent_minor = (person("age", period) < p.earned_income_min_age) & person(
            "is_tax_unit_dependent", period
        )
        # Tax-unit dependency approximates the policy's dependent-minor test.
        # Keep the existing net business inputs without another expense
        # deduction. Section E-2.3 counts a reported business loss as zero.
        earned = 0
        for source in p.sources.earned:
            earned = earned + max_(person(source, period), 0)
        unearned = 0
        for source in p.sources.unearned:
            unearned = unearned + max_(person(source, period, options=[ADD]), 0)
        # Minor unearned income, including SSA paid through an adult guardian,
        # counts. Nonqualified members' income is not prorated or excluded.
        # Annual inputs represent the 12-month option; a separate favorable
        # 30-day comparison and whole-dollar document processing are not modeled.
        # Existing estate/financial inputs cannot capture all principal payouts,
        # nonretirement investment draws, royalties, or legal settlements.
        # Medicare deductions are deferred. Other premium, spenddown, disability
        # premium, and legal-fee deductions need source/input reconciliation;
        # existing aggregates do not isolate the covered non-Medicare amounts.
        income = spm_unit.sum(earned * ~dependent_minor + unearned)
        child_support_paid = add(spm_unit, period, ["child_support_expense"])
        return max_(income - child_support_paid, 0)
