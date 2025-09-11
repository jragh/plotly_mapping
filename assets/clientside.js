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


// This is the main object that holds the references to functions for our client callbacks //
window.dash_clientside = Object.assign({}, window.dash_clientside, {
    clientside: {
        updateCMADropdown: cmaDropdownEnablefunction,
        updateCMATransitModeHeader: cmaTransitModeAggStatsSelection,
        updateKeyStatsHeader: cmaKeyStatsHeader
    }
})