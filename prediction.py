import math
from datetime import datetime

import numpy as np

from database import get_connection


# -------- CHANCE CALCULATOR -----------


def get_inspector_workload(inspector_id: str):

    db = get_connection()
    cursor = db.cursor()

    cursor.execute(
        """
        SELECT COUNT(*)
        FROM inspections
        WHERE inspector_id = ?
        """,
        (inspector_id,)
    )

    inspector_count = cursor.fetchone()[0]

    cursor.execute(
        """
        SELECT COUNT(*)
        FROM inspections
        """
    )

    total = cursor.fetchone()[0]

    db.close()

    if total == 0:
        return 0.0

    return inspector_count / total


def parse_date(date_str):

    return datetime.strptime(
        date_str,
        "%Y-%m-%d"
    )


def inspector_pressure(inspector_id):

    db = get_connection()
    cursor = db.cursor()

    cursor.execute(
        """
        SELECT COUNT(*)
        FROM inspections
        WHERE inspector_id = ?
        """,
        (inspector_id,)
    )

    count = cursor.fetchone()[0]

    db.close()

    return min(
        count / 50,
        1.0
    )


def compute_mu(last_date, avg_interval, days_since):
    """
    Expected remaining days until inspection
    """

    remaining = max(
        avg_interval - days_since,
        0
    )

    return remaining


def compute_sigma(avg_interval, inspector_pressure, grade_risk):

    base = avg_interval * 0.25

    workload_factor = 1 + inspector_pressure

    risk_factor = 1 + grade_risk

    sigma = (
        base *
        workload_factor *
        risk_factor
    )

    return max(
        sigma,
        2
    )


def build_model(mu, var, inspector_p, grade_p):

    sigma = math.sqrt(
        var + 1e-6
    )

    sigma *= (
        1 + inspector_p
    )

    sigma *= (
        1 + grade_p
    )

    return mu, sigma


def get_intervals(dates):

    parsed = [
        parse_date(d)
        for d in dates
    ]

    return [
        (
            parsed[i + 1] -
            parsed[i]
        ).days

        for i in range(
            len(parsed) - 1
        )
    ]


def grade_risk(grade):

    grade = grade.upper().strip()

    return {
        "A": 0.2,
        "B": 0.5,
        "C": 0.9
    }.get(
        grade,
        0.6
    )


def build_bayesian_model(mu, var, inspector_p, grade_p):

    sigma = math.sqrt(
        max(var, 0)
    )

    sigma *= (
        1 + inspector_p
    )

    sigma *= (
        1 + grade_p
    )

    return mu, sigma


def probability_distribution(mu, sigma, days=30):

    sigma = max(
        sigma,
        0.001
    )

    x = np.arange(
        0,
        days
    )

    probs = np.exp(
        -0.5 *
        ((x - mu) / sigma) ** 2
    )

    probs /= probs.sum()

    return list(
        zip(
            x,
            probs
        )
    )


def get_prediction_window(distribution, threshold=0.7):

    sorted_dist = sorted(
        distribution,
        key=lambda x: x[1],
        reverse=True
    )

    total = 0
    days = []

    for day, probability in sorted_dist:

        days.append(day)

        total += probability

        if total >= threshold:
            break

    return (
        min(days),
        max(days)
    )


def predict_inspection(inspector_id, grade, last_date, inspection_dates):
    """
    Returns a prediction window for next inspection
    """

    intervals = get_intervals(
        inspection_dates
    )
    if not inspection_dates:
        return {
            "window": "No history",
            "confidence": 0
        }

    intervals = get_intervals(
        inspection_dates
    )

    if not intervals:
        return {
            "window": "Not enough data",
            "confidence": 0
        }

    avg_interval = np.mean(
        intervals
    )

    variance = np.var(
        intervals
    )

    days_since = (
        datetime.now() -
        parse_date(last_date)
    ).days

    inspector_p = inspector_pressure(
        inspector_id
    )

    grade_p = grade_risk(
        grade
    )

    mu, sigma = build_bayesian_model(
        avg_interval,
        variance,
        inspector_p,
        grade_p
    )

    distribution = probability_distribution(
        mu,
        sigma
    )

    low, high = get_prediction_window(
        distribution
    )

    return {
        "window": f"{low}-{high} days",
        "confidence": round(
            max(
                p for _, p in distribution
            ) * 100,
            1
        )


    }
