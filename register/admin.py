from django.contrib import admin

# Register your models here.

from .models import Equipment, InterfaceType, Port, EndPoint, Communication, Consumer, Connection


# admin.site.register(Equipment)
admin.site.register(InterfaceType)
admin.site.register(Port)
# admin.site.register(EndPoint)
admin.site.register(Communication)
admin.site.register(Consumer)
# admin.site.register(Connection)


class PortInline(admin.TabularInline):
    model = Port


class EquipmentAdmin(admin.ModelAdmin):
    list_display = ('name', 'location', 'type')
    inlines = [PortInline]


admin.site.register(Equipment, EquipmentAdmin)


@admin.register(EndPoint)
class EndPointAdmin(admin.ModelAdmin):
    list_display = ('name', 'code')


@admin.register(Connection)
class ConnectionAdmin(admin.ModelAdmin):
    list_display = ('station', 'line', 'communication')
