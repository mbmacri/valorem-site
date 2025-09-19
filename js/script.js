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

    // Header scroll effect
    const header = document.querySelector('.main-header');
    if (header) {
        const logo = header.querySelector('.logo img');
        if(logo) {
            logo.setAttribute('src', 'assets/logo_trans_landed_white.png');
        }

        window.addEventListener('scroll', () => {
            if (window.scrollY > 50) {
                header.classList.add('scrolled');
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

    // New Contact Form Submission Logic with reCAPTCHA
    const contactForm = document.getElementById('contact-form');
    const formMessage = document.getElementById('form-message');

    if (contactForm) {
        contactForm.addEventListener('submit', function (e) {
            e.preventDefault();
            const submitButton = contactForm.querySelector('button[type="submit"]');
            const name = document.getElementById('name').value;
            const email = document.getElementById('email').value;

            // Basic validation
            if (!name.trim() || !email.trim()) {
                formMessage.textContent = 'Please fill in all required fields.';
                formMessage.style.color = 'red';
                return;
            }

            submitButton.disabled = true;
            submitButton.textContent = 'Sending...';
            formMessage.textContent = '';

            grecaptcha.enterprise.ready(async () => {
                try {
                    const token = await grecaptcha.enterprise.execute('6LdoY80rAAAAAEzTd2UIWBCyY4P1kdMct88FkPy8', {action: 'contact'});
                    
                    const formData = {
                        name: name,
                        email: email,
                        company: document.getElementById('company').value,
                        service: document.getElementById('service').value,
                        message: document.getElementById('message').value,
                        recaptcha_token: token
                    };

                    const response = await fetch('https://b6b5fhl9c1.execute-api.us-east-2.amazonaws.com/contact-form', {
                        method: 'POST',
                        headers: {
                            'Content-Type': 'application/json',
                            'Accept': 'application/json'
                        },
                        body: JSON.stringify(formData)
                    });

                    if (response.ok) {
                        formMessage.textContent = 'Thank you for your message! We will get back to you shortly.';
                        formMessage.style.color = 'green';
                        contactForm.reset();
                    } else {
                        const errorData = await response.json();
                        throw new Error(errorData.error || 'An unknown error occurred.');
                    }

                } catch (error) {
                    formMessage.textContent = `An error occurred: ${error.message}`;
                    formMessage.style.color = 'red';
                } finally {
                    submitButton.disabled = false;
                    submitButton.textContent = 'Send Message';
                }
            });
        });
    }

    // New Talent Form Submission Logic
    const talentForm = document.getElementById('talent-form');
    const talentFormMessage = document.getElementById('talent-form-message');

    if (talentForm) {
        talentForm.addEventListener('submit', function (e) {
            e.preventDefault();
            const submitButton = talentForm.querySelector('button[type="submit"]');
            
            // Form field values
            const name = document.getElementById('apply-name').value;
            const email = document.getElementById('apply-email').value;
            const country = document.getElementById('apply-country').value;
            const linkedin = document.getElementById('apply-linkedin').value;
            const expertise = document.getElementById('apply-expertise').value;
            const resume = document.getElementById('apply-resume').value;
            const consent = document.getElementById('apply-consent').checked;

            // Basic validation
            if (!name || !email || !country || !linkedin || !expertise || !resume) {
                talentFormMessage.textContent = 'Please fill in all required fields.';
                talentFormMessage.style.color = 'red';
                return;
            }
            if (!consent) {
                talentFormMessage.textContent = 'You must consent to store your information.';
                talentFormMessage.style.color = 'red';
                return;
            }

            submitButton.disabled = true;
            submitButton.textContent = 'Submitting...';
            talentFormMessage.textContent = '';

            grecaptcha.enterprise.ready(async () => {
                try {
                    const token = await grecaptcha.enterprise.execute('6LdoY80rAAAAAEzTd2UIWBCyY4P1kdMct88FkPy8', {action: 'join_us'});

                    const formData = {
                        name: name,
                        email: email,
                        country: country,
                        linkedin: linkedin,
                        expertise: expertise,
                        resume: resume,
                        recaptcha_token: token
                    };

                    const response = await fetch('https://b6b5fhl9c1.execute-api.us-east-2.amazonaws.com/join-us-form', {
                        method: 'POST',
                        headers: {
                            'Content-Type': 'application/json',
                            'Accept': 'application/json'
                        },
                        body: JSON.stringify(formData)
                    });

                    if (response.ok) {
                        talentFormMessage.textContent = 'Thank you for your application! We will contact you if a suitable opportunity arises.';
                        talentFormMessage.style.color = 'green';
                        talentForm.reset();
                    } else {
                        const errorData = await response.json();
                        throw new Error(errorData.error || 'An unknown error occurred.');
                    }

                } catch (error) {
                    talentFormMessage.textContent = `An error occurred: ${error.message}`;
                    talentFormMessage.style.color = 'red';
                } finally {
                    submitButton.disabled = false;
                    submitButton.textContent = 'Apply Now';
                }
            });
        });
    }
}

document.addEventListener('DOMContentLoaded', loadHeaderAndFooter);
