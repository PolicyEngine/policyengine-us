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
        "and the family share under 18 NYCRR 404.5(b)(5). Count Family "
        "Assistance through ny_tanf, with TANF take-up and abolition controls, "
        "to avoid other states' dependent care deductions in the federal "
        "TANF aggregate. Count reported Safety Net Assistance amounts and "
        "adults' SSI and state supplements under 404.5(b)(5)(vi). OCFS "
        "excludes children's SSI and state supplements under "
        "404.5(b)(6)(xxi), which OCFS retained when adopting the rule "
        "permanently on June 12, 2024. OCFS uses the child care services unit under "
        "415.1(l). It separates cohabiting adults without a common child "
        "and treats an 18-year-old as an adult outside the parent's unit. "
        "When children live with no parent, OCFS counts only the children "
        "in their unit. PolicyEngine uses the SPM unit, which combines "
        "those cases. Monthly consumers read this annual income with the "
        "bare period and Core divides it."
    )
    reference = (
        "https://www.law.cornell.edu/regulations/new-york/18-NYCRR-404.5",
        "https://ocfs.ny.gov/programs/childcare/regulations/404-Eligibility.pdf#page=10",
        "https://ocfs.ny.gov/main/policies/external/2023/adm/23-OCFS-ADM-18.pdf#page=4",
        "https://dos.ny.gov/system/files/documents/2024/02/022824.pdf#page=8",
        "https://dos.ny.gov/system/files/documents/2024/06/061224.pdf#page=7",
    )

    def formula(spm_unit, period, parameters):
        p = parameters(period).gov.states.ny.ocfs.ccap.income.countable_income
        countable = add(spm_unit, period, p.sources)
        # The federal TANF aggregate reads other states' dependent care
        # deductions, which reach CCAP through child care subsidies.
        # New York's own grant avoids that path. Preserve TANF's controls.
        family_assistance = add(spm_unit, period, ["ny_tanf"]) * spm_unit(
            "takes_up_tanf_if_eligible", period
        )
        family_assistance = where(
            parameters(period).gov.hhs.tanf.abolish_tanf, 0, family_assistance
        )
        person = spm_unit.members
        is_child = person("is_child", period)
        # Both payments are monthly, so add() sums them across the year.
        # OCFS's 404.5(b)(6)(xxi) excludes children's SSI and supplements.
        adult_ssi = where(is_child, 0, add(person, period, ["ssi", "ny_ssp"]))
        # 404.5(b)(6)(xiii) excludes the earnings of a dependent child under
        # 18 who is not legally responsible for the child needing care, and
        # directs that no inquiry be made into them. is_child is age under 18.
        excluded_earner = is_child & ~person("is_parent", period)
        excluded_earnings = where(
            excluded_earner, add(person, period, p.earned_sources), 0
        )
        return (
            countable + family_assistance + spm_unit.sum(adult_ssi - excluded_earnings)
        )
