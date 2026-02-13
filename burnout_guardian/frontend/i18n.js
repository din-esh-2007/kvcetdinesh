/**
 * i18n Translation Dictionary
 * Support for English, Tamil, and Hindi
 */

const translations = {
    en: {
        dashboard: "Dashboard",
        forecast: "Stability",
        interventions: "Interventions",
        emotion_tracker: "Emotion Tracker",
        reports: "Alerts",
        daily_checkin: "Daily Check-In",
        settings: "Settings",
        logout: "Logout",
        system_active: "System Active",
        login: {
            title: "Burnout Guardian",
            subtitle: "Predictive Human Stability Control System",
            username: "Username / Employee ID",
            password: "Security Key",
            button: "Authorize Access",
            error: "Authorization Failed"
        },
        hero_stats: {
            next_peak: "Next Peak Risk",
            stability: "Stability Index",
            risk_prob: "Risk Probability",
            volatility: "Volatility"
        },
        stats: {
            active_interventions: "Active Interventions",
            helping_recovery: "Helping you recover",
            stability_timeline: "Stability Timeline"
        },
        settings_view: {
            title: "System Settings",
            language: "Interface Language",
            theme: "Interface Theme",
            autonomous: "Autonomous Decision Engine",
            privacy: "Privacy Safeguards",
            calibration: "Sensor Calibration",
            recalibrate: "Recalibrate Volatility Baseline",
            reset_emotion: "Reset Emotion Baseline"
        },
        archive: {
            title: "System Archive",
            frequency: "Archive Frequency",
            last: "Last Archive",
            archive_now: "Archive Now",
            clear: "Clear Old Data"
        },
        roles: {
            admin: "Administrator",
            manager: "Manager",
            employee: "Employee"
        },
        admin: {
            onboarding: "User Onboarding",
            full_name: "Full Name",
            email: "Email",
            employee_id: "Employee ID",
            create_btn: "Create Security Profile",
            suspension: "Human Stability Suspension",
            select_human: "Select Human Asset...",
            reason: "Reason for Stability Pause",
            execute: "Execute Suspension",
            manage_managers: "Manage Managers",
            remove_manager: "Remove Manager",
            add_manager: "Add Manager",
            add_employee: "Add Employee",
            mobile: "Mobile Number",
            gender: "Gender",
            address: "Address",
            dob: "Date of Birth",
            department: "Department",
            employment_type: "Employment Type",
            emergency_contact: "Emergency Contact",
            joining_date: "Joining Date",
            username: "Username",
            password: "Password",
            male: "Male",
            female: "Female",
            other: "Other"
        },
        manager: {
            delegation: "Task Delegation",
            objective: "Task Objective",
            exp_volatility: "Expected Volatility (Hrs)",
            delegate_to: "Delegate to...",
            deploy: "Deploy Task",
            heatmap: "Burnout Heatmap"
        }
    },
    ta: {
        dashboard: "முகப்பு",
        forecast: "நிலைமை",
        interventions: "தலையீடுகள்",
        emotion_tracker: "உணர்ச்சி",
        reports: "அறிக்கை",
        daily_checkin: "பதிவு",
        settings: "அமைப்புகள்",
        logout: "வெளியேறு",
        system_active: "செயலில் உள்ளது",
        login: {
            title: "பர்ன்அவுட் கார்டியன்",
            subtitle: "முன்கணிப்பு மனித நிலைத்தன்மை கட்டுப்பாட்டு அமைப்பு",
            username: "பயனர் பெயர் / பணியாளர் ஐடி",
            password: "பாதுகாப்பு விசை",
            button: "அணுகலை அங்கீகரிக்கவும்",
            error: "அங்கீகாரம் தோல்வியடைந்தது"
        },
        hero_stats: {
            next_peak: "அடுத்த அபாய நேரம்",
            stability: "நிலைத்தன்மை குறியீடு",
            risk_prob: "அபாய நிகழ்தகவு",
            volatility: "நிலையற்ற தன்மை"
        },
        stats: {
            active_interventions: "செயலில் உள்ள தலையீடுகள்",
            helping_recovery: "மீண்டு வர உதவுகிறது",
            stability_timeline: "நிலைத்தன்மை காலவரிசை"
        },
        settings_view: {
            title: "அமைப்புகள்",
            language: "மொழி",
            theme: "தோற்றம்",
            autonomous: "தன்னாட்சி முடிவு இயந்திரம்",
            privacy: "தனியுरीமை பாதுகாப்புகள்",
            calibration: "சென்சார் அளவுத்திருத்தம்",
            recalibrate: "நிலையற்ற அடிப்படை அளவீட்டை மீண்டும் கணக்கிடு",
            reset_emotion: "உணர்ச்சி அடிப்படை அளவீட்டை மீட்டமை"
        },
        archive: {
            title: "கணினி காப்பகம்",
            frequency: "காப்பக அதிர்வெண்",
            last: "கடைசி காப்பகம்",
            archive_now: "இப்போது காப்பகப்படுத்து",
            clear: "பழைய தரவை அகற்று"
        },
        roles: {
            admin: "நிர்வாகி",
            manager: "மேலாளர்",
            employee: "பணியாளர்"
        },
        admin: {
            onboarding: "பயனர் சேர்க்கை",
            full_name: "முழு பெயர்",
            email: "மின்னஞ்சல்",
            employee_id: "பணியாளர் ஐடி",
            create_btn: "சுயவிவரத்தை உருவாக்கு",
            suspension: "இடைநீக்கம்",
            select_human: "நபரைத் தேர்ந்தெடுக்கவும்...",
            reason: "காரணம்",
            execute: "செயல்படுத்து",
            manage_managers: "மேலாளர்கள்",
            remove_manager: "நீக்கு",
            add_manager: "மேலாளரைச் சேர்",
            add_employee: "பணியாளரைச் சேர்",
            mobile: "கைப்பேசி எண்",
            gender: "பாலினம்",
            address: "முகவரி",
            dob: "பிறந்த தேதி",
            department: "துறை",
            employment_type: "வேலை வகை",
            emergency_contact: "அவசரகால தொடர்பு",
            joining_date: "சேர்ந்த தேதி",
            username: "பயனர் பெயர்",
            password: "கடவுச்சொல்",
            male: "ஆண்",
            female: "பெண்",
            other: "மற்றவை"
        },
        manager: {
            delegation: "பணி ஒப்படைப்பு",
            objective: "பணி நோக்கம்",
            exp_volatility: "வேலை நேரம்",
            delegate_to: "ஒப்படைக்க வேண்டிய நபர்...",
            deploy: "பணியை ஒப்படை",
            heatmap: "வரைபடம்"
        }
    },
    hi: {
        dashboard: "मुख्य",
        forecast: "स्थिरता",
        interventions: "हस्तक्षेप",
        emotion_tracker: "भावना",
        reports: "अलर्ट",
        daily_checkin: "चेक-इन",
        settings: "सेटिंग्स",
        logout: "लॉगआउट",
        system_active: "सिस्टम सक्रिय",
        login: {
            title: "बर्नआउट गार्जियन",
            subtitle: "भविष्य कहनेवाला मानव स्थिरता नियंत्रण प्रणाली",
            username: "उपयोगकर्ता नाम / कर्मचारी आईडी",
            password: "सुरक्षा कुंजी",
            button: "पहुंच अधिकृत करें",
            error: "प्राधिकरण विफल"
        },
        hero_stats: {
            next_peak: "अगला चरम जोखिम",
            stability: "स्थिरता सूचकांक",
            risk_prob: "जोखिम संभावना",
            volatility: "अस्थिरता"
        },
        stats: {
            active_interventions: "सक्रिय हस्तक्षेप",
            helping_recovery: "रिकवरी में मदद",
            stability_timeline: "स्थिरता समयरेखा"
        },
        settings_view: {
            title: "सिस्टम सेटिंग्स",
            language: "भाषा",
            theme: "थीम",
            autonomous: "स्वायत्त निर्णय इंजन",
            privacy: "गोपनीयता सुरक्षा",
            calibration: "सेंसर अंशांकन",
            recalibrate: "अस्थिरता आधार रेखा को फिर से अंशांकित करें",
            reset_emotion: "भावना आधार रेखा को रीसेट करें"
        },
        archive: {
            title: "सिस्टम आर्काइव",
            frequency: "आर्काइव आवृत्ति",
            last: "पिछला आर्काइव",
            archive_now: "अभी आर्काइव करें",
            clear: "पुराना डेटा साफ़ करें"
        },
        roles: {
            admin: "प्रशासक",
            manager: "प्रबंधक",
            employee: "कर्मचारी"
        },
        admin: {
            onboarding: "ऑनबोर्डिंग",
            full_name: "पूरा नाम",
            email: "ईमेल",
            employee_id: "आईडी",
            create_btn: "प्रोफ़ाइल बनाएं",
            suspension: "निलंबन",
            select_human: "चुनें...",
            reason: "कारण",
            execute: "निष्पादित करें",
            manage_managers: "प्रबंधक",
            remove_manager: "हटाएँ",
            add_manager: "प्रबंधक जोड़ें",
            add_employee: "कर्मचारी जोड़ें",
            mobile: "मोबाइल नंबर",
            gender: "लिंग",
            address: "पता",
            dob: "जन्म तिथि",
            department: "विभाग",
            employment_type: "रोजगार का प्रकार",
            emergency_contact: "आपातकालीन संपर्क",
            joining_date: "शामिल होने की तिथि",
            username: "उपयोगकर्ता नाम",
            password: "पासवर्ड",
            male: "पुरुष",
            female: "महिला",
            other: "अन्य"
        },
        manager: {
            delegation: "प्रतिनिधिमंडल",
            objective: "कार्य उद्देश्य",
            exp_volatility: "अस्थिरता (घंटे)",
            delegate_to: "चुनें...",
            deploy: "कार्य तैनात करें",
            heatmap: "हीटमैप"
        }
    }
};

window.I18N = {
    current: localStorage.getItem('language') || 'en',

    setLanguage(lang) {
        this.current = lang;
        localStorage.setItem('language', lang);
        this.apply();
        console.log(`🌐 Language set to: ${lang}`);
    },

    t(key) {
        const keys = key.split('.');
        let translation = translations[this.current];

        for (const k of keys) {
            if (translation && translation[k]) {
                translation = translation[k];
            } else {
                return key;
            }
        }
        return translation;
    },

    apply() {
        // Update elements with data-t attribute
        document.querySelectorAll('[data-t]').forEach(el => {
            const key = el.dataset.t;
            if (el.tagName === 'INPUT' && (el.type === 'placeholder' || el.hasAttribute('placeholder'))) {
                el.placeholder = this.t(key);
            } else if (el.tagName === 'INPUT' || el.tagName === 'TEXTAREA') {
                if (el.placeholder) el.placeholder = this.t(key);
            } else {
                el.innerText = this.t(key);
            }
        });

        // Custom updates for specific elements if needed
        document.documentElement.lang = this.current;
    }
};
