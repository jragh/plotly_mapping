window.dashExtensions = Object.assign({}, window.dashExtensions, {
    default: {
        function0: function(feature, layer, context) {

            const p = feature.properties;
            if (!p) {
                return;
            }

            const fmt = function(n) {
                return (n == null) ? '0' : Number(n).toLocaleString('en-US');
            };
            const total = p['Total Commuters To Work'] || 0;
            const pct = function(v) {
                return total > 0 ? ((v / total) * 100).toFixed(1) + '%' : '—';
            };

            const transit = p['Public Transit'] || 0;
            const auto = p['Automobile Drivers'] || 0;
            const carpool = p['Carpool Passengers'] || 0;
            const active = p['Active (Walk, Bike, etc)'] || 0;
            const moto = p['Motorcycle & Similar'] || 0;

            // Inline Material-style SVG glyphs so each mode reads at a glance //
            const PATHS = {
                transit: 'M4 16c0 .88.39 1.67 1 2.22V20c0 .55.45 1 1 1h1c.55 0 1-.45 1-1v-1h8v1c0 .55.45 1 1 1h1c.55 0 1-.45 1-1v-1.78c.61-.55 1-1.34 1-2.22V6c0-3.5-3.58-4-8-4S4 2.5 4 6v10zM7.5 17C6.67 17 6 16.33 6 15.5S6.67 14 7.5 14 9 14.67 9 15.5 8.33 17 7.5 17zM16.5 17c-.83 0-1.5-.67-1.5-1.5s.67-1.5 1.5-1.5 1.5.67 1.5 1.5-.67 1.5-1.5 1.5zM18 11H6V6h12v5z',
                car: 'M18.92 6.01C18.72 5.42 18.16 5 17.5 5h-11c-.66 0-1.21.42-1.42 1.01L3 12v8c0 .55.45 1 1 1h1c.55 0 1-.45 1-1v-1h12v1c0 .55.45 1 1 1h1c.55 0 1-.45 1-1v-8l-2.08-5.99zM6.5 16C5.67 16 5 15.33 5 14.5S5.67 13 6.5 13 8 13.67 8 14.5 7.33 16 6.5 16zM17.5 16c-.83 0-1.5-.67-1.5-1.5s.67-1.5 1.5-1.5 1.5.67 1.5 1.5-.67 1.5-1.5 1.5zM5 11l1.5-4.5h11L19 11H5z',
                carpool: 'M16 11c1.66 0 2.99-1.34 2.99-3S17.66 5 16 5c-1.66 0-3 1.34-3 3s1.34 3 3 3zM8 11c1.66 0 2.99-1.34 2.99-3S9.66 5 8 5C6.34 5 5 6.34 5 8s1.34 3 3 3zM8 13c-2.33 0-7 1.17-7 3.5V19h14v-2.5c0-2.33-4.67-3.5-7-3.5zM16 13c-.29 0-.62.02-.97.05 1.16.84 1.97 1.97 1.97 3.45V19h6v-2.5c0-2.33-4.67-3.5-7-3.5z',
                bike: 'M15.5 5.5c1.1 0 2-.9 2-2s-.9-2-2-2-2 .9-2 2 .9 2 2 2zM5 12c-2.8 0-5 2.2-5 5s2.2 5 5 5 5-2.2 5-5-2.2-5-5-5zm0 8.5c-1.9 0-3.5-1.6-3.5-3.5s1.6-3.5 3.5-3.5 3.5 1.6 3.5 3.5-1.6 3.5-3.5 3.5zm5.8-10l2.4-2.4.8.8c1.3 1.3 3 2.1 5.1 2.1V9c-1.5 0-2.7-.6-3.6-1.5l-1.9-1.9c-.5-.4-1-.6-1.6-.6s-1.1.2-1.4.6L7.8 8.4c-.4.4-.6.9-.6 1.4 0 .6.2 1.1.6 1.4L11 14v5h2v-6.2l-2.2-2.3zM19 12c-2.8 0-5 2.2-5 5s2.2 5 5 5 5-2.2 5-5-2.2-5-5-5zm0 8.5c-1.9 0-3.5-1.6-3.5-3.5s1.6-3.5 3.5-3.5 3.5 1.6 3.5 3.5-1.6 3.5-3.5 3.5z',
                moto: 'M19.44 9.03L15.41 5H11v2h3.59l2 2H5c-2.8 0-5 2.2-5 5s2.2 5 5 5c2.46 0 4.45-1.69 4.9-4h1.65l2.77-2.77c-.21.54-.31 1.14-.31 1.77 0 2.76 2.24 5 5 5s5-2.24 5-5c0-2.96-2.57-5.3-5.56-4.97zM7.82 15C7.4 16.15 6.28 17 5 17c-1.63 0-3-1.37-3-3s1.37-3 3-3c1.28 0 2.4.85 2.82 2H5v2h2.82zM19 17c-1.63 0-3-1.37-3-3s1.37-3 3-3 3 1.37 3 3-1.37 3-3 3z'
            };

            const icon = function(key, color) {
                return '<svg class="ct-tt-icon" viewBox="0 0 24 24" width="15" height="15" fill="' + color + '" aria-hidden="true">' +
                    '<path d="' + PATHS[key] + '"></path></svg>';
            };

            const ICON_GREY = '#8a95a1';

            const row = function(label, val, key) {
                return '<div class="ct-tt-row">' +
                    '<span class="ct-tt-label">' + icon(key, ICON_GREY) + label + '</span>' +
                    '<span class="ct-tt-val"><b>' + fmt(val) + '</b> <span class="ct-tt-pct">(' + pct(val) + ')</span></span>' +
                    '</div>';
            };

            const html = '<div class="ct-tt">' +
                '<div class="ct-tt-title">Census Tract ' + (p['CTUID'] || '') + '</div>' +
                '<div class="ct-tt-sub">Total commuters to work: <b>' + fmt(total) + '</b></div>' +
                '<div class="ct-tt-rows">' +
                row('Public transit', transit, 'transit') +
                row('Auto (driver)', auto, 'car') +
                row('Carpool passenger', carpool, 'carpool') +
                row('Active (walk/bike)', active, 'bike') +
                row('Motorcycle &amp; other', moto, 'moto') +
                '</div></div>';

            layer.bindTooltip(html, {
                sticky: true,
                direction: 'top',
                opacity: 1,
                className: 'ct-tooltip'
            });
        },
        function1: function(feature, context) {

            const {
                colorvalues,
                colorscale,
                style,
                colorprop
            } = context.hideout;

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