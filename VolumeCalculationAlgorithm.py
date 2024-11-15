from qgis.PyQt.QtCore import QCoreApplication
from qgis.core import (QgsProcessing, QgsProcessingAlgorithm,
                       QgsProcessingParameterRasterLayer,
                       QgsProcessingParameterVectorLayer,
                       QgsProcessingException)
from osgeo import ogr, gdal, osr
import numpy as np

class VolumeCalculation(QgsProcessingAlgorithm):
    DEM = 'DEM'
    BASE_DEM = 'BASE_DEM'
    HEAP_POLYGON = 'HEAP_POLYGON'
    OUTPUT_CUT_VOLUME = 'OUTPUT_CUT_VOLUME'
    OUTPUT_FILL_VOLUME = 'OUTPUT_FILL_VOLUME'
    OUTPUT_NET_VOLUME = 'OUTPUT_NET_VOLUME'

    def initAlgorithm(self, config=None):
        self.addParameter(
            QgsProcessingParameterRasterLayer(
                self.DEM,
                self.tr('DEM Layer')
            )
        )
        
        self.addParameter(
            QgsProcessingParameterRasterLayer(
                self.BASE_DEM,
                self.tr('Base DEM Layer')
            )
        )

        self.addParameter(
            QgsProcessingParameterVectorLayer(
                self.HEAP_POLYGON,
                self.tr('Heap Polygon Layer'),
                types=[QgsProcessing.TypeVectorPolygon]
            )
        )

    def rasterize_polygon_layer(self, polygon_layer, dem_layer):
        """Rasterizes the polygon layer to match the DEM extent and resolution."""

        # DEM layer properties
        dem_extent = dem_layer.extent()
        cols, rows = dem_layer.width(), dem_layer.height()
        no_data_value = -9999

        # Create an in-memory raster for the polygon mask
        target_ds = gdal.GetDriverByName('MEM').Create('', cols, rows, 1, gdal.GDT_Byte)
        target_ds.SetGeoTransform((
            dem_extent.xMinimum(), dem_layer.rasterUnitsPerPixelX(), 0,
            dem_extent.yMaximum(), 0, -dem_layer.rasterUnitsPerPixelY()
        ))

        # Define spatial reference based on DEM
        srs = osr.SpatialReference()
        srs.ImportFromWkt(dem_layer.crs().toWkt())
        target_ds.SetProjection(srs.ExportToWkt())

        # Convert the QGIS vector layer to an OGR in-memory layer
        uri = polygon_layer.dataProvider().dataSourceUri()
        ogr_ds = ogr.Open(uri)
        ogr_layer = ogr_ds.GetLayer()

        # Rasterize the polygon onto the in-memory raster
        gdal.RasterizeLayer(target_ds, [1], ogr_layer, burn_values=[1])

        # Read the rasterized layer as a numpy array
        mask_array = target_ds.GetRasterBand(1).ReadAsArray()
        mask_array[mask_array == 0] = no_data_value  # Set background cells to no_data_value

        return mask_array

    def processAlgorithm(self, parameters, context, feedback):
        dem_layer = self.parameterAsRasterLayer(parameters, self.DEM, context)
        base_dem_layer = self.parameterAsRasterLayer(parameters, self.BASE_DEM, context)
        heap_polygon_layer = self.parameterAsVectorLayer(parameters, self.HEAP_POLYGON, context)

        dem_raster = gdal.Open(dem_layer.dataProvider().dataSourceUri())
        base_dem_raster = gdal.Open(base_dem_layer.dataProvider().dataSourceUri())
        dem_array = dem_raster.ReadAsArray()
        base_dem_array = base_dem_raster.ReadAsArray()

        if dem_array.shape != base_dem_array.shape:
            raise QgsProcessingException("DEM and Base DEM must have the same resolution and extent.")

        mask_array = self.rasterize_polygon_layer(heap_polygon_layer, dem_layer)
        valid_mask = mask_array != -9999

        dem_values = np.where(valid_mask, dem_array, np.nan)
        base_dem_values = np.where(valid_mask, base_dem_array, np.nan)
        diff = dem_values - base_dem_values

        feedback.pushInfo(f"DEM min and max within polygon: {np.nanmin(dem_values)}, {np.nanmax(dem_values)}")
        feedback.pushInfo(f"Base DEM min and max within polygon: {np.nanmin(base_dem_values)}, {np.nanmax(base_dem_values)}")
        feedback.pushInfo(f"Valid mask sum (number of cells within polygon): {np.sum(valid_mask)}")
        feedback.pushInfo(f"Max and Min values in diff: {np.nanmax(diff)}, {np.nanmin(diff)}")
        feedback.pushInfo(f"Number of positive values in diff (cut volume): {np.sum(diff > 0)}")
        feedback.pushInfo(f"Number of negative values in diff (fill volume): {np.sum(diff < 0)}")

        cut_volume = np.nansum(np.where(diff > 0, diff, 0))
        fill_volume = np.nansum(np.where(diff < 0, -diff, 0))
        net_volume = cut_volume - fill_volume

        feedback.pushInfo("\n\n")

        feedback.pushInfo(f"Cut Volume: {cut_volume}")
        feedback.pushInfo(f"Fill Volume: {fill_volume}")
        feedback.pushInfo(f"Net Volume: {net_volume}")

        feedback.pushInfo("\n\n")

        return {
            self.OUTPUT_CUT_VOLUME: cut_volume,
            self.OUTPUT_FILL_VOLUME: fill_volume,
            self.OUTPUT_NET_VOLUME: net_volume
        }

    def name(self):
        return 'volume_calculation'

    def displayName(self):
        return self.tr('Volume Calculation')

    def group(self):
        return self.tr('Custom Scripts')

    def groupId(self):
        return 'customscripts'

    def tr(self, string):
        return QCoreApplication.translate('Processing', string)

    def createInstance(self):
        return VolumeCalculation()
