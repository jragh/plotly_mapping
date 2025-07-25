window.dashExtensions = Object.assign({}, window.dashExtensions, {
    default: {
        function0: function(feature, context) {

            const {
                colorvalues,
                colorscale,
                style,
                colorprop
            } = context.hideout;


            console.log(colorprop);
            const value = feature.properties[colorprop];

            for (let i = 0; i < colorvalues.length; i++) {

                if (value > colorvalues[i]) {
                    style.fillColor = colorscale[i];
                }

            }


            // Style is stored in the hideout //
            // This updates the hideout to include the fillcolor for the given feature //

            return style;
        }
    }
});