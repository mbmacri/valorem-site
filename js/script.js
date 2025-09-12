document.addEventListener('DOMContentLoaded', () => {

    // Header scroll effect
    const header = document.querySelector('.main-header');
    if (header) {
        window.addEventListener('scroll', () => {
            if (window.scrollY > 50) {
                header.classList.add('scrolled');
                // Change logo for dark background
                const logo = header.querySelector('.logo img');
                if(logo) logo.setAttribute('src', 'assets/logo_trans_landed_white.png');
            } else {
                header.classList.remove('scrolled');
                // Change logo for transparent background
                const logo = header.querySelector('.logo img');
                if(logo) logo.setAttribute('src', 'assets/logo_trans_landed_white.png');
            }
        });
    }

    // Mobile navigation (hamburger menu)
    const hamburger = document.querySelector('.hamburger');
    const navMenu = document.querySelector('.nav-menu');
    if (hamburger && navMenu) {
        hamburger.addEventListener('click', () => {
            hamburger.classList.toggle('active');
            navMenu.classList.toggle('active');
        });
    }

    // Basic form validation (can be expanded)
    const contactForm = document.querySelector('.contact-form');
    if (contactForm) {
        contactForm.addEventListener('submit', (e) => {
            const email = contactForm.querySelector('#email');
            if (email && !validateEmail(email.value)) {
                e.preventDefault();
                alert('Please enter a valid email address.');
            }
        });
    }

    function validateEmail(email) {
        const re = /^(([^<>()[\\]\\.,;:\s@\"]+(\.[^<>()[\\]\\.,;:\s@\"]+)*)|(\".+\"))@((\[[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}\])|(([a-zA-Z\-0-9]+\.)+[a-zA-Z]{2,}))$/;
        return re.test(String(email).toLowerCase());
    }

    // Accordion for Nearshore Application
    const detailsElement = document.querySelector('.nearshore-apply-details');
    if (detailsElement) {
        // The <details> element handles this natively, but you could add JS for more complex animations if needed.
        // For now, no extra JS is required for the basic open/close functionality.
    }

});
