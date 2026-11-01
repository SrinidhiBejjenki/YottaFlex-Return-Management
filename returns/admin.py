from django.contrib import admin

from django.contrib import admin
from .models import (
    Customer,
    Order,
    OrderLine,
    ReturnRequest,
    ReturnLine,
    ReturnAuthorization,
    ReturnShipment,
    Inspection,
    Refund,
    InventoryDisposition,
    ReturnEvent,
)
admin.site.register(Customer)
admin.site.register(Order)
admin.site.register(OrderLine)
admin.site.register(ReturnRequest)
admin.site.register(ReturnLine)
admin.site.register(ReturnAuthorization)
admin.site.register(ReturnShipment)
admin.site.register(Inspection)
admin.site.register(Refund)
admin.site.register(InventoryDisposition)
admin.site.register(ReturnEvent)
