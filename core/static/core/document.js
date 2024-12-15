'use strict';


function decodeHtmlEntities(str) {
    // Create a temporary DOM element
    var tempDiv = document.createElement('div');
    // Set the innerHTML to the string, which will decode entities
    tempDiv.innerHTML = str;
    // Return the decoded text
    return tempDiv.textContent || tempDiv.innerText;
}


function loadPdf(url, text, page_number) {
pdfjsLib.getDocument(url).promise.then(function(pdf) {
    pdf.getPage(page_number).then(function(page) {
        var scale = 1.0;
        var viewport = page.getViewport({
            scale: scale
        });

        // Prepare canvas using PDF page dimensions
        var canvas = document.getElementById('the-canvas');
        var context = canvas.getContext('2d');
        canvas.height = viewport.height;
        canvas.width = viewport.width;

        // Render the PDF page into the canvas context
        var renderContext = {
            canvasContext: context,
            viewport: viewport
        };
        page.render(renderContext);

        // Get text content
        page.getTextContent().then(function(textContent) {
            // Get the transformation matrix for the viewport
            var transform = viewport.transform;

            // Iterate over text items to find the position of text to highlight
            let result = [];

            textContent.items.forEach(function(textItem) {
                // Assume you have logic to determine if this textItem should be highlighted
                if (text.includes(textItem.str)) {
                    result.push(textItem);
                } else {
                    // Apply the transformation matrix
                    if (result.length > 10) {
                        var min_x = 1000000;
                        var min_y = 1000000;
                        var max_x = 0;
                        var max_y = 0;

                        var txt = "";

                        for (const textItem of result) {
                            var x = transform[0] * textItem.transform[4] + transform[2] * textItem.transform[5] + transform[4];
                            var y = transform[1] * textItem.transform[4] + transform[3] * textItem.transform[5] + transform[5];

                            // Calculate height and width based on scale
                            var width = textItem.width * scale;
                            var height = textItem.height * scale;

                            min_x = Math.min(min_x, x);
                            min_y = Math.min(min_y, y - height);
                            max_x = Math.max(max_x, x + width);
                            max_y = Math.max(max_y, y);

                            txt += textItem.str;
                        }
                        context.fillStyle = "rgba(256, 256, 0, 0.5)";
                        context.fillRect(min_x, min_y, max_x-min_x, max_y-min_y);
                        console.log(txt);
                    }

                    result = [];
                }
            });
        });
    });
});

}