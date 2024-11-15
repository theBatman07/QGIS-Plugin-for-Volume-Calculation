def classFactory(iface):
    from .VolumeCalculation import VolumeCalculationPlugin
    return VolumeCalculationPlugin(iface)
