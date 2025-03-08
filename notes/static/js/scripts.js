// Set worker source
pdfjsLib.GlobalWorkerOptions.workerSrc = 'https://cdnjs.cloudflare.com/ajax/libs/pdf.js/3.11.174/pdf.worker.min.js';

// PDF viewing logic
function initPDFViewer(url) {
    let pdfDoc = null;
    let pageNum = 1;
    let scale = 1.0;
    const canvas = document.getElementById('pdf-canvas');
    const ctx = canvas.getContext('2d');
    const loader = document.getElementById('pdf-loader');
    const errorDiv = document.getElementById('pdf-error');
    const container = document.getElementById('pdf-container');

    function calculateScale(page) {
        const viewport = page.getViewport({ scale: 1.0 });
        const containerWidth = container.clientWidth - 40; // 40px padding
        const containerHeight = container.clientHeight - 40;
        
        // Calculate scale to fit width and height
        const scaleWidth = containerWidth / viewport.width;
        const scaleHeight = containerHeight / viewport.height;
        
        // Use the smaller scale to ensure PDF fits both dimensions
        return Math.min(scaleWidth, scaleHeight);
    }

    // Load the PDF
    const loadingTask = pdfjsLib.getDocument(url);
    
    loadingTask.onProgress = function(progress) {
        console.log('Loading progress:', Math.round(progress.loaded / progress.total * 100) + '%');
    };

    loadingTask.promise
        .then(function(pdf) {
            console.log('PDF loaded successfully');
            pdfDoc = pdf;
            document.getElementById('page_count').textContent = pdf.numPages;
            return renderPage(pageNum);
        })
        .catch(function(error) {
            console.error('Error loading PDF:', error);
            loader.style.display = 'none';
            errorDiv.style.display = 'flex';
            errorDiv.querySelector('p').textContent = 'Error loading PDF: ' + error.message;
        });

    function renderPage(num) {
        console.log('Rendering page:', num);
        loader.style.display = 'flex';
        errorDiv.style.display = 'none';
        
        pdfDoc.getPage(num).then(function(page) {
            console.log('Page loaded successfully');
            
            // Calculate the base scale that fits the container
            const baseScale = calculateScale(page);
            const viewport = page.getViewport({ scale: baseScale * scale });
            
            // Set canvas dimensions
            canvas.height = viewport.height;
            canvas.width = viewport.width;

            const renderContext = {
                canvasContext: ctx,
                viewport: viewport
            };

            return page.render(renderContext).promise.then(function() {
                console.log('Page rendered successfully');
                loader.style.display = 'none';
                document.getElementById('page_num').textContent = num;

                // Center scroll position after zoom
                if (scale > 1.0) {
                    const scrollX = (canvas.width - container.clientWidth) / 2;
                    const scrollY = (canvas.height - container.clientHeight) / 2;
                    container.scrollTo(scrollX, scrollY);
                }
            }).catch(function(error) {
                console.error('Error rendering page:', error);
                loader.style.display = 'none';
                errorDiv.style.display = 'flex';
                errorDiv.querySelector('p').textContent = 'Error rendering page: ' + error.message;
            });
        }).catch(function(error) {
            console.error('Error loading page:', error);
            loader.style.display = 'none';
            errorDiv.style.display = 'flex';
            errorDiv.querySelector('p').textContent = 'Error loading page: ' + error.message;
        });
    }

    // Button handlers
    document.getElementById('prev').addEventListener('click', function() {
        if (pageNum <= 1) return;
        pageNum--;
        renderPage(pageNum);
    });

    document.getElementById('next').addEventListener('click', function() {
        if (pageNum >= pdfDoc.numPages) return;
        pageNum++;
        renderPage(pageNum);
    });

    document.getElementById('zoomIn').addEventListener('click', function() {
        scale *= 1.2;
        renderPage(pageNum);
    });

    document.getElementById('zoomOut').addEventListener('click', function() {
        scale *= 0.8;
        renderPage(pageNum);
    });

    // Handle window resize
    window.addEventListener('resize', function() {
        renderPage(pageNum);
    });
}

// Initialize PDF viewer when DOM is loaded
document.addEventListener('DOMContentLoaded', function() {
    const pdfCanvas = document.getElementById('pdf-canvas');
    if (pdfCanvas) {
        const url = pdfCanvas.dataset.pdfUrl;
        if (url) {
            initPDFViewer(url);
        }
    }
}); 