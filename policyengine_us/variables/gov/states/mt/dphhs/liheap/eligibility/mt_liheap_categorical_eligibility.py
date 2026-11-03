from policyengine_us.model_api import *


class MTLIHEAPCategoricalEligibility(Enum):
    SNAP = "SNAP"
    SSI_TANF = "SSI or TANF"
    NONE = "None"


class mt_liheap_categorical_eligibility(Variable):
    value_type = Enum
    entity = SPMUnit
    possible_values = MTLIHEAPCategoricalEligibility
    default_value = MTLIHEAPCategoricalEligibility.NONE
    definition_period = YEAR
    label = "Montana LIHEAP categorical eligibility"
    defined_for = StateCode.MT
    reference = (
        "https://rules.mt.gov/policy-library-documents/application/pdf/5475239b875d29ebe7cf1f12b38458830f87a4a18c8dd600b7548603204fccd9#page=1",
        "https://rules.mt.gov/policy-library-documents/application/pdf/325b36e5abb6a3bfa036c3802fc997ed50711b5407868ec8f4b61eabc538e3ed#page=3",
        "https://rules.mt.gov/policy-library-documents/application/pdf/fa158b2cdbf766e585e1fbf5811523e0dff4e760111590ae75d0456ee81551ad#page=3",
        # PDF pages 27-30, 128-131
        "https://web.archive.org/web/20261015032646/https://dphhs.mt.gov/assets/hcsd/liheap/LIHEAPmanual.pdf#page=27",
        "https://liheapch.acf.gov/docs/2026/state-plans/MT_Plan_2026.pdf#page=5",
    )

    def formula(spm_unit, period, parameters):
        p = parameters(period).gov.states.mt.dphhs.liheap.categorical
        person = spm_unit.members
        first_month = period.first_month
        months = [
            first_month.offset(month_offset) for month_offset in range(MONTHS_IN_YEAR)
        ]
        # Monthly booleans are read month by month, never with an annual ADD,
        # so no summed value is cached under the annual key.
        # SNAP: the unit receives SNAP and every member is in the SNAP unit.
        receives_snap = spm_unit("snap", period, options=[ADD]) > 0
        in_snap_unit = np.any(
            [~person("is_snap_excluded_member", month) for month in months],
            axis=0,
        )
        snap_categorical = receives_snap & spm_unit.all(in_snap_unit)
        # SSI or TANF: every member receives SSI or TANF cash assistance, or
        # had income considered for those grants (ARM 37.70.401(23), numbered
        # (24) from May 23, 2026): a spouse of an SSI recipient, a parent of an
        # SSI-recipient child, or a member of the TANF assistance unit.
        receives_ssi = person("mt_liheap_receives_ssi", period)
        receives_tanf = spm_unit("tanf", period) > 0
        in_tanf_unit = np.any(
            [
                person("mt_tanf_payment_eligible_child", month)
                | person("mt_tanf_payment_eligible_parent", month)
                for month in months
            ],
            axis=0,
        )
        tanf_member = spm_unit.project(receives_tanf) & in_tanf_unit
        spouse_of_ssi_recipient = person.marital_unit.any(receives_ssi)
        ssi_recipient_child = receives_ssi & (person("age", period) < p.minor_child_age)
        # SSA considers a parent's income for a child's SSI. The head or spouse
        # of the SSI child's own tax unit stands in for the parent; an adult
        # sibling or other relative filing separately is not covered (manual
        # Appendix A, section 9.8 examples). An unmarried co-resident parent
        # who does not claim the child is also not covered, and a grandparent
        # or other relative who claims the child counts as a parent.
        head_or_spouse = person("is_tax_unit_head_or_spouse", period)
        parent_of_ssi_child = head_or_spouse & person.tax_unit.any(ssi_recipient_child)
        covered = (
            receives_ssi | tanf_member | spouse_of_ssi_recipient | parent_of_ssi_child
        )
        ssi_tanf_categorical = spm_unit.all(covered) & (
            spm_unit.any(receives_ssi) | receives_tanf
        )
        # Manual section 3.10 checks SNAP first, then SSI and TANF.
        return select(
            [snap_categorical, ssi_tanf_categorical],
            [
                MTLIHEAPCategoricalEligibility.SNAP,
                MTLIHEAPCategoricalEligibility.SSI_TANF,
            ],
            default=MTLIHEAPCategoricalEligibility.NONE,
        )
