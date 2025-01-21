import streamlit as st
import geopandas as gpd
import folium
from streamlit_folium import folium_static

# Streamlit app layout
st.title("Filter Shapefile for Lewisham")

# Upload shapefile
uploaded_file = st.file_uploader("Upload your shapefile (.shp, .shx, .dbf, .prj as a .zip file)", type=["zip"])

if uploaded_file is not None:
    # Save uploaded zip file and extract
    with open("shapefile.zip", "wb") as f:
        f.write(uploaded_file.getvalue())

    import zipfile
    with zipfile.ZipFile("shapefile.zip", "r") as zip_ref:
        zip_ref.extractall("shapefile")

    # Load the shapefile using geopandas
    try:
        gdf = gpd.read_file("shapefile")

        # Ensure the column exists
        if 'LAD11NM' not in gdf.columns:
            st.error("Column 'LAD11NM' not found in shapefile.")
        else:
            # Filter for records where LAD11NM contains 'lewisham' (case insensitive)
            filtered_gdf = gdf[gdf['LAD11NM'].str.contains('lewisham', case=False, na=False)]

            if filtered_gdf.empty:
                st.warning("No records found for 'Lewisham'.")
            else:
                st.write(f"Filtered {len(filtered_gdf)} areas with 'Lewisham' in LAD11NM")

                # Convert CRS to WGS84 (latitude/longitude)
                if filtered_gdf.crs and filtered_gdf.crs.to_string() != "EPSG:4326":
                    filtered_gdf = filtered_gdf.to_crs(epsg=4326)

                # Display the filtered data
                st.write(filtered_gdf[['LAD11NM']].head())

                # Create a folium map centered on the filtered area
                center = filtered_gdf.geometry.centroid.iloc[0].y, filtered_gdf.geometry.centroid.iloc[0].x
                m = folium.Map(location=center, zoom_start=12)

                # Add filtered polygons to the map
                folium.GeoJson(filtered_gdf, name="Filtered Areas").add_to(m)

                # Display the map
                folium_static(m)

    except Exception as e:
        st.error(f"Error loading shapefile: {e}")

st.write("Upload a shapefile (zipped) to visualize filtered areas.")
