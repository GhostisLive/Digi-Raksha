document.addEventListener('DOMContentLoaded', () => {
    const authContainer = document.getElementById('auth-container');
    const appContainer = document.getElementById('app-container');
    const loginScreen = document.getElementById('loginScreen');
    const registrationScreen = document.getElementById('registrationScreen');
    const loginForm = document.getElementById('login-form');
    const registrationForm = document.getElementById('registration-form');
    const showRegisterLink = document.getElementById('show-register-link');
    const showLoginLink = document.getElementById('show-login-link');
    const photoUpload = document.getElementById('photo-upload');
    const imagePreview = document.getElementById('image-preview');
    const uploadPrompt = document.getElementById('upload-prompt');
    
    const pages = document.querySelectorAll('.page');
    const navButtons = document.querySelectorAll('.nav-btn');
    const tabButtons = document.querySelectorAll('.tab-btn');
    const languageSelector = document.getElementById('languageSelector');

    // --- App State ---
    let currentUser = null; // Store current user info
    let missingPersons = [];
    let communityPosts = [
        { category: 'Water', message: 'Family of 4 needs drinking water near the old temple.', location: 'Old town', time: '1h ago'},
        { category: 'Volunteer', message: 'I have a truck and can help transport supplies or people.', location: 'Central Market', time: '2h ago'},
    ];
    let familyMembers = [
        { name: 'Rohan Sharma', status: 'Safe'},
        { name: 'Priya Sharma', status: 'Unknown'},
        { name: 'Amit Singh', status: 'Safe'},
    ];
    let sosCalls = [];
    
    // --- Translations ---
    const translations = {
        en: {
            appName: 'Digi-रक्षा',
            appSubtitle: 'An Initiative by the Government of India',
            sos: 'SOS',
            markMe: 'Mark Me',
            safe: 'Safe',
            yourLocation: 'Your Location',
            potentialRisks: 'Potential Risks:',
            communityTitle: 'Community Feed',
            newPost: 'New Post',
            submitPost: 'Submit Post',
            announcements: 'Announcements',
            helpRequests: 'Help Requests',
            alertsTitle: 'Alerts & Warnings',
            missingPersonsTitle: 'Missing Persons Registry',
            nearbySos: 'Nearby SOS Calls',
            familyStatus: 'Family Status',
            searchRegistry: 'Search Registry',
            reportMissing: 'Report Missing',
            submitReport: 'Submit Report',
            navHome: 'Home',
            navAlerts: 'Alerts',
            navCommunity: 'Community',
            navMissing: 'Missing',
            reportIncident: 'Report Incident',
            takePhoto: 'Take Photo',
            recordAudio: 'Record Audio',
            shareLocation: 'Share Location',
            reportIncidentTitle: 'Report an Incident',
            incidentType: 'Select Incident Type...',
            incidentDescription: 'Describe the incident...',
            attachPhoto: 'Attach Photo',
            incidentLocation: 'Location (e.g., street name, landmark)',
            submitIncident: 'Submit Incident Report',
            addFamilyTitle: 'Add Family Member',
            newMemberNamePlaceholder: 'Full Name',
            addMemberBtn: 'Add Member',
        },
        hi: {
            appName: 'डिजी-रक्षा',
            appSubtitle: 'भारत सरकार की एक पहल',
            sos: 'मदद',
            markMe: 'मुझे',
            safe: 'सुरक्षित करें',
            yourLocation: 'आपका स्थान',
            potentialRisks: 'संभावित खतरे:',
            communityTitle: 'कम्युनिटी फीड',
            newPost: 'नई पोस्ट',
            submitPost: 'पोस्ट सबमिट करें',
            announcements: 'घोषणाएं',
            helpRequests: 'सहायता अनुरोध',
            alertsTitle: 'चेतावनी और सूचनाएं',
            missingPersonsTitle: 'लापता व्यक्ति रजिस्ट्री',
            nearbySos: 'आस-पास के एसओएस कॉल',
            familyStatus: 'परिवार की स्थिति',
            searchRegistry: 'रजिस्ट्री खोजें',
            reportMissing: 'लापता की रिपोर्ट करें',
            submitReport: 'रिपोर्ट सबमिट करें',
            navHome: 'होम',
            navAlerts: 'चेतावनी',
            navCommunity: 'समुदाय',
            navMissing: 'लापता',
            reportIncident: 'घटना की रिपोर्ट करें',
            takePhoto: 'फोटो लें',
            recordAudio: 'ऑडियो रिकॉर्ड करें',
            shareLocation: 'स्थान साझा करें',
            reportIncidentTitle: 'एक घटना की रिपोर्ट करें',
            incidentType: 'घटना का प्रकार चुनें...',
            incidentDescription: 'घटना का वर्णन करें...',
            attachPhoto: 'फोटो संलग्न करें',
            incidentLocation: 'स्थान (उदा. गली का नाम, लैंडमार्क)',
            submitIncident: 'घटना रिपोर्ट सबमिट करें',
            addFamilyTitle: 'परिवार का सदस्य जोड़ें',
            newMemberNamePlaceholder: 'पूरा नाम',
            addMemberBtn: 'सदस्य जोड़ें',
        },
        bn: {
            appName: 'ডিজি-রক্ষা',
            appSubtitle: 'ভারত সরকারের একটি উদ্যোগ',
            sos: 'SOS',
            markMe: 'আমাকে',
            safe: 'নিরাপদ করুন',
            yourLocation: 'আপনার অবস্থান',
            potentialRisks: 'সম্ভাব্য ঝুঁকি:',
            communityTitle: 'কমিউনিটি ফিড',
            newPost: 'নতুন পোস্ট',
            submitPost: 'পোস্ট জমা দিন',
            announcements: 'ঘোষণা',
            helpRequests: 'সাহায্যের অনুরোধ',
            alertsTitle: 'সতর্কতা এবং বিজ্ঞপ্তি',
            missingPersonsTitle: 'নিখোঁজ ব্যক্তি রেজিস্ট্রি',
            nearbySos: 'কাছাকাছি এসওএস কল',
            familyStatus: 'পরিবারের অবস্থা',
            searchRegistry: 'রেজিস্ট্রি অনুসন্ধান করুন',
            reportMissing: 'নিখোঁজ রিপোর্ট করুন',
            submitReport: 'রিপোর্ট জমা দিন',
            navHome: 'হোম',
            navAlerts: 'সতর্কতা',
            navCommunity: 'কমিউনিটি',
            navMissing: 'নিখোঁজ',
            reportIncident: 'ঘটনা রিপোর্ট করুন',
            takePhoto: 'ছবি তুলুন',
            recordAudio: 'অডিও রেকর্ড করুন',
            shareLocation: 'অবস্থান শেয়ার করুন',
            reportIncidentTitle: 'একটি ঘটনা রিপোর্ট করুন',
            incidentType: 'ঘটনার ধরন নির্বাচন করুন...',
            incidentDescription: 'ঘটনাটি বর্ণনা করুন...',
            attachPhoto: 'ছবি সংযুক্ত করুন',
            incidentLocation: 'অবস্থান (যেমন রাস্তার নাম, ল্যান্ডমার্ক)',
            submitIncident: 'ঘটনা রিপোর্ট জমা দিন',
            addFamilyTitle: 'পরিবারের সদস্য যোগ করুন',
            newMemberNamePlaceholder: 'পুরো নাম',
            addMemberBtn: 'সদস্য যোগ করুন',
        },
        gu: {
            appName: 'ડિજિ-રક્ષા',
            appSubtitle: 'ભારત સરકારની એક પહેલ',
            sos: 'SOS',
            markMe: 'મને',
            safe: 'સુરક્ષિત કરો',
            yourLocation: 'તમારું સ્થાન',
            potentialRisks: 'સંભવિત જોખમો:',
            communityTitle: 'કમ્યુનિટિ ફીડ',
            newPost: 'નવી પોસ્ટ',
            submitPost: 'પોસ્ટ સબમિટ કરો',
            announcements: 'જાહેરાતો',
            helpRequests: 'મદદ માટે વિનંતીઓ',
            alertsTitle: 'ચેતવણીઓ અને સૂચનાઓ',
            missingPersonsTitle: 'ગુમ થયેલ વ્યક્તિઓની રજિસ્ટ્રી',
            nearbySos: 'નજીકના એસઓએસ કોલ્સ',
            familyStatus: 'કૌટુંબિક સ્થિતિ',
            searchRegistry: 'રજિસ્ટ્રી શોધો',
            reportMissing: 'ગુમ થયાની જાણ કરો',
            submitReport: 'રિપોર્ટ સબમિટ કરો',
            navHome: 'હોમ',
            navAlerts: 'ચેતવણીઓ',
            navCommunity: 'કમ્યુનિટિ',
            navMissing: 'ગુમ થયેલ',
            reportIncident: 'ઘટનાની જાણ કરો',
            takePhoto: 'ફોટો લો',
            recordAudio: 'ઓડિયો રેકોર્ડ કરો',
            shareLocation: 'સ્થાન શેર કરો',
            reportIncidentTitle: 'એક ઘટનાની જાણ કરો',
            incidentType: 'ઘટનાનો પ્રકાર પસંદ કરો...',
            incidentDescription: 'ઘટનાનું વર્ણન કરો...',
            attachPhoto: 'ફોટો જોડો',
            incidentLocation: 'સ્થાન (દા.ત. શેરીનું નામ, સીમાચિહ્ન)',
            submitIncident: 'ઘટના અહેવાલ સબમિટ કરો',
            addFamilyTitle: 'પરિવારના સભ્યને ઉમેરો',
            newMemberNamePlaceholder: 'પૂરું નામ',
            addMemberBtn: 'સભ્ય ઉમેરો',
        },
        or: {
            appName: 'ଡିଜି-ରକ୍ଷା',
            appSubtitle: 'ଭାରତ ସରକାରଙ୍କ ଏକ ପଦକ୍ଷେପ',
            sos: 'SOS',
            markMe: 'ମୋତେ',
            safe: 'ସୁରକ୍ଷିତ କରନ୍ତୁ',
            yourLocation: 'ଆପଣଙ୍କ ସ୍ଥାନ',
            potentialRisks: 'ସମ୍ଭାବ୍ୟ ବିପଦ:',
            communityTitle: 'କମ୍ୟୁନିଟି ଫିଡ୍',
            newPost: 'ନୂଆ ପୋଷ୍ଟ',
            submitPost: 'ପୋଷ୍ଟ ଦାଖଲ କରନ୍ତୁ',
            announcements: 'ଘୋଷଣା',
            helpRequests: 'ସାହାଯ୍ୟ ଅନୁରୋଧ',
            alertsTitle: 'ସତର୍କତା ଏବଂ ଚେତାବନୀ',
            missingPersonsTitle: 'ନିଖୋଜ ବ୍ୟକ୍ତିଙ୍କ ରେଜିଷ୍ଟ୍ରି',
            nearbySos: 'ନିକଟବର୍ତ୍ତୀ SOS କଲ୍',
            familyStatus: 'ପରିବାର ସ୍ଥିତି',
            searchRegistry: 'ରେଜିଷ୍ଟ୍ରି ଖୋଜନ୍ତୁ',
            reportMissing: 'ନିଖୋଜ ରିପୋର୍ଟ କରନ୍ତୁ',
            submitReport: 'ରିପୋର୍ଟ ଦାଖଲ କରନ୍ତୁ',
            navHome: 'ହୋମ୍',
            navAlerts: 'ସତର୍କତା',
            navCommunity: 'କମ୍ୟୁନିଟି',
            navMissing: 'ନିଖୋଜ',
            reportIncident: 'ଘଟଣା ରିପୋର୍ଟ କରନ୍ତୁ',
            takePhoto: 'ଫଟୋ ନିଅନ୍ତୁ',
            recordAudio: 'ଅଡିଓ ରେକର୍ଡ କରନ୍ତୁ',
            shareLocation: 'ଅବସ୍ଥାନ ସେୟାର କରନ୍ତୁ',
            reportIncidentTitle: 'ଏକ ଘଟଣା ରିପୋର୍ଟ କରନ୍ତୁ',
            incidentType: 'ଘଟଣାର ପ୍ରକାର ଚୟନ କରନ୍ତୁ...',
            incidentDescription: 'ଘଟଣା ବର୍ଣ୍ଣନା କରନ୍ତୁ...',
            attachPhoto: 'ଫଟୋ ସଂଲଗ୍ନ କରନ୍ତୁ',
            incidentLocation: 'ଅବସ୍ଥାନ (ଯଥା, ରାସ୍ତା ନାମ, ସ୍ଥାନ ଚିହ୍ନ)',
            submitIncident: 'ଘଟଣା ରିପୋର୍ଟ ଦାଖଲ କରନ୍ତୁ',
            addFamilyTitle: 'ପରିବାର ସଦସ୍ୟ ଯୋଗ କରନ୍ତୁ',
            newMemberNamePlaceholder: 'ପୂରା ନାମ',
            addMemberBtn: 'ସଦସ୍ୟ ଯୋଗ କରନ୍ତୁ',
        },
    };

    function updateUI(lang) {
        const langPack = translations[lang];
        document.getElementById('app-title').textContent = langPack.appName;
        document.getElementById('app-subtitle').textContent = langPack.appSubtitle;
        document.querySelector('#sosButton').textContent = langPack.sos;
        document.querySelector('#safeButton > span[data-translate="markMe"]').textContent = langPack.markMe;
        document.querySelector('#safeButton > span[data-translate="safe"]').textContent = langPack.safe;

        document.querySelectorAll('[data-translate]').forEach(el => {
            const key = el.dataset.translate;
            if(langPack[key]) {
                if (!el.parentElement.matches('#safeButton')) {
                   el.textContent = langPack[key];
                }
            }
        });
        
        document.querySelectorAll('[data-translate-placeholder]').forEach(el => {
            const key = el.dataset.translatePlaceholder;
            if (langPack[key]) {
                el.placeholder = langPack[key];
            }
        });
    }
    
    languageSelector.addEventListener('change', (e) => updateUI(e.target.value));

    // --- Auth Flow ---
    function showAuthScreen(screenId) {
        document.querySelectorAll('.auth-page').forEach(s => s.classList.remove('active'));
        document.getElementById(screenId).classList.add('active');
    }

    showRegisterLink.addEventListener('click', (e) => {
        e.preventDefault();
        showAuthScreen('registrationScreen');
    });
     showLoginLink.addEventListener('click', (e) => {
        e.preventDefault();
        showAuthScreen('loginScreen');
    });

    function enterMainApp() {
        authContainer.classList.add('hidden');
        appContainer.classList.remove('hidden');
        initializeMainApp();
    }

    loginForm.addEventListener('submit', async (e) => {
        e.preventDefault();
        
        try {
            const formData = new FormData();
            formData.append('gov_id_number', document.getElementById('login-gov-id').value);
            formData.append('password', document.getElementById('login-password').value);
            
            const response = await fetch('/api/auth/login', {
                method: 'POST',
                body: formData
            });
            
            if (response.ok) {
                const result = await response.json();
                currentUser = result.user; // Store user info
                enterMainApp();
            } else {
                const error = await response.json();
                alert(error.detail || 'Login failed');
            }
        } catch (error) {
            console.error('Login error:', error);
            alert('Login failed. Please try again.');
        }
    });
    
    registrationForm.addEventListener('submit', async (e) => {
        e.preventDefault();
        
        try {
            const formData = new FormData(registrationForm);
            
            const response = await fetch('/api/auth/register', {
                method: 'POST',
                body: formData
            });
            
            if (response.ok) {
                const result = await response.json();
                // Set basic user info for registration
                currentUser = {
                    id: result.user_id,
                    first_name: formData.get('first_name'),
                    last_name: formData.get('last_name')
                };
                enterMainApp();
            } else {
                const error = await response.json();
                alert(error.detail || 'Registration failed');
            }
        } catch (error) {
            console.error('Registration error:', error);
            alert('Registration failed. Please try again.');
        }
    });

     photoUpload.addEventListener('change', function(event) {
        const file = event.target.files[0];
        if (file) {
            const reader = new FileReader();
            reader.onload = function(e) {
                imagePreview.src = e.target.result;
                imagePreview.classList.remove('hidden');
                uploadPrompt.classList.add('hidden');
            }
            reader.readAsDataURL(file);
        }
    });


    // --- Main App Logic ---
    function initializeMainApp() {
        const pages = document.querySelectorAll('.page');
        const navButtons = document.querySelectorAll('.nav-btn');
        const tabButtons = document.querySelectorAll('.tab-btn');
        
        function showPage(pageId) {
            pages.forEach(page => page.classList.remove('active'));
            document.getElementById(pageId).classList.add('active');

            navButtons.forEach(btn => {
                if (btn.dataset.page === pageId) {
                    btn.classList.remove('text-orange-200');
                    btn.classList.add('text-white');
                } else {
                    btn.classList.remove('text-white');
                    btn.classList.add('text-orange-200');
                }
            });
        }
    
        navButtons.forEach(button => {
            button.addEventListener('click', () => {
                showPage(button.dataset.page);
            });
        });

        tabButtons.forEach(button => {
            button.addEventListener('click', () => {
                const tabId = button.dataset.tab;
                document.querySelectorAll('.tab-content').forEach(c => c.classList.add('hidden'));
                document.getElementById(tabId).classList.remove('hidden');

                tabButtons.forEach(b => {
                    b.classList.remove('active', 'text-orange-600', 'border-orange-500');
                    b.classList.add('text-gray-500', 'border-transparent');
                });
                button.classList.add('active', 'text-orange-600', 'border-orange-500');
                button.classList.remove('text-gray-500', 'border-transparent');
            });
        });

        const modal = document.getElementById('modal');
        const modalTitle = document.getElementById('modal-title');
        const modalText = document.getElementById('modal-text');
        const modalConfirm = document.getElementById('modal-confirm');
        const modalCancel = document.getElementById('modal-cancel');
        let confirmCallback = null;

        function showModal(title, text, confirmText = 'Confirm', onConfirm) {
            modalTitle.textContent = title;
            modalText.textContent = text;
            modalConfirm.textContent = confirmText;
            modal.classList.remove('hidden');
            modal.classList.add('flex');
            confirmCallback = onConfirm;
        }

        function hideModal() {
            modal.classList.add('hidden');
            modal.classList.remove('flex');
            confirmCallback = null;
        }

        modalCancel.addEventListener('click', hideModal);
        modalConfirm.addEventListener('click', () => {
            if(confirmCallback) confirmCallback();
            hideModal();
        });

        const locationText = document.getElementById('location-text');
        const riskText = document.getElementById('risk-text');
        const sosButton = document.getElementById('sosButton');
        const safeButton = document.getElementById('safeButton');
        const reportIncidentBtn = document.getElementById('reportIncidentBtn');

        function getUserLocation() {
            if (navigator.geolocation) {
                navigator.geolocation.getCurrentPosition(position => {
                    const { latitude, longitude } = position.coords;
                    locationText.textContent = `Lat: ${latitude.toFixed(2)}, Lon: ${longitude.toFixed(2)}`;
                    riskText.textContent = 'Floods, Severe Thunderstorms';
                }, () => {
                    locationText.textContent = 'Location access denied.';
                    riskText.textContent = 'Cannot assess risks without location.';
                });
            } else {
                locationText.textContent = 'Geolocation is not supported by this browser.';
            }
        }
        
        sosButton.addEventListener('click', () => {
            showModal('Confirm SOS', 'This will send a distress signal to emergency services. Are you sure?', 'SEND SOS', async () => {
                try {
                    // Get user's current location
                    if (navigator.geolocation) {
                        navigator.geolocation.getCurrentPosition(async (position) => {
                            const { latitude, longitude } = position.coords;
                            
                            // Create FormData for SOS alert
                            const formData = new FormData();
                            formData.append('latitude', latitude);
                            formData.append('longitude', longitude);
                            formData.append('location_description', `Emergency at Lat: ${latitude.toFixed(4)}, Lon: ${longitude.toFixed(4)}`);
                            formData.append('emergency_type', 'urgent');
                            formData.append('user_name', currentUser?.first_name || 'Anonymous User');
                            
                            // Use currentUser ID if available, otherwise get first available user ID
                            let userId = currentUser?.id;
                            if (!userId) {
                                try {
                                    const usersResponse = await fetch('/api/users');
                                    if (usersResponse.ok) {
                                        const usersData = await usersResponse.json();
                                        if (usersData.users && usersData.users.length > 0) {
                                            userId = usersData.users[0].id;
                                        }
                                    }
                                } catch (e) {
                                    console.error('Failed to get fallback user ID:', e);
                                }
                            }
                            
                            if (!userId) {
                                showModal('Error', 'Unable to send SOS alert. Please try logging in first.', 'OK', () => {});
                                return;
                            }
                            
                            formData.append('user_id', userId);
                            
                            // Send SOS alert to backend
                            const response = await fetch('/api/sos', {
                                method: 'POST',
                                body: formData
                            });
                            
                            if (response.ok) {
                                const result = await response.json();
                                showModal('SOS Sent', 'Your distress signal has been sent. Help is on the way.', 'OK', () => {
                                    // Reload SOS alerts to show the new one
                                    loadSOSAlerts();
                                });
                            } else {
                                const error = await response.json();
                                showModal('Error', 'Failed to send SOS alert. Please try again.', 'OK', () => {});
                            }
                        }, () => {
                            // Location access denied
                            showModal('Location Required', 'Location access is required to send SOS alerts. Please enable location services.', 'OK', () => {});
                        });
                    } else {
                        showModal('Error', 'Geolocation is not supported by this browser.', 'OK', () => {});
                    }
                } catch (error) {
                    console.error('Error sending SOS alert:', error);
                    showModal('Error', 'Failed to send SOS alert. Please try again.', 'OK', () => {});
                }
            });
        });

        safeButton.addEventListener('click', () => {
            showModal('Mark as Safe', `This will notify authorities that you are safe.`, 'NOTIFY', () => {
                showModal('Notification Sent', 'You have been marked as safe.', 'OK', () => {});
            });
        });

        reportIncidentBtn.addEventListener('click', () => {
            showPage('reportIncidentPage');
        });

        const newPostBtn = document.getElementById('newPostBtn');
        const newPostFormContainer = document.getElementById('newPostFormContainer');
        const newPostForm = document.getElementById('newPostForm');
        const communityPostsContainer = document.getElementById('communityPosts');
        const categoryColors = {
            'Food': 'bg-green-100 text-green-800',
            'Water': 'bg-blue-100 text-blue-800',
            'Medical': 'bg-red-100 text-red-800',
            'Rescue': 'bg-yellow-100 text-yellow-800',
            'Volunteer': 'bg-purple-100 text-purple-800',
        }

        newPostBtn.addEventListener('click', () => {
            newPostFormContainer.classList.toggle('hidden');
        });

        function renderCommunityPosts() {
            console.log('Rendering community posts:', communityPosts.length, 'posts');
            communityPostsContainer.innerHTML = '';
            if (communityPosts.length === 0) {
                 communityPostsContainer.innerHTML = `<p class="text-center text-gray-500">No posts or alerts yet.</p>`;
                 return;
            }
            communityPosts.forEach((post, index) => {
                console.log(`Rendering post ${index + 1}:`, post.post_type, post.category);
                const postEl = document.createElement('div');
                
                // Different styling for incidents vs regular community posts
                if (post.post_type === 'incident') {
                    postEl.className = 'bg-red-50 border border-red-200 p-3 rounded-lg';
                    
                    const timeAgo = new Date(post.created_at).toLocaleString();
                    postEl.innerHTML = `
                        <div class="flex justify-between items-center mb-1">
                            <span class="text-xs font-semibold px-2 py-0.5 rounded-full bg-red-100 text-red-800">⚠️ ${post.category}</span>
                            <span class="text-xs text-gray-400">${timeAgo}</span>
                        </div>
                        <p class="text-gray-700 font-medium">${post.message}</p>
                        <p class="text-xs text-gray-600 mt-1">📍 ${post.location}</p>
                        <p class="text-xs text-red-600 mt-1">Status: ${post.status.charAt(0).toUpperCase() + post.status.slice(1)}</p>
                        ${post.image_url ? `<img src="${post.image_url}" alt="Incident Evidence" class="mt-2 w-full h-32 object-cover rounded-md" onerror="this.style.display='none'">` : ''}
                        <p class="text-xs text-gray-500 mt-2">🏛️ ${post.user_name}</p>
                    `;
                } else {
                    // Regular community post
                    postEl.className = 'bg-white border p-3 rounded-lg';
                    const timeAgo = post.time || new Date(post.created_at).toLocaleString();
                    postEl.innerHTML = `
                        <div class="flex justify-between items-center mb-1">
                            <span class="text-xs font-semibold px-2 py-0.5 rounded-full ${categoryColors[post.category] || 'bg-gray-100 text-gray-800'}">${post.category}</span>
                            <span class="text-xs text-gray-400">${timeAgo}</span>
                        </div>
                        <p class="text-gray-700">${post.message}</p>
                        <p class="text-xs text-gray-500 mt-1">📍 ${post.location}</p>
                        ${post.image_url ? `<img src="${post.image_url}" alt="Post Image" class="mt-2 w-full h-32 object-cover rounded-md" onerror="this.style.display='none'">` : ''}
                        <p class="text-xs text-gray-500 mt-1">👤 ${post.user_name || 'Anonymous'}</p>
                    `;
                }
                
                communityPostsContainer.appendChild(postEl);
            });
        }

        // Load community feed (includes both posts and incidents)
        async function loadCommunityFeed() {
            try {
                // Add cache busting parameter to ensure fresh data
                const timestamp = new Date().getTime();
                const response = await fetch(`/api/community/feed?t=${timestamp}`);
                if (response.ok) {
                    const data = await response.json();
                    communityPosts = data.posts || [];
                    renderCommunityPosts();
                    console.log('Community feed loaded:', data.count, 'posts');
                } else {
                    console.error('Failed to load community feed');
                }
            } catch (error) {
                console.error('Error loading community feed:', error);
            }
        }

         newPostForm.addEventListener('submit', (e) => {
            e.preventDefault();
            const newPost = {
                category: document.getElementById('postCategory').value,
                message: document.getElementById('postMessage').value,
                location: 'Near your location',
                time: 'Just now',
                post_type: 'community',
                user_name: currentUser?.first_name || 'Anonymous'
            };
            communityPosts.unshift(newPost);
            renderCommunityPosts();
            newPostForm.reset();
            newPostFormContainer.classList.add('hidden');
            
            // TODO: Submit to backend API as well
            // For now, just adding to local state
        });

        const sosCallsContainer = document.getElementById('sos-calls-container');

        function renderSosCalls() {
            sosCallsContainer.innerHTML = '';
            if (sosCalls.length === 0) {
                sosCallsContainer.innerHTML = `<p class="text-center text-gray-500">No nearby SOS calls.</p>`;
                return;
            }
            sosCalls.forEach(call => {
                const callEl = document.createElement('div');
                callEl.className = 'bg-red-50 border border-red-200 p-4 rounded-lg flex justify-between items-center';
                callEl.innerHTML = `
                    <div>
                        <p class="font-bold text-red-800">${call.name}</p>
                        <p class="text-sm text-red-700">${call.location}</p>
                    </div>
                    <div class="text-right">
                        <p class="text-sm font-semibold text-red-800">${call.time}</p>
                        <button class="text-xs text-orange-600 font-bold hover:underline">VIEW MAP</button>
                    </div>
                `;
                sosCallsContainer.appendChild(callEl);
            });
        }

        const reportIncidentForm = document.getElementById('reportIncidentForm');
        const backToHomeBtn = document.getElementById('backToHomeBtn');
        const incidentPhotoInput = document.getElementById('incidentPhoto');
        const incidentImagePreview = document.getElementById('incidentImagePreview');
        const incidentPreviewImage = document.getElementById('incidentPreviewImage');
        let incidentReports = [];

        // Handle incident photo preview
        if (incidentPhotoInput) {
            incidentPhotoInput.addEventListener('change', function(event) {
                const file = event.target.files[0];
                if (file) {
                    const reader = new FileReader();
                    reader.onload = function(e) {
                        incidentPreviewImage.src = e.target.result;
                        incidentImagePreview.classList.remove('hidden');
                    }
                    reader.readAsDataURL(file);
                } else {
                    incidentImagePreview.classList.add('hidden');
                }
            });
        }

        backToHomeBtn.addEventListener('click', () => showPage('homePage'));

        reportIncidentForm.addEventListener('submit', async (e) => {
            e.preventDefault();
            
            try {
                // Get user ID - use current user or fallback to existing user
                let userId = currentUser?.id;
                if (!userId) {
                    try {
                        const usersResponse = await fetch('/api/users');
                        if (usersResponse.ok) {
                            const usersData = await usersResponse.json();
                            if (usersData.users && usersData.users.length > 0) {
                                userId = usersData.users[0].id;
                            }
                        }
                    } catch (e) {
                        console.error('Failed to get fallback user ID:', e);
                    }
                }
                
                if (!userId) {
                    showModal('Error', 'Unable to submit incident report. Please try logging in first.', 'OK');
                    return;
                }
                
                // Create FormData to handle file uploads and form data
                const formData = new FormData();
                formData.append('incident_type', document.getElementById('incidentType').value);
                formData.append('description', document.getElementById('incidentDescription').value);
                formData.append('location', document.getElementById('incidentLocation').value);
                formData.append('user_id', userId);
                
                // Add photo if selected
                const incidentPhoto = document.getElementById('incidentPhoto');
                console.log('Incident photo element:', incidentPhoto);
                console.log('Files selected:', incidentPhoto ? incidentPhoto.files.length : 0);
                
                if (incidentPhoto && incidentPhoto.files[0]) {
                    const file = incidentPhoto.files[0];
                    console.log('Uploading file:', file.name, 'Size:', file.size, 'Type:', file.type);
                    formData.append('incident_image', file);
                } else {
                    console.log('No photo selected');
                }
                
                console.log('Submitting incident report to API...');
                
                // Submit to backend API
                const response = await fetch('/api/incidents', {
                    method: 'POST',
                    body: formData
                });
                
                if (response.ok) {
                    const result = await response.json();
                    console.log('Incident reported successfully:', result);
                    reportIncidentForm.reset();
                    showModal('Incident Reported', 'Your incident report has been submitted and will appear in the community feed.', 'OK', () => {
                        showPage('homePage');
                        // Refresh community feed to show new incident
                        loadCommunityFeed();
                    });
                } else {
                    const error = await response.json();
                    console.error('Failed to submit incident:', error);
                    showModal('Error', error.detail || 'Failed to submit incident report', 'OK');
                }
            } catch (error) {
                console.error('Error submitting incident report:', error);
                showModal('Error', 'Failed to submit incident report. Please try again.', 'OK');
            }
        });

        const reportMissingForm = document.getElementById('reportMissingForm');
        const missingPersonsList = document.getElementById('missingPersonsList');
        const searchMissingInput = document.getElementById('searchMissingInput');
        const familyStatusList = document.getElementById('familyStatusList');
        const addFamilyBtn = document.getElementById('addFamilyBtn');
        const backToMissingBtn = document.getElementById('backToMissingBtn');
        const addFamilyMemberForm = document.getElementById('addFamilyMemberForm');

        addFamilyBtn.addEventListener('click', () => showPage('addFamilyMemberPage'));
        backToMissingBtn.addEventListener('click', () => showPage('missingPersonsPage'));

        addFamilyMemberForm.addEventListener('submit', (e) => {
            e.preventDefault();
            const newMemberNameInput = document.getElementById('newMemberName');
            const newName = newMemberNameInput.value.trim();
            if (newName) {
                familyMembers.unshift({ name: newName, status: 'Safe' });
                renderFamilyStatus();
                addFamilyMemberForm.reset();
                showPage('missingPersonsPage');
            }
        });

        function renderFamilyStatus() {
            familyStatusList.innerHTML = '';
            familyMembers.forEach(member => {
                const statusClass = member.status === 'Safe' ? 'bg-green-100 text-green-800' : 'bg-gray-200 text-gray-800';
                const li = document.createElement('div');
                li.className = 'bg-gray-50 p-3 rounded-lg flex justify-between items-center border';
                li.innerHTML = `
                    <span class="font-medium text-gray-700">${member.name}</span>
                    <span class="text-xs font-semibold px-2.5 py-1 rounded-full ${statusClass}">${member.status}</span>
                `;
                familyStatusList.appendChild(li);
            });
        }

        function renderMissingPersons(filter = '') {
            missingPersonsList.innerHTML = '';
            const filteredList = missingPersons.filter(p => p.name.toLowerCase().includes(filter.toLowerCase()));
            
            if(filteredList.length === 0) {
                missingPersonsList.innerHTML = `<li class="text-center text-gray-500">No reports found.</li>`;
            }
            filteredList.forEach(person => {
                 const personCard = document.createElement('div');
                 personCard.className = 'bg-gray-50 p-4 rounded-lg flex items-center space-x-4 border';
                 
                 // Use actual photo URL if available, otherwise use placeholder
                 const photoUrl = person.photo_url || person.photo || 'https://placehold.co/80x80/EFEFEF/333333?text=Person';
                 
                 personCard.innerHTML = `
                    <img src="${photoUrl}" alt="Missing Person" class="w-20 h-20 rounded-md object-cover bg-gray-300" onerror="this.src='https://placehold.co/80x80/EFEFEF/333333?text=Person'">
                    <div>
                        <h4 class="font-bold text-gray-800">${person.name}</h4>
                        <p class="text-sm text-gray-600">Age: ${person.age}, Last Seen: ${person.last_seen_location || person.lastSeen}</p>
                        <p class="text-sm text-gray-600">${person.description}</p>
                        <p class="text-xs mt-1 text-gray-500">Contact: ${person.reporter_contact || person.reporter}</p>
                    </div>
                 `;
                 missingPersonsList.appendChild(personCard);
            });
        }

        // Load missing persons from API
        async function loadMissingPersons() {
            try {
                const response = await fetch('/api/missing');
                if (response.ok) {
                    const data = await response.json();
                    missingPersons = data.missing_persons || [];
                    renderMissingPersons();
                } else {
                    console.error('Failed to load missing persons');
                }
            } catch (error) {
                console.error('Error loading missing persons:', error);
            }
        }

        // Load SOS alerts from API
        async function loadSOSAlerts() {
            try {
                const response = await fetch('/api/sos');
                if (response.ok) {
                    const data = await response.json();
                    sosCalls = data.alerts || [];
                    // Transform the API data to match the frontend format
                    sosCalls = sosCalls.map(alert => ({
                        name: alert.user_name || 'Anonymous',
                        location: alert.location_description || `Lat: ${alert.latitude}, Lon: ${alert.longitude}`,
                        time: new Date(alert.created_at).toLocaleString(),
                        emergency_type: alert.emergency_type || 'General',
                        latitude: alert.latitude,
                        longitude: alert.longitude,
                        id: alert.id
                    }));
                    renderSosCalls();
                } else {
                    console.error('Failed to load SOS alerts');
                }
            } catch (error) {
                console.error('Error loading SOS alerts:', error);
            }
        }

        reportMissingForm.addEventListener('submit', async (e) => {
            e.preventDefault();
            
            try {
                const formData = new FormData();
                formData.append('name', document.getElementById('missingName').value);
                formData.append('age', document.getElementById('missingAge').value);
                formData.append('last_seen_location', document.getElementById('lastSeen').value);
                formData.append('description', document.getElementById('missingDescription').value);
                formData.append('reporter_contact', document.getElementById('reporterContact').value);
                formData.append('user_id', currentUser?.id || 'anonymous');
                
                // Add photo if selected
                const photoFile = document.getElementById('missingPhoto').files[0];
                if (photoFile) {
                    formData.append('person_photo', photoFile);
                }
                
                const response = await fetch('/api/missing', {
                    method: 'POST',
                    body: formData
                });
                
                if (response.ok) {
                    const result = await response.json();
                    reportMissingForm.reset();
                    showModal('Report Submitted', 'Your missing person report has been added to the registry.', 'OK', () => {
                        document.querySelector('.tab-btn[data-tab="searchTab"]').click();
                        loadMissingPersons(); // Reload the list
                    });
                } else {
                    const error = await response.json();
                    showModal('Error', error.detail || 'Failed to submit report', 'OK');
                }
            } catch (error) {
                console.error('Error submitting missing person report:', error);
                showModal('Error', 'Failed to submit report. Please try again.', 'OK');
            }
        });
        
        searchMissingInput.addEventListener('input', (e) => {
            renderMissingPersons(e.target.value);
        });

        getUserLocation();
        renderFamilyStatus();
        loadMissingPersons(); // Load missing persons from API
        loadSOSAlerts(); // Load SOS alerts from API
        loadCommunityFeed(); // Load community feed (posts + incidents)
        updateUI('en');
    }
});