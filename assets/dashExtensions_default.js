window.dashExtensions = Object.assign({}, window.dashExtensions, {
    default: {
        function0: function(feature, context) {
            const {
                style
            } = context.hideout;

            style.fillColor = '#FEB24C';

            return style;
        }
    }
});