from enum import StrEnum


class UserRole(StrEnum):
    GeneralManager = "Генеральный директор"
    ProductionManager = "Заведующий производственным цехом"
    WarehouseManager = "Заведующий складом"
    PatternDesigner = "Закройщик-конструктор"
    Designer = "Дизайнер"
    Cutter = "Раскройщик"
    PackerInspector = "Упаковщик-контролёр готовой продукции"
    Sewer = "Швея"


    @classmethod
    @property
    def values_list(cls):
        return [
            (channel.value, channel.value) for channel in cls
        ]
    
    @classmethod
    @property
    def workers_list(cls):
        return [
            "Раскройщик",
            "Швея"
        ]
