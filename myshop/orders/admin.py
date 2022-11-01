import csv
import datetime
from django.http import HttpResponse
from django.contrib import admin
from django.urls import reverse
from django.utils.safestring import mark_safe
from prometheus_client import CONTENT_TYPE_LATEST

from .models import Order, OrderItem


def order_payment(obj: Order):
    url = obj.get_stripe_url()
    if obj.stripe_id:
        html = f'<a href="{url}" target="_blank">{obj.stripe_id}</a>'
        return mark_safe(html)
    return ""


order_payment.short_description = "оплата на Stripe"

def order_detail(obj):
    url = reverse('orders:admin_order_detail', args=[obj.id])
    return mark_safe(f'<a href="{url}">Детальное описание</a>')


def export_to_csv(modeladmin, request, queryset):
    opts = modeladmin.model._meta
    content_dispositon = f"attachment; filename={opts.verbose_name}.csv"
    response = HttpResponse(content_type="text/csv")
    response['Content-Disposition'] = content_dispositon
    writer = csv.writer(response)
    fields = [field for field in opts.get_fields() if not field.many_to_many and not field.one_to_many]
    # [first_name, last_name, email] for Model Order
    writer.writerow([field.verbose_name for field in fields])
    for obj in queryset:
        data_row = []
        for field in fields:
            value = getattr(obj, field.name)
            if isinstance(value, datetime.datetime):
                value = value.strftime('%d/%m/%Y')
            data_row.append(value)
        writer.writerow(data_row)
    return response
export_to_csv.short_description = "Экспорт в CSV"



class OrderItemInline(admin.TabularInline):
    model = OrderItem
    raw_id_fields = ["product"]


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = [
        "id",
        "first_name",
        "last_name",
        "email",
        "address",
        "postal_code",
        "city",
        "paid",
        order_payment,
        "created",
        "updated",
        order_detail
    ]
    list_filter = ["paid", "created", "updated"]
    inlines = [OrderItemInline]
    readonly_fields = ["stripe_id"]
    actions = [export_to_csv]