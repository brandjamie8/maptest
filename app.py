import streamlit as st
import geopandas as gpd
import folium
from streamlit_folium import folium_static
from folium.plugins import MarkerCluster

# Streamlit app layout
st.title("Dynamic Map from Shapefile")

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
        st.write("Shapefile successfully loaded!")

        # Convert to WGS84 (lat/lon) if needed
        if gdf.crs and gdf.crs.to_string() != "EPSG:4326":
            gdf = gdf.to_crs(epsg=4326)

        # Preview data
        st.write(gdf.head())

        # Create a folium map
        center = gdf.geometry.centroid.iloc[0].y, gdf.geometry.centroid.iloc[0].x
        m = folium.Map(location=center, zoom_start=10)

        # Add data to map
        folium.GeoJson(gdf, name="Shapefile Layer").add_to(m)

        # Optionally add markers for centroids
        marker_cluster = MarkerCluster().add_to(m)
        for _, row in gdf.iterrows():
            centroid = row.geometry.centroid
            folium.Marker([centroid.y, centroid.x], popup=row.get('name', 'No Name')).add_to(marker_cluster)

        # Display map in Streamlit
        folium_static(m)

    except Exception as e:
        st.error(f"Error loading shapefile: {e}")

st.write("Upload a shapefile (zipped) to visualize it on the map.")
