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
        # Tax-unit dependency approximates the policy's dependent-minor test.
        dependent_minor = (person("age", period) < p.adult_age) & person(
            "is_tax_unit_dependent", period
        )
        # Keep the existing net business inputs without another expense
        # deduction. Section E-2.3 counts a reported business loss as zero, and
        # each source is floored at zero so a loss in one source cannot offset
        # another.
        income = 0
        for sources in [p.sources.earned, p.sources.unearned]:
            for source in sources:
                income = income + max_(person(source, period, options=[ADD]), 0)
        # Guidelines E-2.2 (page 7) count the income of members 18 or older and
        # a minor's SS/SSDI paid to an adult payee; a child's SSI and other
        # income are not counted. The FY2026 plan (page 6) excludes only
        # "Earned income of a child under the age of 18"; the Guidelines govern.
        social_security = max_(person("social_security", period), 0)
        counted = where(dependent_minor, 0, income) + social_security
        # Nonqualified members' income is not prorated or excluded. Annual
        # inputs represent the 12-month option; a separate favorable 30-day
        # comparison and whole-dollar document processing are not modeled.
        # Existing estate/financial inputs cannot capture all principal payouts,
        # nonretirement investment draws, royalties, or legal settlements.
        # Guidelines Appendix XXIII (page 74) and the application (page 7)
        # deduct child support paid and health, dental, vision, prescription
        # plan, and Medicare premiums; the FY2026 plan (page 6) counts Social
        # Security "Excluding MediCare deduction". The non-Part-B premium input
        # excludes the Part B premium, so no premium is deducted twice.
        # Spenddown, disability premium, and legal-fee deductions have no input.
        deductions = add(
            spm_unit,
            period,
            [
                "child_support_expense",
                "health_insurance_premiums_without_medicare_part_b",
                "medicare_part_b_premium",
            ],
        )
        return max_(spm_unit.sum(counted) - deductions, 0)
