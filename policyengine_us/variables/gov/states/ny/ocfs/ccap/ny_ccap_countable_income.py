from policyengine_us.model_api import *


class ny_ccap_countable_income(Variable):
    value_type = float
    entity = SPMUnit
    label = "New York CCAP countable income"
    definition_period = YEAR
    unit = USD
    defined_for = StateCode.NY
    documentation = (
        "New York counts income for Child Care Assistance Program eligibility "
        "and the family share under 18 NYCRR 404.5(b)(5). Count the Family "
        "Assistance the family takes up through ny_ccap_family_assistance. "
        "Count reported Safety Net Assistance amounts and SSI and state "
        "supplements under 404.5(b)(5)(vi). From October 1, 2023, OCFS "
        "excludes children's SSI and state supplements under "
        "404.5(b)(5)(vi) and (b)(6)(xxi); before then, OCFS counted them "
        "for every member under (b)(5)(vi). OCFS uses the child care "
        "services unit under 415.1(l). It separates cohabiting adults "
        "without a common child and treats an 18-year-old as an adult "
        "outside the parent's unit. When children live with no parent, "
        "OCFS counts only the children in their unit. PolicyEngine uses "
        "the SPM unit, which combines those cases. Monthly consumers read "
        "this annual income with the bare period and Core divides it."
    )
    reference = (
        "https://ocfs.ny.gov/programs/childcare/regulations/404-Eligibility.pdf#page=10",
        "https://web.archive.org/web/20220529152858id_/https://ocfs.ny.gov/programs/childcare/regulations/404-Eligibility.pdf#page=10",
        "https://ocfs.ny.gov/main/policies/external/2023/adm/23-OCFS-ADM-18.pdf#page=4",
        "https://dos.ny.gov/system/files/documents/2023/10/101823.pdf#page=7",
        "https://dos.ny.gov/system/files/documents/2024/06/061224.pdf#page=7",
    )

    def formula(spm_unit, period, parameters):
        p = parameters(period).gov.states.ny.ocfs.ccap.income.countable_income
        countable = add(spm_unit, period, p.sources)
        family_assistance = add(spm_unit, period, ["ny_ccap_family_assistance"])
        person = spm_unit.members
        is_child = person("is_child", period)
        # SSI and ny_ssp are monthly. OCFS began excluding children's
        # payments on October 1, 2023, so apply the exclusion month by month.
        ssi = 0
        for month in period.get_subperiods(MONTH):
            p_month = parameters(month).gov.states.ny.ocfs.ccap.income
            child_excluded = p_month.countable_income.child_ssi_exclusion_in_effect
            payments = add(person, month, ["ssi", "ny_ssp"])
            ssi = ssi + where(is_child & child_excluded, 0, payments)
        # 404.5(b)(6)(xiii) excludes the earnings of a dependent child under
        # 18 who is not legally responsible for the child needing care, and
        # directs that no inquiry be made into them. is_child is age under 18.
        excluded_earner = is_child & ~person("is_parent", period)
        excluded_earnings = where(
            excluded_earner, add(person, period, p.earned_sources), 0
        )
        return countable + family_assistance + spm_unit.sum(ssi - excluded_earnings)
