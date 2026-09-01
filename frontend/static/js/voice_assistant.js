/**
 * Smart Kolhapur Guide - Voice Assistant
 * Built with browser Web Speech API (SpeechRecognition + SpeechSynthesis)
 * Client-side, zero paid API keys required.
 */

// Embedded authentic destination dataset for zero-latency client-side voice lookup
const KOLHAPUR_PLACES_DATA = [
  {
    "id": "mahalaxmi-temple",
    "name": "Shri Mahalaxmi Temple (Ambabai Mandir)",
    "category": "religion",
    "description": "One of the 108 Shakti Peethas and Dakshin Kashi, built in the 7th century by the Chalukyas. Famous for Kiranotsav where the sun rays directly illuminate the idol.",
    "tagline": "Ancient 7th Century Shakti Peetha & Spiritual Soul of Kolhapur"
  },
  {
    "id": "panhala-fort",
    "name": "Panhala Fort (Panhalgad)",
    "category": "history",
    "description": "The largest and most strategic hilltop fortress in the Deccan plateau, where Chhatrapati Shivaji Maharaj spent over 500 days. Features Sajja Kothi, Ambarkhana granaries, and Teen Darwaza.",
    "tagline": "Historic Maratha Citadel with Panoramic Sahyadri Valley Views"
  },
  {
    "id": "jyotiba-temple",
    "name": "Shri Jyotiba Temple (Wadi Ratnagiri)",
    "category": "religion",
    "description": "Sacred hilltop pilgrimage situated 3100 feet high, dedicated to Lord Jyotiba (an incarnation of Brahma, Vishnu, Shiva, and Jamadagni). Renowned for the radiant sea of yellow gulal.",
    "tagline": "Holy Hilltop Shrine Radiant with Golden Gulal Celebrations"
  },
  {
    "id": "rankala-lake",
    "name": "Rankala Lake & Promenade",
    "category": "nature",
    "description": "Historic freshwater lake constructed during the reign of Chhatrapati Shahu Maharaj, flanked by Sandhya Math, Shalini Palace, and picturesque sunset promenades.",
    "tagline": "Historic Waterfront Lake with Scenic Sunset Promenade & Chowpatty"
  },
  {
    "id": "new-palace",
    "name": "New Palace & Chhatrapati Shahu Museum",
    "category": "history",
    "description": "Magnificent Indo-Saracenic royal palace constructed in black basalt stone, housing the private museum of the royal Bhonsle dynasty of Kolhapur.",
    "tagline": "Architectural Masterpiece of Royal Maratha Heritage & Dynasty Museum"
  },
  {
    "id": "radhanagari-sanctuary",
    "name": "Radhanagari Wildlife Sanctuary",
    "category": "adventure",
    "description": "UNESCO World Heritage site nestled in the southern Western Ghats, renowned for the Indian Bison (Gaur), dense moist evergreen forests, and rich biodiversity.",
    "tagline": "UNESCO Western Ghats Wilderness & Protected Indian Bison Sanctuary"
  },
  {
    "id": "dajipur-bison-sanctuary",
    "name": "Dajipur Bison Wildlife Safari",
    "category": "adventure",
    "description": "The pioneer wildlife sanctuary of Maharashtra, offering exhilarating 4x4 open jungle safaris, birdwatching trails, and deep rainforest views.",
    "tagline": "Thrilling 4x4 Open Jeep Safaris & Dense Rainforest Trails"
  },
  {
    "id": "bhavani-mandap",
    "name": "Bhavani Mandap",
    "category": "history",
    "description": "Historic court of state ceremonies, wrestling akhadas, and temple dedicated to Goddess Tulja Bhavani inside the old royal palace complex.",
    "tagline": "Historic Royal Court, Traditional Wrestling Akhada & Goddess Shrine"
  },
  {
    "id": "shalini-palace",
    "name": "Shalini Palace",
    "category": "history",
    "description": "Only heritage lake palace in Maharashtra, built in Italian marble and black stone on the western bank of Rankala Lake for Princess Shalini Raje.",
    "tagline": "Regal Italian-Marble Heritage Palace on Rankala Lake Front"
  },
  {
    "id": "town-hall-museum",
    "name": "Town Hall Archaeological Museum",
    "category": "history",
    "description": "Neo-Gothic heritage museum preserving rare Satavahana and Roman artifacts discovered during Brahmagiri archaeological excavations in Kolhapur.",
    "tagline": "Neo-Gothic Museum Preserving Ancient Satavahana & Roman Artifacts"
  },
  {
    "id": "narsobawadi",
    "name": "Shri Kshetra Narsobawadi",
    "category": "religion",
    "description": "Sacred confluence (Sangam) of Krishna and Panchganga rivers, seat of Shri Nrusinha Saraswati Maharaj with serene ghats and palanquin rituals.",
    "tagline": "Sacred Holy River Confluence & Dattatreya Pilgrimage Ghats"
  },
  {
    "id": "kaneri-math",
    "name": "Kaneri Math (Siddhagiri Gramjivan Museum)",
    "category": "culture",
    "description": "Vast open-air cultural sculpture museum portraying traditional self-sustained Indian village life (Gramjivan) before modern industrialization.",
    "tagline": "Vast Open-Air Heritage Village Sculpture & Vedic Culture Museum"
  },
  {
    "id": "kopeshwar-temple",
    "name": "Kopeshwar Temple, Khidrapur",
    "category": "religion",
    "description": "Exquisite 12th-century stone temple dedicated to Lord Shiva on the Krishna river bank, celebrated for its circular open-roof Swarga Mandapa.",
    "tagline": "12th-Century Architectural Marvel Famous for Circular Swarga Mandapa"
  },
  {
    "id": "gaganbawda",
    "name": "Gaganbawda Hill Station & Fort",
    "category": "adventure",
    "description": "Pristine mist-covered hill station on the crest of Sahyadri ranges, home to Gagangiri Maharaj Ashram, scenic ghats, and heavy monsoon rains.",
    "tagline": "Misty Sahyadri Hilltop Station with Ancient Fort & Gagangiri Ashram"
  }
];

class VoiceAssistant {
  constructor() {
    this.places = KOLHAPUR_PLACES_DATA;
    this.recognition = null;
    this.synth = window.speechSynthesis || null;
    this.isListening = false;
    this.isSpeaking = false;
    this.preferredVoice = null;

    // DOM Elements
    this.modalOverlay = document.getElementById('voiceModalOverlay');
    this.voiceWave = document.getElementById('voiceWave');
    this.voiceStatus = document.getElementById('voiceStatusTitle');
    this.transcriptBox = document.getElementById('voiceTranscript');
    this.closeBtn = document.getElementById('voiceCloseBtn');
    this.heroMicBtn = document.getElementById('heroMicBtn');
    this.floatingMicBtn = document.getElementById('floatingVoiceBtn');

    this.init();
  }

  init() {
    // 1. Setup speech synthesis voices
    if (this.synth) {
      this.loadVoices();
      if (typeof speechSynthesis.onvoiceschanged !== "undefined") {
        speechSynthesis.onvoiceschanged = () => this.loadVoices();
      }
    }

    // 2. Setup Web Speech Recognition
    const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
    this.hasSpeechSupport = !!SpeechRecognition;

    // 3. Attach Event Listeners
    if (this.heroMicBtn) {
      this.heroMicBtn.addEventListener('click', (e) => {
        e.preventDefault();
        e.stopPropagation();
        this.startListening();
      });
    }

    if (this.floatingMicBtn) {
      this.floatingMicBtn.addEventListener('click', (e) => {
        e.preventDefault();
        e.stopPropagation();
        this.startListening();
      });
    }

    if (this.closeBtn) {
      this.closeBtn.addEventListener('click', () => this.stopAndClose());
    }

    if (this.modalOverlay) {
      this.modalOverlay.addEventListener('click', (e) => {
        if (e.target === this.modalOverlay) {
          this.stopAndClose();
        }
      });
    }

    // Document-level delegation in case heroMicBtn is re-rendered
    document.addEventListener('click', (e) => {
      const btn = e.target.closest('#heroMicBtn') || e.target.closest('#floatingVoiceBtn');
      if (btn) {
        e.preventDefault();
        this.startListening();
      }
    });
  }

  loadVoices() {
    if (!this.synth) return;
    const voices = this.synth.getVoices();
    // Prioritize English Indian, then natural English voices
    this.preferredVoice = voices.find(v => v.lang.includes('en-IN') || v.name.includes('India')) ||
                          voices.find(v => v.lang.startsWith('en') && (v.name.includes('Natural') || v.name.includes('Google'))) ||
                          voices.find(v => v.lang.startsWith('en')) || null;
  }

  /**
   * Start microphone listening with fresh SpeechRecognition instance
   */
  startListening() {
    this.stopSpeaking();

    const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
    if (!SpeechRecognition) {
      alert("Speech recognition is not supported in this browser. Please use Google Chrome, Microsoft Edge, or Safari on desktop/mobile.");
      return;
    }

    // Stop existing instance if running
    if (this.recognition) {
      try {
        this.recognition.abort();
      } catch (e) {}
    }

    // Open Modal and display active listening state immediately
    this.openModal();
    this.setStatus("Listening... Speak now");
    this.setTranscript("Listening for destination (e.g. 'Tell me about Mahalaxmi Temple')...");
    this.updateUIListening(true);

    try {
      this.recognition = new SpeechRecognition();
      this.recognition.continuous = false;
      this.recognition.interimResults = true;
      this.recognition.lang = 'en-IN'; // Indian English

      this.recognition.onstart = () => {
        this.isListening = true;
        this.updateUIListening(true);
        this.setStatus("Listening... Speak now");
      };

      this.recognition.onresult = (event) => {
        let interimTranscript = '';
        let finalTranscript = '';

        for (let i = event.resultIndex; i < event.results.length; ++i) {
          if (event.results[i].isFinal) {
            finalTranscript += event.results[i][0].transcript;
          } else {
            interimTranscript += event.results[i][0].transcript;
          }
        }

        const currentText = finalTranscript || interimTranscript;
        if (currentText) {
          this.setTranscript(currentText);

          // Update hero search input live as user speaks
          const searchInput = document.getElementById('heroSearchInput');
          if (searchInput) {
            searchInput.value = currentText;
            searchInput.dispatchEvent(new Event('input'));
          }
        }

        if (finalTranscript) {
          this.isListening = false;
          this.updateUIListening(false);
          this.processQuery(finalTranscript);
        }
      };

      this.recognition.onerror = (event) => {
        console.warn("Speech recognition error:", event.error);
        this.isListening = false;
        this.updateUIListening(false);

        if (event.error === 'not-allowed') {
          this.setStatus("Microphone Permission Blocked");
          this.setTranscript("Please click the lock/mic icon in your browser address bar and select 'Allow Microphone'.");
        } else if (event.error === 'no-speech') {
          this.setStatus("No Speech Detected");
          this.setTranscript("I didn't hear anything. Tap the microphone icon below to speak again.");
        } else {
          this.setStatus("Listening Paused");
          this.setTranscript(`Recognition notice (${event.error}). Tap the mic button to try again.`);
        }
      };

      this.recognition.onend = () => {
        this.isListening = false;
        this.updateUIListening(false);
      };

      this.recognition.start();
    } catch (e) {
      console.error("SpeechRecognition start error:", e);
      this.isListening = false;
      this.updateUIListening(false);
      this.setStatus("Voice Search Ready");
      this.setTranscript("Tap the microphone button to start voice recognition.");
    }
  }

  stopSpeaking() {
    if (this.synth) {
      this.synth.cancel();
      this.synth.resume();
    }
    this.isSpeaking = false;
    this.updateUIListening(false);
  }

  stopAndClose() {
    if (this.recognition) {
      try {
        this.recognition.abort();
      } catch (e) {}
    }
    this.stopSpeaking();
    this.closeModal();
  }

  openModal() {
    if (this.modalOverlay) {
      this.modalOverlay.classList.add('active');
    }
  }

  closeModal() {
    if (this.modalOverlay) {
      this.modalOverlay.classList.remove('active');
    }
  }

  updateUIListening(active) {
    if (this.voiceWave) {
      if (active) {
        this.voiceWave.classList.add('listening');
      } else {
        this.voiceWave.classList.remove('listening');
      }
    }

    const heroMic = document.getElementById('heroMicBtn');
    const floatMic = document.getElementById('floatingVoiceBtn');

    if (active) {
      if (heroMic) heroMic.classList.add('listening-pulse');
      if (floatMic) floatMic.classList.add('listening-pulse');
    } else {
      if (heroMic) heroMic.classList.remove('listening-pulse');
      if (floatMic) floatMic.classList.remove('listening-pulse');
    }
  }

  setStatus(text) {
    if (this.voiceStatus) {
      this.voiceStatus.textContent = text;
    }
  }

  setTranscript(text) {
    if (this.transcriptBox) {
      this.transcriptBox.textContent = `"${text}"`;
    }
  }

  /**
   * Process query text, find destination/category, and speak response
   */
  processQuery(rawText) {
    if (!rawText) return;
    const text = rawText.toLowerCase().trim();

    this.openModal();
    this.setTranscript(rawText);

    // Stop command
    if (text.includes("stop") || text.includes("cancel") || text.includes("quiet")) {
      this.stopSpeaking();
      this.setStatus("Stopped");
      this.setTranscript("Voice playback stopped.");
      return;
    }

    // 1. Hotel recommendations check
    if (text.includes("hotel") || text.includes("stay") || text.includes("room") || text.includes("resort")) {
      const matchedPlace = this.matchPlace(text);
      if (matchedPlace) {
        const msg = `Finding top recommended hotels near ${matchedPlace.name}. Opening hotels portal!`;
        this.setStatus(`Hotels near ${matchedPlace.name}`);
        this.speak(msg, () => {
          window.location.href = `/hotels?destination=${matchedPlace.id}`;
        });
      } else {
        const msg = "Opening the Kolhapur hotel recommendation engine.";
        this.setStatus("Opening Hotel Finder...");
        this.speak(msg, () => {
          window.location.href = '/hotels';
        });
      }
      return;
    }

    // 2. Category filtering check
    const categoryMatches = [
      { keys: ["temple", "spiritual", "religion", "god", "devi", "darshan", "shrine"], cat: "religion", label: "Spiritual & Temples" },
      { keys: ["fort", "history", "historical", "palace", "museum", "chhatrapati"], cat: "history", label: "Forts & Heritage" },
      { keys: ["nature", "lake", "water", "greenery", "garden"], cat: "nature", label: "Lakes & Nature" },
      { keys: ["culture", "craft", "village", "art", "gramjivan"], cat: "culture", label: "Arts & Culture" },
      { keys: ["adventure", "safari", "wildlife", "bison", "jungle", "ghat"], cat: "adventure", label: "Safaris & Adventure" },
      { keys: ["all places", "all destinations", "show everything", "reset"], cat: "all", label: "All Destinations" }
    ];

    for (const item of categoryMatches) {
      if (item.keys.some(k => text.includes(k))) {
        const catBtn = document.querySelector(`.category-btn[data-category="${item.cat}"]`);
        if (catBtn) {
          catBtn.click();
        }
        this.setStatus(`Showing: ${item.label}`);
        const msg = `Showing ${item.label} in Kolhapur district.`;
        this.speak(msg);
        const grid = document.getElementById('placesGrid');
        if (grid) grid.scrollIntoView({ behavior: 'smooth', block: 'start' });
        return;
      }
    }

    // 3. Destination Lookup
    const matchedPlace = this.matchPlace(text);
    if (matchedPlace) {
      this.setStatus(`Voice Guide: ${matchedPlace.name}`);
      this.setTranscript(`${matchedPlace.name} — ${matchedPlace.description}`);

      // Highlight card on homepage if available
      const card = document.getElementById(`place-${matchedPlace.id}`);
      if (card) {
        card.style.display = 'flex';
        card.scrollIntoView({ behavior: 'smooth', block: 'center' });
        card.style.outline = '4px solid #D4AF37';
        card.style.transition = 'outline 0.3s ease';
        setTimeout(() => { card.style.outline = 'none'; }, 6000);
      }

      this.speak(`${matchedPlace.name}. ${matchedPlace.description}`);
      return;
    }

    // 4. Kolhapur Overview
    if (text.includes("kolhapur") || text.includes("best place") || text.includes("overview") || text.includes("tell me") || text.includes("what is")) {
      const summary = "Kolhapur is a renowned historical, cultural, and pilgrimage district of Maharashtra, celebrated for Shri Mahalaxmi Temple, historic Panhala Fort, scenic Rankala Lake, and the legacy of Rajarshi Shahu Maharaj.";
      this.setStatus("Kolhapur Overview");
      this.setTranscript(summary);
      this.speak(summary);
      return;
    }

    // 5. Fallback
    this.setStatus("Place Not Found");
    const notFoundMsg = "I couldn't find that destination. You can ask about Mahalaxmi Temple, Panhala Fort, Jyotiba Temple, or say 'Show temples'.";
    this.setTranscript(notFoundMsg);
    this.speak(notFoundMsg);
  }

  matchPlace(text) {
    const aliases = {
      "mahalaxmi-temple": ["mahalaxmi", "ambabai", "lakshmi", "temple in kolhapur", "goddess", "shakti peeth", "dakshin kashi"],
      "panhala-fort": ["panhala", "panhalgad", "fort", "sajja kothi", "shivaji maharaj fort"],
      "jyotiba-temple": ["jyotiba", "wadi ratnagiri", "kedareshwar", "gulal"],
      "rankala-lake": ["rankala", "lake", "chowpatty", "sandhya math", "waterfront"],
      "new-palace": ["new palace", "shahu museum", "durbar hall", "palace museum"],
      "radhanagari-sanctuary": ["radhanagari", "wildlife", "dam", "laxmi talav", "bison sanctuary"],
      "dajipur-bison-sanctuary": ["dajipur", "safari", "gaur", "jungle safari"],
      "bhavani-mandap": ["bhavani mandap", "tulja bhavani", "wrestling", "kusti"],
      "shalini-palace": ["shalini", "shalini palace", "lake palace"],
      "town-hall-museum": ["town hall", "museum", "archaeological"],
      "narsobawadi": ["narsobawadi", "nrusinhawadi", "dattatreya", "sangam", "basundi"],
      "kaneri-math": ["kaneri", "siddhagiri", "gramjivan", "village museum"],
      "kopeshwar-temple": ["kopeshwar", "khidrapur", "swarga mandapa", "stone temple"],
      "gaganbawda": ["gaganbawda", "gagangiri", "ashram", "ghat", "hill station"]
    };

    // Match by ID or Name
    for (const place of this.places) {
      if (text.includes(place.name.toLowerCase()) || text.includes(place.id.toLowerCase())) {
        return place;
      }
    }

    // Match by keywords/aliases
    for (const [placeId, words] of Object.entries(aliases)) {
      for (const word of words) {
        if (text.includes(word)) {
          return this.places.find(p => p.id === placeId);
        }
      }
    }

    return null;
  }

  /**
   * Speak text with browser SpeechSynthesis
   */
  speak(text, onComplete = null) {
    if (!this.synth) {
      if (onComplete) onComplete();
      return;
    }

    // Ensure speech synthesis is unblocked
    this.synth.cancel();
    this.synth.resume();

    const utterance = new SpeechSynthesisUtterance(text);
    utterance.rate = 0.95;
    utterance.pitch = 1.0;
    utterance.lang = 'en-IN';

    if (this.preferredVoice) {
      utterance.voice = this.preferredVoice;
    }

    utterance.onstart = () => {
      this.isSpeaking = true;
      this.updateUIListening(true);
    };

    utterance.onend = () => {
      this.isSpeaking = false;
      this.updateUIListening(false);
      if (onComplete) {
        setTimeout(onComplete, 500);
      }
    };

    utterance.onerror = (e) => {
      console.warn("Speech error:", e);
      this.isSpeaking = false;
      this.updateUIListening(false);
      if (onComplete) onComplete();
    };

    this.synth.speak(utterance);
  }
}

// Global function to speak any tourist destination directly
function speakTouristPlace(name, description, placeId = null) {
  if (window.KolhapurVoiceAssistant) {
    const assistant = window.KolhapurVoiceAssistant;
    assistant.openModal();
    assistant.setStatus(`Voice Guide: ${name}`);
    assistant.setTranscript(`${name} — ${description}`);

    // Highlight card if on page
    if (placeId) {
      const card = document.getElementById(`place-${placeId}`);
      if (card) {
        card.style.display = 'flex';
        card.scrollIntoView({ behavior: 'smooth', block: 'center' });
        card.style.outline = '4px solid #D4AF37';
        card.style.transition = 'outline 0.3s ease';
        setTimeout(() => { card.style.outline = 'none'; }, 6000);
      }
    }

    assistant.speak(`${name}. ${description}`);
  }
}

// Instantiate immediately and attach to window
window.KolhapurVoiceAssistant = new VoiceAssistant();
