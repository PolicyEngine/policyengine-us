from policyengine_us.model_api import *
from policyengine_us.parameters.gov.states.tx.twc.ccs.payment.rates_expanded_age_groups import (
    get_rates,
)


class tx_ccs_payment_rate(Variable):
    value_type = float
    entity = Person
    label = "Texas Child Care Services (CCS) payment amount"
    unit = USD
    definition_period = MONTH
    defined_for = "tx_ccs_eligible_child"
    reference = (
        "https://web.archive.org/web/20161230070058/http://twc.texas.gov/files/partners/board-maximum-daily-rates-twc.pdf",
        "https://web.archive.org/web/20180904071531/https://twc.texas.gov/files/partners/12-18att1-twc.pdf",
        "https://web.archive.org/web/20191118112209/https://www.twc.texas.gov/files/policy_letters/attachments/wd-23-19att1-twc.pdf",
        "https://web.archive.org/web/20201020200555/https://www.twc.texas.gov/files/policy_letters/attachments/wd-25-20-att.1-wfed.pdf",
        "https://web.archive.org/web/20210428191842/https://www.twc.texas.gov/files/partners/bcy21-child-care-rates-twc.xlsx",
        "https://web.archive.org/web/20210930004510/https://www.twc.texas.gov/files/policy_letters/attachments/24-21-att1-twc.pdf",
        "https://www.twc.texas.gov/sites/default/files/wf/policy-letter/wd/22-22-att1-twc.pdf",
        "https://www.twc.texas.gov/sites/default/files/wf/docs/20-23-att1-twc.pdf",
        "https://www.twc.texas.gov/sites/default/files/ccel/docs/bcy25-board-max-provider-payment-rates-4-age-groups-twc.pdf",
        "https://www.twc.texas.gov/sites/default/files/ccel/docs/bcy25-board-max-provider-payment-rates-8-age-groups-twc.pdf",
        "https://www.twc.texas.gov/sites/default/files/ccel/docs/bcy26-board-max-provider-payment-rates-twc.pdf",
        "https://www.twc.texas.gov/sites/default/files/wf/policy-letter/wd/02-20-twc.pdf#page=2",
    )

    def formula(person, period, parameters):
        household = person.household
        region = household("tx_ccs_workforce_board_region", period)

        p = parameters(period).gov.states.tx.twc.ccs.payment

        provider_type = person("tx_ccs_provider_type", period)
        provider_rating = person("tx_ccs_provider_rating", period)
        age_category = person("tx_ccs_child_age_category", period)
        care_schedule = person("tx_ccs_care_schedule", period)

        attending_days_per_month = person(
            "childcare_attending_days_per_month", period.this_year
        )

        # TWC prints one relative rate per Board and labels it Reg or None, by
        # table and by Board, so either label reads that rate.
        rating_labels = provider_rating.possible_values
        unrated_relative = (provider_type == provider_type.possible_values.RELATIVE) & (
            (provider_rating == rating_labels.REG)
            | (provider_rating == rating_labels.NONE)
        )
        rating = where(
            unrated_relative,
            "REG" if p.uses_expanded_age_groups else "NONE",
            provider_rating.decode_to_str(),
        )

        if p.uses_expanded_age_groups:
            year = period.start.year
            month = period.start.month
            bcy_year = year + where(month >= 10, 1, 0)
            daily_rate = _lookup_expanded_rate(
                bcy_year,
                region,
                provider_type,
                rating,
                age_category,
                care_schedule,
            )
        else:
            daily_rate = p.rates[region][provider_type][rating][age_category][
                care_schedule
            ]

        return daily_rate * attending_days_per_month


def _lookup_expanded_rate(
    bcy_year,
    region,
    provider_type,
    provider_rating,
    age_category,
    care_schedule,
):
    rates_df = get_rates(bcy_year)

    df = pd.DataFrame(
        {
            "region": region.decode_to_str(),
            "provider_type": provider_type.decode_to_str(),
            "provider_rating": provider_rating,
            "age_group": age_category.decode_to_str(),
            "schedule": care_schedule.decode_to_str(),
        }
    )
    df["_idx"] = np.arange(len(df))

    merged = pd.merge(
        df,
        rates_df,
        how="left",
        on=[
            "region",
            "provider_type",
            "provider_rating",
            "age_group",
            "schedule",
        ],
    )

    merged = merged.sort_values("_idx")
    return merged["rate"].fillna(0.0).values
