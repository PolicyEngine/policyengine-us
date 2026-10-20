from policyengine_us.model_api import *


class ia_ssa(Variable):
    value_type = float
    entity = Person
    label = "Iowa State Supplementary Assistance"
    definition_period = MONTH
    unit = USD
    reference = (
        # Iowa Code 249.3
        "https://www.legis.iowa.gov/docs/code/249.pdf#page=1",
        # 441 IAC 52.1; PDF pages 1-2
        "https://www.legis.iowa.gov/docs/iac/chapter/441.52.pdf#page=1",
        # PDF pages 35, 41-49, 59-74, 76-78
        "https://hhs.iowa.gov/media/3987/download?inline=#page=35",
    )
    defined_for = "ia_ssa_eligible"

    def formula(person, period, parameters):
        p = parameters(period).gov.states.ia.hhs.ssa
        federal = parameters(period).gov.ssa.ssi
        category = person("ia_ssa_category", period)
        c = category.possible_values
        federally_paid = person("ia_ssa_federal", period)
        income = person("ia_ssa_care_countable_income", period)
        extra = max_(person("ia_ssa_care_additional_deductions", period), 0)
        partial = person("ia_ssa_care_partial_month_days", period)
        days = where(partial > 0, min_(partial, period.days), period.days)
        # RCF income eligibility uses a 31-day ceiling; payment uses the
        # actual covered days billed by the provider.
        rate = min_(max_(person("ia_ssa_rcf_daily_rate", period), 0), p.rcf_daily_limit)
        rcf_participation = max_(income - p.rcf_personal_needs - extra, 0)
        rcf = max_(rate * days - rcf_participation, 0)
        ihhrc = person("ia_ssa_ihhrc_amount", period)
        # 6-B Making the Family-Life Home Payment: "For a recipient who has
        # only SSI and no other income (and hence no $20 to disregard), an
        # additional $20 payment is necessary". The $20 is SSI's general income
        # exclusion, so the federal parameter is used. Only positive amounts
        # count as other income, and the eligible couple shares one $20.
        receives_ssi = (person("ssi", period) > 0) | person("receives_ssi", period)
        joint = person("ssi_couple_computation_applies", period)
        sources = federal.income.sources
        has_other_income = np.zeros(person.count, dtype=bool)
        for source in list(sources.earned) + list(sources.unearned):
            has_other_income = has_other_income | (person(source, period) > 0)
        has_other_income = where(
            joint, person.marital_unit.any(has_other_income), has_other_income
        )
        flh = category == c.FAMILY_LIFE_HOME
        recipients = person.marital_unit.sum(flh)
        top_up = (
            ~has_other_income
            * receives_ssi
            * federal.income.exclusions.general
            / where(joint, max_(recipients, 1), 1)
        )
        # The SMME standard uses the federal poverty guideline for the
        # recipient's marital unit (6-B Income (SMME)).
        size = person.marital_unit.nb_persons()
        fpg = parameters(period).gov.hhs.fpg
        poverty = (
            fpg.first_person.CONTIGUOUS_US
            + (size - 1) * fpg.additional_person.CONTIGUOUS_US
        ) / MONTHS_IN_YEAR
        # NOTE: Iowa Code 249.3(4)(g) requires "income of at least one hundred
        # twenty percent of the federal poverty level", in a subsection that
        # opens "At the discretion of the department". 441 IAC 51.7(6) says
        # income "must exceed 120 percent of the federal poverty level", and
        # 6-B Income (SMME) p.77 says it "also exceeds 120% of the federal
        # poverty level". The model follows 51.7(6) and the manual, so income
        # of exactly 120% does not qualify (ia_ssa.yaml Cases 56-57).
        smme = (
            person("ia_ssa_smme_coverage_eligible", period)
            & (
                person("ia_ssa_smme_countable_income", period)
                > p.smme_minimum_fpg_rate * poverty
            )
            & (federally_paid == 0)
        )
        state = select(
            [
                category == c.RESIDENTIAL_CARE,
                category == c.IN_HOME_CARE,
                flh,
                category == c.SMME,
            ],
            [rcf, ihhrc, top_up, smme * p.smme_amount],
            default=0,
        )
        return federally_paid + state
