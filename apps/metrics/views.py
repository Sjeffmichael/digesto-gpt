from datetime import datetime, timedelta

from django.db.models import Count, F, FloatField, Q
from django.db.models.functions import Cast, Round
from django.shortcuts import render
from django.views.generic import View
from pydantic import BaseModel, Field

from apps.chats.models import Message
from common.util.locale import is_language_switcher_request

# Create your views here.


class DateOptions(BaseModel):
    today: datetime = Field(default=datetime.now())
    yesterday: datetime = Field(default=datetime.now() - timedelta(days=1))
    last_seven_days: datetime = Field(default=datetime.now() - timedelta(days=7))
    last_thirty_days: datetime = Field(default=datetime.now() - timedelta(days=30))
    last_ninety_days: datetime = Field(default=datetime.now() - timedelta(days=90))


class Metrics(View):

    def get(self, request):
        context = {}
        date_format = "%d/%m/%Y"
        date_options = DateOptions()
        default_start_date = datetime(date_options.today.year, 1, 1)
        default_end_date = date_options.today
        incoming_start_date = request.GET.get("start_date")
        incoming_end_date = request.GET.get("end_date")
        start_date = (
            datetime.strptime(incoming_start_date, date_format)
            if incoming_start_date
            else default_start_date
        )
        end_date = (
            datetime.strptime(incoming_end_date, date_format)
            if incoming_end_date
            else default_end_date
        )
        language_switcher_request = is_language_switcher_request(request)
        context["date_options"] = date_options.model_dump()
        context["start_date"] = start_date
        context["end_date"] = end_date
        if request.htmx and not language_switcher_request:
            template_name = "metrics/metrics_section.html"
        else:
            template_name = "metrics/metrics_full.html"
        context["generation_metrics"] = (
            Message.objects.filter(
                Q(created_date__gte=start_date)
                & Q(created_date__lte=end_date)
                & ~Q(metrics={}),
                metrics__isnull=False,
            )
            .annotate(
                faithfulness=Round(
                    Cast(F("metrics__faithfulness"), FloatField()) * 100
                ),
                answer_relevancy=Round(
                    Cast(F("metrics__answer_relevancy"), FloatField()) * 100
                ),
                context_utilization=Round(
                    Cast(F("metrics__context_utilization"), FloatField()) * 100
                ),
            )
            .values(
                "faithfulness",
                "answer_relevancy",
                "context_utilization",
                "created_date",
            )
        )

        context["metrics_counts"] = Message.objects.filter(
            Q(created_date__gte=start_date)
            & Q(created_date__lte=end_date)
            & ~Q(metrics={}),
            metrics__isnull=False,
        ).aggregate(
            total_answers=Count("id"),
            coherent_count_metric=Count("metrics", filter=Q(metrics__coherence=1.0)),
            incoherent_count_metric=Count("metrics", filter=Q(metrics__coherence=0.0)),
            correct_count_metric=Count("metrics", filter=Q(metrics__correctness=1.0)),
            incorrect_count_metric=Count("metrics", filter=Q(metrics__correctness=0.0)),
            consistent_count_metric=Count(
                "metrics", filter=Q(metrics__conciseness=1.0)
            ),
            inconsistent_count_metric=Count(
                "metrics", filter=Q(metrics__conciseness=0.0)
            ),
        )

        return render(request, template_name, context)
