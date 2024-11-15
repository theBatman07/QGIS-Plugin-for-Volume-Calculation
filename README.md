# Volume Calculation Plugin for QGIS

#### Overview

This QGIS plugin calculates the cut, fill, and net volume between a primary Digital Elevation Model (DEM) and a reference DEM within a specified polygon boundary. This is useful in fields where precise volume estimations are required.

#### Solution

The `VolumeCalculation` plugin leverages Python, GDAL, and QGIS libraries to:

- Load two DEM layers and a polygon layer that defines the area of interest.
- Rasterize the polygon boundary to match the DEM resolution.
- Calculate the volume differences within the polygon, outputting cut, fill, and net volumes.

---

### Requirements

- QGIS
- Python
- Numpy

## Setup and Installation

- Clone the GitHub repo -
  
  ```bash
  git clone https://github.com/theBatman07/QGIS-Plugin-for-Volume-Calculation.git
  ```
  
- Open QGIS, click on Plugins > Manage and Install Plugins > Settings, and enable Show also Experimental Plugins
  
- Go to Install from Zip and Choose the Zip file from the clone repo and Click on Install Plugin
  
- You can now see the Plugin in QGIS Processing Toolbox. (You can also search for 'Volume Calculation' and will show the plugin)
  

### Usage

1. **Load Layers**:
  
  - Add a primary DEM layer and a base/reference DEM layer in QGIS (heap-dem and base-dem).
  - Add a polygon vector layer defining the area for volume calculation (polygons.shp).
2. **Run the Plugin**:
  
  - Open the Volume Calculation tool from the QGIS Processing Toolbox.
  - Select the layers for DEM, Base DEM, and Heap Polygon.
  - Click “Run” to process the layers and calculate volumes.
3. **Output**:
  
  - The plugin returns cut, fill, and net volume values. These values are displayed in the QGIS log window.

### Technical Details

- **DEM and Base DEM Compatibility**: Both DEM layers should have matching extents and resolutions for accurate calculation.
- **Polygon Masking**: The plugin rasterizes the polygon to a mask array, ensuring calculations are limited to within the polygon.
- **Volume Calculation**:
  - The difference between DEM and Base DEM is computed for each pixel within the polygon.
  - Positive differences (cut volume) and negative differences (fill volume) are summed to provide the net volume.

### Technical Choices and Trade-offs

- **GDAL and QGIS**: Chosen for efficient geospatial data handling.
- **NumPy**: Enables high-speed array operations and efficient calculation of large raster data.
- **Limitations**: Current implementation assumes DEMs are aligned. If they aren’t, an error will alert the user.

### Known Limitations and TODOs

- **Performance on Large Datasets**: Processing may be slow for high-resolution DEMs over large areas. Memory management improvements can be done large-scale projects.

### Future Improvements

- **Auto Alignment**: Check for DEMs alignment and auto align DEMs.
- **Performance Enhancements**: Process large DEMs in parallel or by tiles.
- **Improved Error Handling**: Additional validation to handle varied DEM resolutions.
- **Enhanced Usability**: Allow users to specify no-data values or apply custom scaling.

## Explanation of Output and Scenarios

#### **Volume Calculation Output:**

The plugin calculates **Cut Volume**, **Fill Volume**, and **Net Volume** based on the difference between the **Primary DEM** (current terrain) and the **Base DEM** (reference terrain), within the user-defined polygon area. Here’s an example of the output and what it means:

```mathematica
DEM min and max within polygon: 13.894182205200195, 30.69779396057129
Base DEM min and max within polygon: 13.894182205200195, 18.0
Valid mask sum (number of cells within polygon): 18399372
Max and Min values in diff: 12.697793960571289, 0.0
Number of positive values in diff (cut volume): 12356925
Number of negative values in diff (fill volume): 0

Cut Volume: 32212708.0
Fill Volume: 0.0
Net Volume: 32212708.0
```

#### **When Fill Volume is 0:**

In some cases, the **fill volume** may be zero. This happens when:

- **Base DEM Elevations Are Higher Than or Equal to the Primary DEM**: If the **Base DEM** is **always higher** than or equal to the **Primary DEM** within the defined area, there will be no need for fill (no areas where material needs to be added). In this case, the **difference** (Primary DEM - Base DEM) will always be **positive** or zero, which means **no fill volume** is calculated.
  
- **Example from the Above Data**:
  
  - The **Base DEM** minimum value is **18.0**, while the **Primary DEM** has a maximum value of **30.7** within the same area.
  - The **difference (Primary DEM - Base DEM)** yields a **positive** value (cut volume), indicating that the current terrain is above the baseline, and material would need to be **excavated (cut)** to bring the terrain down to the baseline level.
  - Since there is no area where the **Primary DEM** is below the **Base DEM**, there is no need for material to be added, which results in **fill volume = 0**.