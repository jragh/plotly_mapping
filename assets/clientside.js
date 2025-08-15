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

        console.log(JSON.stringify(selectedData));

        return [
            selectedData[0]["Public Transit"].toString(),
            selectedData[0]["Pct of Public Transit Commute"].toString(),
            selectedData[0]["Automobile Drivers"].toString(),
            selectedData[0]["Pct of Automobile Driver Commute"].toString()
        ]

    }

    return [window.dash_clientside.no_update, window.dash_clientside.no_update, window.dash_clientside.no_update, window.dash_clientside.no_update];
    

}

// This is the main object that holds the references to functions for our client callbacks //
window.dash_clientside = Object.assign({}, window.dash_clientside, {
    clientside: {
        updateCMADropdown: cmaDropdownEnablefunction,
        updateCMATransitModeHeader: cmaTransitModeAggStatsSelection
    }
})