const API_URL = '/api';

// State for date navigation
let currentDate = null;
let availableDates = [];

document.addEventListener('DOMContentLoaded', () => {
    initTheme();
    loadAvailableDates();
    fetchMenu();
    
    // Poll for updates every 5 minutes (only if viewing today)
    setInterval(() => {
        const today = new Date().toISOString().split('T')[0];
        if (!currentDate || currentDate === today) {
            fetchMenu();
        }
    }, 5 * 60 * 1000);
});

async function loadAvailableDates() {
    try {
        const response = await fetch(`${API_URL}/dates`);
        const data = await response.json();
        availableDates = data.dates || [];
        updateNavButtons();
    } catch (error) {
        console.error("Failed to load dates:", error);
    }
}

function updateNavButtons() {
    const prevBtn = document.getElementById('prev-day-btn');
    const nextBtn = document.getElementById('next-day-btn');
    const todayBtn = document.getElementById('today-btn');
    const today = new Date().toISOString().split('T')[0];
    
    if (!currentDate) {
        currentDate = availableDates[0] || today;
    }
    
    const currentIndex = availableDates.indexOf(currentDate);
    
    // Disable prev if at oldest date
    prevBtn.disabled = currentIndex === -1 || currentIndex >= availableDates.length - 1;
    
    // Disable next if at newest date or today
    nextBtn.disabled = currentIndex <= 0;
    
    // Hide today button if already viewing today/latest
    todayBtn.style.display = (currentDate === today || currentIndex === 0) ? 'none' : 'inline-block';
}

function navigateDay(direction) {
    const currentIndex = availableDates.indexOf(currentDate);
    const newIndex = currentIndex - direction; // dates are DESC, so -1 goes newer, +1 goes older
    
    if (newIndex >= 0 && newIndex < availableDates.length) {
        currentDate = availableDates[newIndex];
        fetchMenuForDate(currentDate);
    }
}

function goToToday() {
    const today = new Date().toISOString().split('T')[0];
    currentDate = availableDates.includes(today) ? today : availableDates[0];
    fetchMenuForDate(currentDate);
}

async function fetchMenuForDate(date) {
    try {
        document.getElementById('menu-container').innerHTML = '<div class="loading">Loading...</div>';
        const response = await fetch(`${API_URL}/menu?date=${date}&t=${new Date().getTime()}`);
        if (!response.ok) {
            if (response.status === 404) throw new Error('Menu not found');
            throw new Error(`Server error: ${response.status}`);
        }
        
        const data = await response.json();
        currentDate = data.date;
        renderMenu(data);
        updateNavButtons();
        
    } catch (error) {
        console.error("Fetch error:", error);
        const container = document.getElementById('menu-container');
        container.innerHTML = `
            <div class="error">
                <p>No menu available for ${date}.</p>
                <button onclick="goToToday()">Go to Latest</button>
            </div>
        `;
        updateNavButtons();
    }
}

function initTheme() {
    const savedTheme = localStorage.getItem('theme');
    if (savedTheme) {
        document.documentElement.setAttribute('data-theme', savedTheme);
        updateThemeButton(savedTheme);
    } else {
        // Check system preference
        if (window.matchMedia && window.matchMedia('(prefers-color-scheme: dark)').matches) {
            updateThemeButton('dark');
        } else {
            updateThemeButton('light');
        }
    }
}

function toggleTheme() {
    const currentTheme = document.documentElement.getAttribute('data-theme');
    let newTheme = 'light';
    
    if (currentTheme === 'dark') {
        newTheme = 'light';
    } else if (currentTheme === 'light') {
        newTheme = 'dark';
    } else {
        // If no attribute is set, check system preference
        if (window.matchMedia && window.matchMedia('(prefers-color-scheme: dark)').matches) {
            newTheme = 'light'; // System is dark, so toggle to light
        } else {
            newTheme = 'dark'; // System is light, so toggle to dark
        }
    }
    
    document.documentElement.setAttribute('data-theme', newTheme);
    localStorage.setItem('theme', newTheme);
    updateThemeButton(newTheme);
}

function updateThemeButton(theme) {
    const btn = document.getElementById('theme-toggle-btn');
    if (theme === 'dark') {
        btn.textContent = '☀️ Light Mode';
        btn.style.backgroundColor = '#f1c40f'; // Yellow for sun
        btn.style.color = '#333';
    } else {
        btn.textContent = '🌙 Dark Mode';
        btn.style.backgroundColor = '#34495e'; // Dark blue for moon
        btn.style.color = 'white';
    }
}

async function fetchMenu() {
    try {
        const url = currentDate 
            ? `${API_URL}/menu?date=${currentDate}&t=${new Date().getTime()}`
            : `${API_URL}/menu?t=${new Date().getTime()}`;
        const response = await fetch(url);
        if (!response.ok) {
            if (response.status === 404) throw new Error('Menu not found');
            throw new Error(`Server error: ${response.status}`);
        }
        
        const data = await response.json();
        currentDate = data.date;
        renderMenu(data);
        updateNavButtons();
        
    } catch (error) {
        console.error("Fetch error:", error);
        const container = document.getElementById('menu-container');
        if (error.message === 'Menu not found') {
            container.innerHTML = `
                <div class="error">
                    <p>No menu available yet for today.</p>
                    <button onclick="forceCheck()">Check Now</button>
                </div>
            `;
        } else {
            container.innerHTML = `
                <div class="error">
                    <p>Error loading menu: ${error.message}</p>
                    <button onclick="location.reload()">Retry</button>
                </div>
            `;
        }
    }
}

async function forceCheck() {
    document.getElementById('menu-container').innerHTML = '<div class="loading">Checking...</div>';
    await fetch(`${API_URL}/check-now`, { method: 'POST' });
    setTimeout(fetchMenu, 1000);
}

async function forceRescan() {
    const btn = document.getElementById('rescan-btn');
    if (!btn) return;
    
    const originalText = btn.textContent;
    btn.textContent = 'Scanning...';
    btn.disabled = true;
    
    try {
        await fetch(`${API_URL}/check-now`, { 
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ force: true })
        });
        // Reload available dates and fetch menu
        await loadAvailableDates();
        await fetchMenu();
    } catch (error) {
        console.error("Rescan failed:", error);
        alert("Failed to rescan menu.");
    } finally {
        btn.textContent = originalText;
        btn.disabled = false;
    }
}

function renderMenu(data) {
    const dateDisplay = document.getElementById('date-display');
    dateDisplay.textContent = `Menu for: ${data.date}`;

    const container = document.getElementById('menu-container');
    
    // Format text content (replace newlines with <br>)
    const plContent = data.content_pl.replace(/\n/g, '<br>');
    const enContent = data.content_en.replace(/\n/g, '<br>');

    let dishesHtml = '';
    if (data.images && data.images.length > 0) {
        dishesHtml = `
            <h3>Extracted Dishes / Wyodrębnione Dania</h3>
            <div class="dish-list">
                ${data.images.map(item => `
                    <div class="dish-item">
                        <div class="dish-pl">${item.pl}</div>
                        <div class="dish-en">${item.en}</div>
                    </div>
                `).join('')}
            </div>
        `;
    }

    container.innerHTML = `
        <div class="menu-card">
            ${dishesHtml}
            <div class="menu-columns">
                <div class="lang-col">
                    <h3>🇵🇱 Polski</h3>
                    <div class="content">${plContent}</div>
                </div>
                <div class="lang-col">
                    <h3>🇬🇧 English</h3>
                    <div class="content">${enContent}</div>
                </div>
            </div>
        </div>
    `;
}

function checkAndNotify(data) {
    const lastSeenDate = localStorage.getItem('lastSeenMenuDate');
    
    if (lastSeenDate !== data.date) {
        // It's a new menu!
        localStorage.setItem('lastSeenMenuDate', data.date);
        
        if (Notification.permission === "granted") {
            new Notification("New Menu Available!", {
                body: "The menu for today has been posted. Click to view.",
                icon: "/favicon.ico" // Optional
            });
        }
    }
}
