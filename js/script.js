async function loadComponent(url, elementId) {
    try {
        const response = await fetch(url);
        if (!response.ok) {
            throw new Error(`Failed to fetch ${url}: ${response.statusText}`);
        }
        const text = await response.text();
        const element = document.getElementById(elementId);
        if (element) {
            element.innerHTML = text;
        } else {
            console.error(`Element with id ${elementId} not found.`);
        }
    } catch (error) {
        console.error(`Error loading component from ${url}:`, error);
    }
}

async function loadHeaderAndFooter() {
    // Load header and footer in parallel
    await Promise.all([
        loadComponent('header.html', 'main-header-placeholder'),
        loadComponent('footer.html', 'main-footer-placeholder')
    ]);

    // --- All the original script.js logic goes here ---

    // Header scroll effect
    const header = document.querySelector('.main-header');
    if (header) {
        // Set initial logo state
        const logo = header.querySelector('.logo img');
        if(logo) {
            logo.setAttribute('src', 'assets/logo_trans_landed_white.png');
        }

        window.addEventListener('scroll', () => {
            if (window.scrollY > 50) {
                header.classList.add('scrolled');
                // The logo remains the same based on the original script logic
                if (logo) {
                    logo.setAttribute('src', 'assets/logo_trans_landed_white.png');
                }
            } else {
                header.classList.remove('scrolled');
                if (logo) {
                    logo.setAttribute('src', 'assets/logo_trans_landed_white.png');
                }
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
        const re = /^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$/;
        return re.test(String(email).toLowerCase());
    }
}

document.addEventListener('DOMContentLoaded', loadHeaderAndFooter);