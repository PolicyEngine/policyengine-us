from policyengine_us.model_api import *


class ks_disabled_veteran_exemptions_eligible_person(Variable):
    value_type = bool
    entity = Person
    label = "Eligible person for the Kansas disabled veteran exemption"
    definition_period = YEAR
    reference = (
        "https://law.justia.com/codes/kansas/chapter-79/article-32/section-79-32-121/",
        "https://www.kslegislature.gov/li/b2025_26/statute/079_000_0000_chapter/079_032_0000_article/079_032_0121b_section/079_032_0121b_k/",
        "https://www.ksrevenue.gov/pdf/ip23.pdf#page=6",
    )
    defined_for = StateCode.KS

    def formula(person, period, parameters):
        p = parameters(period).gov.states.ks.tax.income.exemptions.disabled_veteran
        # K.S.A. 79-32,121b(b)(2): a veteran the VA certifies "to be in
        # receipt of disability compensation at the 100% rate, if the
        # disability is permanent and was sustained through military action
        # or accident or resulted from disease contracted while in such
        # active service". The VA flags already imply veteran status. The
        # model has no discharge input, so a flagged veteran is assumed to
        # have been honorably discharged.
        paid_at_100_percent = person(
            "is_fully_disabled_service_connected_veteran", period
        )
        permanent = person("is_permanently_disabled_veteran", period)
        return p.in_effect & paid_at_100_percent & permanent
