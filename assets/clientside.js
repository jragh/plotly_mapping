// Function to enable CMA dropdown for graphing //
let cmaDropdownEnablefunction  = function(selectedJSON) {

    console.log(selectedJSON);
        
    if (selectedJSON !== null && selectedJSON !== undefined && selectedJSON !== '' && selectedJSON.length > 0) {
                    
        console.log(selectedJSON);
                    
        console.log(false);
            
        return [false, undefined];
        
    }

    return [true, window.dash_clientside.no_update];

}


let cmaTransitModeAggStatsSelection = function(selectedCMA, cmaTransitModeAggStats, geojsonSelected) {

    if (geojsonSelected === 'assets/test_output_2.geojson' && selectedCMA !== undefined && selectedCMA !== '') {

        console.log(`Selected CMA: ${selectedCMA}`);

        let fullTransitModeAggStats = cmaTransitModeAggStats;

        let selectedData = fullTransitModeAggStats.filter(

            function(feature) { return selectedCMA.includes(feature['CMA Code']); }

        );

        console.log((Math.round(selectedData[0]["Pct of Public Transit Commute"] * 100 * 10, 5) / 10).toFixed(2));
        

        return [
            `${selectedData[0]["Public Transit"].toLocaleString("en-US")}`,
            `${(selectedData[0]["Pct of Public Transit Commute"] * 100).toFixed(2)}%`,
            `${selectedData[0]["Automobile Drivers"].toLocaleString("en-US")}`,
            `${(selectedData[0]["Pct of Automobile Driver Commute"] * 100).toFixed(2)}%`
        ]

    }

    return [window.dash_clientside.no_update, window.dash_clientside.no_update, window.dash_clientside.no_update, window.dash_clientside.no_update];
    

}


// clientside callback function to update the header for our statistics cards //
let cmaKeyStatsHeader = function(selectedGeojson, selectedCMA, stateGeojson, stateCMA, stateCMADropdownStore) {

    if (stateGeojson === undefined || stateGeojson === null || stateGeojson == '') {

        return ['Key Statistics: Please select a Data Topic & CMA'];

    }

    // Else condition when the geoJSON is selected here //
    else {

        // if the CMA selection is blank, then 
        if (stateCMA === undefined || stateCMA === null || stateCMA === '') { return ['Travel Mode Key Statistics: Please Select a CMA'];}

        else {

            // Introduced a dcc.store which has the values and labels for the CMA dropdown //
            // need to filter it based on the selected value since there is no way currently to extract value and label //
            let stateCMALabel = stateCMADropdownStore['cma_listing'].filter(cma => cma.value === stateCMA);

            // Return statement separated for organization //
            let returnStatement = `Travel Mode Key Statistics: ${stateCMALabel[0]['label']}`;

            // Returning non blank return statement //
            return [returnStatement];

        }

    }

}


// clientside callback function to animate zoom to bounds in leaflet based on selected CMA //
let cmaLeafletMapBoundsZoom = function(selectedCMA, cmaCentroidObj) {

    if (!selectedCMA || selectedCMA === undefined) {

        return [window.dash_clientside.no_update];

    }

    

    const bounds = (selectedCMA in cmaCentroidObj) ? cmaCentroidObj[selectedCMA] : undefined;

    if (bounds === undefined || !bounds) { return [window.dash_clientside.no_update]; }

    // Extract coordinates: [[south, west], [north, east]]
    const [[south, west], [north, east]] = bounds;
    
    // Calculate center
    const centerLat = (south + north) / 2;
    const centerLon = (west + east) / 2;
    
    // Calculate zoom level based on bounds size
    // Rough approximation: smaller area = higher zoom
    const latDiff = Math.abs(north - south);
    const lonDiff = Math.abs(east - west);
    const maxDiff = Math.max(latDiff, lonDiff);
    
    // Zoom calculation (rough heuristic)
    let zoom;
    if (maxDiff > 5) zoom = 6;        // Very large area (multiple provinces)
    else if (maxDiff > 2) zoom = 8;   // Large CMA
    else if (maxDiff > 1) zoom = 9;   // Medium CMA
    else if (maxDiff > 0.5) zoom = 10; // Small-medium CMA
    else if (maxDiff > 0.25) zoom = 11; // Small CMA
    else zoom = 12; // Very small area

    let center = [centerLat, centerLon];

    const viewport = {
        'center': center,
        'zoom': zoom,
        'transition': 'flyTo',
        'option': {'duration': 1.5, 'easeLinearity': 0.2}
    };

    // const viewport = {
    //     'bounds': bounds,
    //     'transition': 'flyToBounds',
    //     'option': {'duration': 1.5, 'easeLinearity': 0.2, 'padding': [50, 50]}
    // };

    // Debug Logging on callback //
    console.log(`viewport: ${JSON.stringify(viewport)}`);
                           
    // return [window.dash_clientside.no_update];

    return viewport

    // return [center, zoom]

}


// This is the main object that holds the references to functions for our client callbacks //
window.dash_clientside = Object.assign({}, window.dash_clientside, {
    clientside: {
        updateCMADropdown: cmaDropdownEnablefunction,
        updateCMATransitModeHeader: cmaTransitModeAggStatsSelection,
        updateKeyStatsHeader: cmaKeyStatsHeader,
        updateLeafletMapBounds: cmaLeafletMapBoundsZoom
    }
})



// // Get bounds for the selected CMA
//             if (selectedCMA in allBounds) {
//                 const bounds = allBounds[selectedCMA];
//                 console.log('Bounds found:', bounds);
                
//                 // Find and animate the map
//                 setTimeout(() => {
//                     const mapElement = document.getElementById('dash-leaflet-main-map');
                    
//                     if (!mapElement) {
//                         console.error('Map element not found');
//                         return;
//                     }
                    
//                     console.log('Map element found', mapElement);
                    
//                     // Method 1: Search for Leaflet map in window
//                     let map = null;
                    
//                     if (window.L && window.L.Map) {
//                         // Iterate through all properties in window to find the map
//                         for (let key in window) {
//                             try {
//                                 if (window[key] instanceof L.Map) {
//                                     if (window[key]._container === mapElement || 
//                                         window[key]._container.id === 'dash-leaflet-main-map') {
//                                         map = window[key];
//                                         console.log('Found map via window search');
//                                         break;
//                                     }
//                                 }
//                             } catch(e) {
//                                 // Skip properties that throw errors
//                             }
//                         }
//                     }
                    
//                     // Method 2: Check if map is stored on the element
//                     if (!map && mapElement._leaflet_id) {
//                         console.log('Trying to find map via leaflet_id:', mapElement._leaflet_id);
//                     }
                    
//                     if (map && map.flyToBounds) {
//                         console.log('Calling flyToBounds with:', bounds);
//                         map.flyToBounds(bounds, {
//                             duration: 1.5,
//                             easeLinearity: 0.25,
//                             padding: [50, 50]
//                         });
//                     } else {
//                         console.error('Map not found or flyToBounds not available');
//                     }
//                 }, 100);
                
//                 // Still return bounds as fallback
//                 return bounds;
//             }
            
//             console.log('CMA not found in bounds dictionary');
//             return window.dash_clientside.no_update;
//         }