The code is still messy and has some debugging parts in it.

You have to use the pipeline JSON to run it. For this, you need to have PDAL installed (I did it with Anaconda).

Steps:
1. Place the files in the same folder, preferably together with the input .las.
2. Open the pipeline in a text editor and change filename (line 6) to the input .las.
3. Change filename in line 30 to your desired output filename.
4. Open Anaconda Prompt.
5. cd to the directory where you've placed the files
6. Run the following command: PDAL pipeline bag_pipeline.json

Results:
1. Point cloud with an added BAG-id dimension
2. Shapefile of the BAG-features
3. Shapefile of the BAG-classified points to easily visualise the outcome

Known issue: BAG-ids are appended to the .las as floats. This is due to a PDAL limitation when adding a new dimension.
