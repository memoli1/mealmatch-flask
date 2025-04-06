// Handle image loading states
document.addEventListener('DOMContentLoaded', function() {
    const images = document.querySelectorAll('.recipe-image');
    
    images.forEach(img => {
        // Add loading class while image is loading
        img.classList.add('loading');
        
        // Remove loading class when image is loaded
        img.addEventListener('load', function() {
            this.classList.remove('loading');
        });
        
        // Handle image errors
        img.addEventListener('error', function() {
            this.classList.remove('loading');
            this.classList.add('error');
        });
    });
}); 