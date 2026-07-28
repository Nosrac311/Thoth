from datetime import datetime
import discord

from database import (  # type: ignore
    get_connection,
    get_restaurant_history,
    get_distribution_params,
)

from prediction import (  # type: ignore
    parse_date,
    get_intervals,
    inspector_pressure,
    grade_risk,
    build_bayesian_model,
    probability_distribution,
    build_model
)


async def build_forecast_embed(county: str):
    county = county.upper()

    db = get_connection()
    cursor = db.cursor()

    cursor.execute("""
        SELECT restaurant, inspector_id, grade, inspection_date
        FROM inspections
        WHERE source = ?
        GROUP BY restaurant
    """, (county,))

    restaurants = cursor.fetchall()

    db.close()

    predictions = []

    for restaurant, inspector_id, grade, last_date in restaurants:

        dates = get_restaurant_history(
            restaurant,
            county.upper()
        )

        # Need history to predict
        if len(dates) < 2:
            continue

        intervals = get_intervals(dates)

        if not intervals:
            continue

        # Bayesian parameters
        mu, var = get_distribution_params(
            restaurant,
            county.upper()
        )

        inspector_p = inspector_pressure(
            inspector_id
        )

        grade_p = grade_risk(
            grade
        )

        # Bayesian model
        mu, sigma = build_model(
            mu,
            var,
            inspector_p,
            grade_p
        )

        days_since = (
            datetime.now()
            - parse_date(last_date)
        ).days

        # Probability that inspection happens soon
        dist = probability_distribution(
            mu,
            sigma,
            days=60
        )

        # Adjust probability based on how long overdue it is
        probability_score = 0

        for days, probability in dist:
            predicted_date = days

            if predicted_date >= days_since:
                probability_score += probability

        predictions.append({
            "restaurant": restaurant,
            "score": probability_score,
            "days_since": days_since,
            "avg_interval": round(mu),
            "grade": grade
        })

    if not predictions:
        embed = discord.Embed(
            title=f"🔮 Live Inspection Forecast - {county}",
            description="Not enough inspection history available.",
            color=discord.Color.orange()
        )
        return embed

    predictions.sort(
        key=lambda x: x["score"],
        reverse=True
    )

    embed = discord.Embed(
        title=f"🔮 Live Inspection Forecast - {county}",
        description="Automatically updated.",
        color=discord.Color.purple()
    )

    for index, item in enumerate(predictions[:3], start=1):

        confidence = round(item["score"] * 100, 1)

        embed.add_field(
            name=f"{index}. {item['restaurant']}",
            value=(
                f"📈 Likelihood: **{confidence}%**\n"
                f"📅 Days since last inspection: {item['days_since']}\n"
                f"⏱ Avg interval: {item['avg_interval']} days\n"
                f"⭐ Grade: {item['grade']}"
            ),
            inline=False
        )

    embed.set_footer(
        text=f"Updated {discord.utils.utcnow():%Y-%m-%d %H:%M UTC}"
    )

    return embed
