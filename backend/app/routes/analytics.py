"""Analytics blueprint — read-only endpoints."""
import datetime

from flask import Blueprint, jsonify, request

from app.services.analytics_service import AnalyticsService

analytics_bp = Blueprint("analytics", __name__)


def _current_month() -> str:
    return datetime.date.today().strftime("%Y-%m")


@analytics_bp.route("/summary", methods=["GET"])
def summary():
    month = request.args.get("month", _current_month())
    return jsonify(AnalyticsService.monthly_summary(month)), 200


@analytics_bp.route("/breakdown", methods=["GET"])
def breakdown():
    month = request.args.get("month", _current_month())
    return jsonify(AnalyticsService.category_breakdown(month)), 200


@analytics_bp.route("/trends", methods=["GET"])
def trends():
    months = request.args.get("months", 6, type=int)
    return jsonify(AnalyticsService.monthly_trends(months=min(months, 24))), 200
