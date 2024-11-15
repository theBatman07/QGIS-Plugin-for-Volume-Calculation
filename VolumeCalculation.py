from qgis.core import QgsProcessingProvider, QgsApplication
from .VolumeCalculationAlgorithm import VolumeCalculation

class VolumeCalculationProvider(QgsProcessingProvider):
    def loadAlgorithms(self, *args, **kwargs):
        self.addAlgorithm(VolumeCalculation())

    def id(self):
        return "volume_calculation_provider"

    def name(self):
        return "Volume Calculation Provider"

    def icon(self):
        return QgsApplication.getThemeIcon("/algorithms.svg")

class VolumeCalculationPlugin:
    def __init__(self, iface):
        self.iface = iface
        self.provider = VolumeCalculationProvider()

    def initGui(self):
        QgsApplication.processingRegistry().addProvider(self.provider)

    def unload(self):
        QgsApplication.processingRegistry().removeProvider(self.provider)
