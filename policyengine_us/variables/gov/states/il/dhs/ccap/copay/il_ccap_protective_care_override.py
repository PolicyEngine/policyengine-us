from policyengine_us.model_api import *


class il_ccap_protective_care_override(Variable):
    value_type = bool
    entity = SPMUnit
    definition_period = MONTH
    label = "Illinois CCAP protective child care copay exemption override"
    defined_for = StateCode.IL
    # Illinois exempts several protective child care groups from the
    # copayment. il_ccap_protective_care_copay_exempt derives two of them from
    # existing inputs: homelessness, and receipt of or need for protective
    # services. This variable carries the remaining groups, none of which has a
    # PolicyEngine analogue, so a caller must set it directly:
    #   - families transitioning from IDCFS Intact Family Services
    #   - families whose parent is called into active military duty
    #   - parenting youth who are themselves in care
    #   - families served by the Extended Family Support Program
    # It defaults to false, so in microsimulation these families are modeled as
    # paying a full Table A copayment rather than none, understating the
    # subsidy for a small share of the caseload.
    # 89 Ill. Adm. Code 50.310 governs the exemption. Part 50 transferred to
    # 23 Ill. Adm. Code 2060 (Department of Early Childhood) at 50 Ill. Reg.
    # 9842, so the section is 2060.310 from 2026-07-01.
    reference = (
        "https://www.dhs.state.il.us/page.aspx?item=54862",
        "https://www.ilga.gov/agencies/JCAR/EntirePart?titlepart=08900050",
    )
