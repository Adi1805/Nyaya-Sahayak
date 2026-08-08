document.addEventListener("DOMContentLoaded", () => {
    const micBtn = document.getElementById("mic-btn");
    const manualInput = document.getElementById("manual-incident-input");
    const submitTextBtn = document.getElementById("submit-text-btn");
    const statusText = document.getElementById("dictation-status");
    const transcriptBox = document.getElementById("transcript-box");
    const liveTranscript = document.getElementById("live-transcript");
    const aiProgressContainer = document.getElementById("ai-progress-container");
    const aiProgress = document.getElementById("ai-progress");
    const stepExtraction = document.getElementById("step-extraction");
    const factsContainer = document.getElementById("facts-container");
    const stepSections = document.getElementById("step-sections");
    const sectionsContainer = document.getElementById("sections-container");
    const stepFir = document.getElementById("step-fir");
    const firDraftContent = document.getElementById("fir-draft-content");
    const btnEditFir = document.getElementById("btn-edit-fir");
    const btnDownloadPdf = document.getElementById("btn-download-pdf");
    const btnDiscardCase = document.getElementById("btn-discard-case");
    const btnSaveCase = document.getElementById("btn-save-case");
    const navNewFir = document.getElementById("nav-new-fir");
    const navActiveCases = document.getElementById("nav-active-cases");
    const navSearchLaws = document.getElementById("nav-search-laws");
    const newFirView = document.getElementById("new-fir-view");
    const activeCasesView = document.getElementById("active-cases-view");
    const searchLawsView = document.getElementById("search-laws-view");
    const aiPanel = document.querySelector(".ai-panel");
    const activeCasesGrid = document.getElementById("active-cases-grid");
    const searchInput = document.getElementById("search-laws-input");
    const btnSearchLaws = document.getElementById("btn-search-laws");
    const searchStatus = document.getElementById("search-laws-status");
    const searchResults = document.getElementById("search-laws-results");
    const stateSelect = document.getElementById("state-select");
    const districtSelect = document.getElementById("district-select");
    const stationSelect = document.getElementById("station-select");
    const sectionModal = document.getElementById("section-modal");
    const modalCloseBtn = document.getElementById("modal-close-btn");
    const modalTitle = document.getElementById("modal-title");
    const modalFullText = document.getElementById("modal-full-text");
    let isProcessing = false;
    modalCloseBtn.addEventListener("click", () => {
        sectionModal.classList.add("hidden");
    });
    sectionModal.addEventListener("click", (e) => {
        if(e.target === sectionModal) sectionModal.classList.add("hidden");
    });
    const witnessView = document.getElementById("witness-analyzer-view");
    const navWitness = document.getElementById("nav-witness-analyzer");
    function hideAllViews() {
        navNewFir.classList.remove("active");
        navActiveCases.classList.remove("active");
        navSearchLaws.classList.remove("active");
        if(navWitness) navWitness.classList.remove("active");
        newFirView.classList.add("hidden");
        activeCasesView.classList.add("hidden");
        searchLawsView.classList.add("hidden");
        if(witnessView) witnessView.classList.add("hidden");
        const cdView = document.getElementById("case-details-view");
        if(cdView) cdView.classList.add("hidden");
        aiPanel.classList.add("hidden");
    }
    navNewFir.addEventListener("click", (e) => {
        e.preventDefault();
        hideAllViews();
        navNewFir.classList.add("active");
        newFirView.classList.remove("hidden");
        aiPanel.classList.remove("hidden");
    });
    navActiveCases.addEventListener("click", (e) => {
        e.preventDefault();
        hideAllViews();
        navActiveCases.classList.add("active");
        activeCasesView.classList.remove("hidden");
        renderActiveCases();
    });
    navSearchLaws.addEventListener("click", (e) => {
        e.preventDefault();
        hideAllViews();
        navSearchLaws.classList.add("active");
        searchLawsView.classList.remove("hidden");
    });
    if(navWitness) {
        navWitness.addEventListener("click", (e) => {
            e.preventDefault();
            hideAllViews();
            navWitness.classList.add("active");
            witnessView.classList.remove("hidden");
        });
    }
    let currentCaseData = null;
    if (typeof locationData !== 'undefined') {
        locationData.states.forEach(state => {
            const opt = document.createElement("option");
            opt.value = state.name;
            opt.textContent = state.name;
            stateSelect.appendChild(opt);
        });
        stateSelect.addEventListener("change", () => {
            districtSelect.innerHTML = '<option value="">Select District</option>';
            stationSelect.innerHTML = '<option value="">Select Police Station</option>';
            stationSelect.disabled = true;
            const selectedState = locationData.states.find(s => s.name === stateSelect.value);
            if (selectedState) {
                districtSelect.disabled = false;
                selectedState.districts.forEach(dist => {
                    const opt = document.createElement("option");
                    opt.value = dist.name;
                    opt.textContent = dist.name;
                    districtSelect.appendChild(opt);
                });
            } else {
                districtSelect.disabled = true;
            }
        });
        districtSelect.addEventListener("change", () => {
            stationSelect.innerHTML = '<option value="">Select Police Station</option>';
            const selectedState = locationData.states.find(s => s.name === stateSelect.value);
            if (selectedState) {
                const selectedDistrict = selectedState.districts.find(d => d.name === districtSelect.value);
                if (selectedDistrict) {
                    stationSelect.disabled = false;
                    selectedDistrict.police_stations.forEach(ps => {
                        const opt = document.createElement("option");
                        opt.value = ps;
                        opt.textContent = ps;
                        stationSelect.appendChild(opt);
                    });
                } else {
                    stationSelect.disabled = true;
                }
            }
        });
    }
    btnEditFir.addEventListener("click", () => {
        if (firDraftContent.contentEditable === "true") {
            firDraftContent.contentEditable = "false";
            btnEditFir.innerHTML = '<i class="ph ph-pencil-simple"></i> Edit Draft';
            if (currentCaseData) currentCaseData.firHTML = firDraftContent.innerHTML;
        } else {
            firDraftContent.contentEditable = "true";
            firDraftContent.focus();
            btnEditFir.innerHTML = '<i class="ph-fill ph-check-circle"></i> Save Edits';
        }
    });
    btnDownloadPdf.addEventListener("click", async () => {
        const content = document.createElement("div");
        content.innerHTML = firDraftContent.innerHTML;
        content.style.padding = "5px";
        content.style.fontFamily = "'Times New Roman', Times, serif";
        content.style.color = "#000000";
        content.style.backgroundColor = "#ffffff";
        content.style.lineHeight = "1.6";
        let headerImgData = null;
        let headerImgAspect = 1;
        const wrapper = document.createElement('div');
        wrapper.style.overflow = 'hidden';
        wrapper.style.height = '0';
        wrapper.style.position = 'absolute';
        wrapper.style.left = '0';
        wrapper.style.top = '0';
        wrapper.appendChild(content);
        document.body.appendChild(wrapper);
        const headerEl = content.querySelector("#ncrb-header");
        if (headerEl && typeof html2canvas === 'function') {
            wrapper.style.height = 'auto';
            wrapper.style.overflow = 'visible';
            const canvas = await html2canvas(headerEl, { scale: 3, backgroundColor: '#ffffff' });
            headerImgData = canvas.toDataURL('image/png');
            headerImgAspect = canvas.width / canvas.height;
            wrapper.style.height = '0';
            wrapper.style.overflow = 'hidden';
        }
        document.body.removeChild(wrapper);
        wrapper.removeChild(content);
        const opt = {
            margin:       [28, 15, 15, 15],
            filename:     'FIR_Draft.pdf',
            image:        { type: 'jpeg', quality: 0.98 },
            html2canvas:  { scale: 2 },
            jsPDF:        { unit: 'mm', format: 'a4', orientation: 'portrait' },
            pagebreak:    { mode: ['css', 'legacy'], avoid: ['table', 'tr', 'h3', 'p'] }
        };
        html2pdf().set(opt).from(content).toPdf().get('pdf').then(function(pdf) {
            if (headerImgData) {
                var totalPages = pdf.internal.getNumberOfPages();
                var pageWidth = pdf.internal.pageSize.getWidth();
                var imgWidth = pageWidth - 30;
                var imgHeight = imgWidth / headerImgAspect;
                for (let i = 2; i <= totalPages; i++) {
                    pdf.setPage(i);
                    pdf.addImage(headerImgData, 'PNG', 15, 3, imgWidth, imgHeight);
                }
            }
        }).save();
    });
    btnDiscardCase.addEventListener("click", () => {
        if(confirm("Are you sure you want to discard this case?")) {
            currentCaseData = null;
            stepExtraction.classList.add("hidden");
            stepSections.classList.add("hidden");
            stepFir.classList.add("hidden");
            transcriptBox.classList.add("hidden");
            statusText.style.color = "#94a3b8";
            statusText.innerText = "Case discarded. Ready for next incident.";
            aiProgressContainer.classList.add("hidden");
            manualInput.value = "";
        }
    });
    btnSaveCase.addEventListener("click", () => {
        if (!currentCaseData) return;
        currentCaseData.firHTML = firDraftContent.innerHTML;
        let savedCases = JSON.parse(localStorage.getItem("nyaya_cases") || "[]");
        savedCases.push(currentCaseData);
        localStorage.setItem("nyaya_cases", JSON.stringify(savedCases));
        alert("Case successfully saved to Active Cases!");
        navActiveCases.click();
    });
    function renderActiveCases() {
        activeCasesGrid.innerHTML = "";
        let savedCases = JSON.parse(localStorage.getItem("nyaya_cases") || "[]");
        if (savedCases.length === 0) {
            activeCasesGrid.innerHTML = "<p style='color: #94a3b8'>No active cases found. Generate a new FIR to save it here.</p>";
            return;
        }
        savedCases.reverse().forEach(c => {
            const card = document.createElement("div");
            card.className = "case-card glass-panel";
            card.innerHTML = `
                <h3>${c.title}</h3>
                <p><i class="ph ph-calendar"></i> ${c.date}</p>
                <p><i class="ph ph-map-pin"></i> ${c.location}</p>
                <div class="case-card-footer">
                    <span style="color: #10b981; font-size: 0.8rem; font-weight: 600;">STATUS: ACTIVE</span>
                    <button class="case-card-btn" onclick="viewSavedCase('${c.id}')">View Case File</button>
                </div>
            `;
            activeCasesGrid.appendChild(card);
        });
    }
    window.viewSavedCase = function(id) {
        let savedCases = JSON.parse(localStorage.getItem("nyaya_cases") || "[]");
        const c = savedCases.find(x => x.id === id);
        if(c) {
            currentCaseData = c;
            document.getElementById("new-fir-view").classList.add("hidden");
            document.getElementById("active-cases-view").classList.add("hidden");
            document.getElementById("search-laws-view").classList.add("hidden");
            const cdView = document.getElementById("case-details-view");
            cdView.classList.remove("hidden");
            document.getElementById("cd-title").innerText = c.title;
            document.getElementById("cd-subtitle").innerText = c.location + " • " + c.date;
            document.getElementById("cs-output").classList.add("hidden");
            document.getElementById("cd-witness").value = "";
            document.getElementById("cd-forensics").value = "";
        }
    };
    const btnGenChargesheet = document.getElementById("btn-gen-chargesheet");
    const csLoading = document.getElementById("cs-loading");
    const csOutput = document.getElementById("cs-output");
    if (btnGenChargesheet) {
        btnGenChargesheet.addEventListener("click", async () => {
            if (!currentCaseData) return;
            btnGenChargesheet.disabled = true;
            csLoading.classList.remove("hidden");
            csOutput.classList.add("hidden");
            try {
                const response = await fetch("http://localhost:8000/api/generate_chargesheet", {
                    method: "POST",
                    headers: { "Content-Type": "application/json" },
                    body: JSON.stringify({
                        fir_content: currentCaseData.firHTML || "FIR content missing",
                        witness_statements: document.getElementById("cd-witness").value,
                        forensic_reports: document.getElementById("cd-forensics").value,
                        case_title: currentCaseData.title
                    })
                });
                if (!response.ok) throw new Error("Failed to generate charge-sheet");
                const data = await response.json();
                document.getElementById("cs-diary-content").innerHTML = data.case_diary;
                const matrixBody = document.getElementById("cs-matrix-body");
                matrixBody.innerHTML = "";
                data.evidence_matrix.forEach((item, idx) => {
                    const row = document.createElement("tr");
                    row.style.borderBottom = "1px solid rgba(255,255,255,0.05)";
                    row.innerHTML = `
                        <td style="padding: 12px;">${item.accused_name}</td>
                        <td style="padding: 12px;"><span style="background: rgba(255,255,255,0.1); padding: 4px 8px; border-radius: 4px; font-size: 12px;">${item.evidence_type}</span></td>
                        <td style="padding: 12px;">${item.description}</td>
                        <td style="padding: 12px;"><span style="color: ${item.strength === 'High' ? '#10b981' : (item.strength === 'Medium' ? '#f59e0b' : '#ef4444')}; font-weight: bold;">${item.strength}</span></td>
                    `;
                    matrixBody.appendChild(row);
                });
                document.getElementById("cs-draft-content").innerHTML = data.charge_sheet;
                csOutput.classList.remove("hidden");
                csOutput.scrollIntoView({ behavior: 'smooth' });
            } catch(e) {
                alert("Error generating documents: " + e.message);
            } finally {
                btnGenChargesheet.disabled = false;
                csLoading.classList.add("hidden");
            }
        });
    }
    btnSearchLaws.addEventListener("click", async () => {
        const query = searchInput.value.trim();
        if (!query) return;
        btnSearchLaws.innerHTML = '<i class="ph ph-spinner"></i> Searching...';
        btnSearchLaws.disabled = true;
        searchStatus.innerText = "Querying ChromaDB Vector Database...";
        searchResults.innerHTML = "";
        try {
            const response = await fetch(`http://localhost:8000/api/search_laws?q=${encodeURIComponent(query)}`);
            if (!response.ok) throw new Error("Failed to fetch");
            const data = await response.json();
            searchStatus.innerText = `Found ${data.sections.length} relevant laws matching your query.`;
            data.sections.forEach((sec, idx) => {
                const div = document.createElement("div");
                div.className = "section-item";
                div.style.animation = `fadeIn 0.4s ease backwards ${idx * 0.15}s`;
                const cogClass = sec.cognizable && sec.cognizable.toLowerCase().includes("non") ? "tag-green" : "tag-red";
                const bailClass = sec.bailable && sec.bailable.toLowerCase().includes("non") ? "tag-red" : "tag-green";
                div.innerHTML = `
                    <div class="section-subtitle">${sec.section_number || ''} — ${sec.chapter_name || 'Offences'}</div>
                    <div class="section-title">${sec.short_title || 'Legal Section'}</div>
                    <div class="section-desc" style="color: #cbd5e1; margin-top: 8px;">${sec.punishment || 'See detailed text'}</div>
                    <div class="section-footer">
                        <span>Old IPC equivalent: ${sec.ipc_equivalent || 'Unknown'}</span>
                        <div class="tag-container">
                            <span class="${cogClass}">${sec.cognizable || 'Unknown'}</span>
                            <span class="${bailClass}">${sec.bailable || 'Unknown'}</span>
                        </div>
                    </div>
                `;
                div.addEventListener("click", () => {
                    modalTitle.innerText = `${sec.section_number} - ${sec.short_title}`;
                    modalFullText.innerText = sec.full_text || "No detailed text available.";
                    sectionModal.classList.remove("hidden");
                });
                searchResults.appendChild(div);
            });
        } catch(err) {
            searchStatus.innerText = "Error fetching laws. Make sure the backend server is running.";
            searchStatus.style.color = "#ef4444";
        }
        btnSearchLaws.innerHTML = '<i class="ph ph-magnifying-glass"></i> Search';
        btnSearchLaws.disabled = false;
    });
    function isLocationSelected() {
        if (!stateSelect.value || !districtSelect.value || !stationSelect.value) {
            alert("Please select the State, District, and Police Station first.");
            return false;
        }
        return true;
    }
    const voiceControls = document.getElementById("voice-controls");
    const recIndicatorDot = document.getElementById("rec-indicator-dot");
    const recStatusText = document.getElementById("rec-status-text");
    const recTimeDisplay = document.getElementById("rec-time-display");
    const btnPauseRec = document.getElementById("btn-pause-rec");
    const btnResumeRec = document.getElementById("btn-resume-rec");
    const btnStopRec = document.getElementById("btn-stop-rec");
    const recLivePreview = document.getElementById("rec-live-preview");
    const manualInputSection = document.getElementById("manual-input-section");
    let firMediaRecorder = null;
    let firAudioChunks = [];
    let firRecInterval = null;
    let firRecSeconds = 0;
    let firIsRecording = false;
    let firSpeechRec = null;
    let firSpeechText = "";
    const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
    micBtn.addEventListener("click", async () => {
        if(isProcessing || firIsRecording) return;
        if(!isLocationSelected()) return;
        try {
            const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
            firMediaRecorder = new MediaRecorder(stream, { mimeType: 'audio/webm;codecs=opus' });
            firAudioChunks = [];
            firSpeechText = "";
            if (recLivePreview) {
                recLivePreview.style.fontStyle = "italic";
                recLivePreview.style.color = "#cbd5e1";
                recLivePreview.textContent = "Listening for speech...";
            }
            if (SpeechRecognition) {
                try {
                    firSpeechRec = new SpeechRecognition();
                    firSpeechRec.continuous = true;
                    firSpeechRec.interimResults = true;
                    firSpeechRec.lang = 'en-IN';
                    firSpeechRec.onresult = (event) => {
                        let interim = "";
                        let final = "";
                        for (let i = 0; i < event.results.length; ++i) {
                            if (event.results[i].isFinal) {
                                final += event.results[i][0].transcript + " ";
                            } else {
                                interim += event.results[i][0].transcript;
                            }
                        }
                        firSpeechText = (final + interim).trim();
                        if (firSpeechText && recLivePreview) {
                            recLivePreview.style.fontStyle = "normal";
                            recLivePreview.style.color = "#ffffff";
                            recLivePreview.textContent = firSpeechText;
                        }
                    };
                    firSpeechRec.onerror = (e) => console.log("Speech recognition error:", e.error);
                    firSpeechRec.start();
                } catch (err) {
                    console.log("Web Speech fallback to Whisper:", err);
                }
            }
            firMediaRecorder.ondataavailable = (e) => {
                if (e.data.size > 0) firAudioChunks.push(e.data);
            };
            firMediaRecorder.onstop = async () => {
                stream.getTracks().forEach(t => t.stop());
                if (firSpeechRec) {
                    try { firSpeechRec.stop(); } catch(e) {}
                }
                clearInterval(firRecInterval);
                firIsRecording = false;
                micBtn.classList.remove("recording");
                if (voiceControls) voiceControls.classList.add("hidden");
                if (manualInputSection) manualInputSection.classList.remove("hidden");
                statusText.style.color = "#f59e0b";
                statusText.innerText = "Transcribing voice recording...";
                const audioBlob = new Blob(firAudioChunks, { type: 'audio/webm' });
                let finalNarrative = firSpeechText;
                try {
                    const formData = new FormData();
                    formData.append("audio", audioBlob, "dictation.webm");
                    const resp = await fetch("http://localhost:8000/api/transcribe_audio", {
                        method: "POST",
                        body: formData
                    });
                    if (resp.ok) {
                        const data = await resp.json();
                        if (data.text && data.text.length > 2) {
                            finalNarrative = data.text;
                        }
                    }
                } catch (err) {
                    console.error("Backend whisper fetch failed, relying on browser speech:", err);
                }
                if (!finalNarrative || finalNarrative.trim().length === 0) {
                    alert("No speech detected in audio recording. Please try speaking louder or enter text manually.");
                    statusText.innerText = "Tap mic to start real voice dictation (regional or English)";
                    statusText.style.color = "var(--text-secondary)";
                    return;
                }
                manualInput.value = finalNarrative;
                processPipeline(finalNarrative, 'voice');
            };
            firMediaRecorder.start();
            firIsRecording = true;
            firRecSeconds = 0;
            micBtn.classList.add("recording");
            if (voiceControls) voiceControls.classList.remove("hidden");
            if (manualInputSection) manualInputSection.classList.add("hidden");
            if (btnPauseRec) btnPauseRec.classList.remove("hidden");
            if (btnResumeRec) btnResumeRec.classList.add("hidden");
            if (recIndicatorDot) {
                recIndicatorDot.style.background = "#ef4444";
                recIndicatorDot.style.boxShadow = "0 0 10px #ef4444";
            }
            if (recStatusText) recStatusText.textContent = "Recording Voice...";
            if (recTimeDisplay) recTimeDisplay.textContent = "00:00";
            firRecInterval = setInterval(() => {
                firRecSeconds++;
                const mins = String(Math.floor(firRecSeconds / 60)).padStart(2, '0');
                const secs = String(firRecSeconds % 60).padStart(2, '0');
                if (recTimeDisplay) recTimeDisplay.textContent = `${mins}:${secs}`;
            }, 1000);
        } catch(e) {
            alert("Microphone access denied or unavailable. Please allow microphone permissions in your browser.");
            statusText.innerText = "Microphone access denied. Please type incident details below.";
            statusText.style.color = "#ef4444";
        }
    });
    if (btnPauseRec) {
        btnPauseRec.addEventListener("click", () => {
            if (!firMediaRecorder || firMediaRecorder.state !== "recording") return;
            firMediaRecorder.pause();
            if (firSpeechRec) {
                try { firSpeechRec.stop(); } catch(e){}
            }
            clearInterval(firRecInterval);
            btnPauseRec.classList.add("hidden");
            if (btnResumeRec) btnResumeRec.classList.remove("hidden");
            if (recIndicatorDot) {
                recIndicatorDot.style.background = "#f59e0b";
                recIndicatorDot.style.boxShadow = "0 0 10px #f59e0b";
            }
            if (recStatusText) recStatusText.textContent = "Recording Paused";
            statusText.innerText = "Voice recording paused.";
        });
    }
    if (btnResumeRec) {
        btnResumeRec.addEventListener("click", () => {
            if (!firMediaRecorder || firMediaRecorder.state !== "paused") return;
            firMediaRecorder.resume();
            if (firSpeechRec) {
                try { firSpeechRec.start(); } catch(e){}
            }
            btnResumeRec.classList.add("hidden");
            if (btnPauseRec) btnPauseRec.classList.remove("hidden");
            if (recIndicatorDot) {
                recIndicatorDot.style.background = "#ef4444";
                recIndicatorDot.style.boxShadow = "0 0 10px #ef4444";
            }
            if (recStatusText) recStatusText.textContent = "Recording Voice...";
            statusText.innerText = "Listening...";
            firRecInterval = setInterval(() => {
                firRecSeconds++;
                const mins = String(Math.floor(firRecSeconds / 60)).padStart(2, '0');
                const secs = String(firRecSeconds % 60).padStart(2, '0');
                if (recTimeDisplay) recTimeDisplay.textContent = `${mins}:${secs}`;
            }, 1000);
        });
    }
    if (btnStopRec) {
        btnStopRec.addEventListener("click", () => {
            if (!firMediaRecorder || !firIsRecording) return;
            firMediaRecorder.stop();
        });
    }
    manualInput.addEventListener("focus", () => {
        if(!isLocationSelected()) {
            manualInput.blur();
        }
    });
    submitTextBtn.addEventListener("click", () => {
        if(isProcessing) return;
        if(!isLocationSelected()) return;
        const text = manualInput.value.trim();
        if(!text) {
            alert("Please enter the incident details first.");
            return;
        }
        processPipeline(text, 'text');
    });
    function updateProgress(percent) {
        aiProgress.style.width = percent + "%";
    }
    async function processPipeline(narrativeText, sourceMode) {
        isProcessing = true;
        stepExtraction.classList.add("hidden");
        stepSections.classList.add("hidden");
        stepFir.classList.add("hidden");
        factsContainer.innerHTML = "";
        sectionsContainer.innerHTML = "";
        firDraftContent.innerHTML = "";
        firDraftContent.contentEditable = "false";
        transcriptBox.classList.add("hidden");
        currentCaseData = null;
        if (sourceMode === 'voice' || sourceMode === true) {
            statusText.style.color = "#10b981";
            statusText.innerText = "Voice audio transcribed. Initiating AI Pipeline...";
            transcriptBox.classList.remove("hidden");
            liveTranscript.textContent = narrativeText;
        } else {
            statusText.style.color = "#f59e0b";
            statusText.innerText = "Manual input received. Initiating AI Pipeline...";
            transcriptBox.classList.remove("hidden");
            liveTranscript.textContent = narrativeText;
        }
        statusText.innerText = "Initiating AI Pipeline (Calling Backend API)...";
        aiProgressContainer.classList.remove("hidden");
        updateProgress(20);
        try {
            const response = await fetch("http://localhost:8000/api/generate_fir", {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify({ 
                    narrative: narrativeText,
                    state: stateSelect.value,
                    district: districtSelect.value,
                    police_station: stationSelect.value
                })
            });
            if (!response.ok) {
                const errData = await response.json();
                throw new Error(errData.detail || "Server error");
            }
            const data = await response.json();
            updateProgress(50);
            statusText.innerText = "AI Investigator finished extracting facts...";
            stepExtraction.classList.remove("hidden");
            let i = 0;
            for (const [key, value] of Object.entries(data.facts)) {
                if (key === "error" || key === "raw" || key === "case_title") continue;
                const div = document.createElement("div");
                div.className = "fact-card";
                div.style.animationDelay = `${i * 0.1}s`;
                const formattedKey = key.replace(/_/g, " ").replace(/\b\w/g, l => l.toUpperCase());
                div.innerHTML = `
                    <div class="fact-label">${formattedKey}</div>
                    <div class="fact-value">${value}</div>
                `;
                factsContainer.appendChild(div);
                i++;
                await sleep(100);
            }
            await sleep(1000);
            updateProgress(75);
            statusText.innerText = "Magistrate Agent retrieved BNS Sections...";
            stepSections.classList.remove("hidden");
            data.sections.forEach((sec, idx) => {
                const div = document.createElement("div");
                div.className = "section-item";
                div.style.animationDelay = `${idx * 0.15}s`;
                const cogClass = sec.cognizable && sec.cognizable.toLowerCase().includes("non") ? "tag-green" : "tag-red";
                const bailClass = sec.bailable && sec.bailable.toLowerCase().includes("non") ? "tag-red" : "tag-green";
                let confClass = "conf-low";
                const confStr = (sec.confidence || "").toLowerCase();
                if(confStr.includes("high")) confClass = "conf-high";
                else if (confStr.includes("medium") || confStr.includes("med")) confClass = "conf-med";
                div.innerHTML = `
                    <div class="confidence-badge ${confClass}">${sec.confidence || 'Medium Confidence'}</div>
                    <div class="section-subtitle">${sec.section_number || ''} — ${sec.chapter_name || 'Offences'}</div>
                    <div class="section-title">${sec.short_title || 'Legal Section'}</div>
                    <div class="section-reason">" ${sec.reason || 'Applicable based on narrative.'} "</div>
                    <div class="section-desc">${sec.punishment || 'See detailed text'}</div>
                    <div class="section-footer">
                        <span>Old IPC equivalent: ${sec.ipc_equivalent || 'Unknown'}</span>
                        <div class="tag-container">
                            <span class="${cogClass}">${sec.cognizable || 'Unknown'}</span>
                            <span class="${bailClass}">${sec.bailable || 'Unknown'}</span>
                        </div>
                    </div>
                `;
                div.addEventListener("click", () => {
                    modalTitle.innerText = `${sec.section_number} - ${sec.short_title}`;
                    modalFullText.innerText = sec.full_text || "No detailed text available.";
                    sectionModal.classList.remove("hidden");
                });
                sectionsContainer.appendChild(div);
            });
            await sleep(1000);
            updateProgress(100);
            statusText.innerText = "Clerk Agent drafted FIR successfully.";
            stepFir.classList.remove("hidden");
            const panelContent = document.querySelector('.panel-content');
            panelContent.scrollTo({ top: panelContent.scrollHeight, behavior: 'smooth' });
            firDraftContent.innerHTML = data.fir;
            currentCaseData = {
                id: Date.now().toString(),
                title: data.facts.case_title || "Unnamed Incident",
                date: new Date().toLocaleDateString(),
                location: `${stationSelect.value}, ${districtSelect.value}, ${stateSelect.value}`,
                firHTML: data.fir
            };
        } catch (error) {
            statusText.style.color = "#ef4444";
            statusText.innerText = `Error: ${error.message}`;
            updateProgress(0);
        } finally {
            isProcessing = false;
            setTimeout(() => {
                aiProgressContainer.classList.add("hidden");
            }, 2000);
        }
    }
    function sleep(ms) {
        return new Promise(resolve => setTimeout(resolve, ms));
    }
    async function typeText(element, text, speed) {
        element.innerHTML = "";
        for(let i=0; i<text.length; i++) {
            if (text.charAt(i) === '\n') {
                element.innerHTML += '<br>';
            } else {
                element.innerHTML += text.charAt(i);
            }
            if (i % 2 === 0) await sleep(speed);
        }
    }
    (function initWitnessAnalyzer() {
        const witnessMicBtn = document.getElementById("witness-mic-btn");
        const witnessRecStatus = document.getElementById("witness-rec-status");
        const witnessRecTimer = document.getElementById("witness-rec-timer");
        const witnessUploadZone = document.getElementById("witness-upload-zone");
        const witnessFileInput = document.getElementById("witness-file-input");
        const witnessAudioPreview = document.getElementById("witness-audio-preview");
        const witnessAudioPlayer = document.getElementById("witness-audio-player");
        const witnessFileName = document.getElementById("witness-file-name");
        const witnessPrevStatement = document.getElementById("witness-prev-statement");
        const btnAnalyze = document.getElementById("btn-analyze-witness");
        const waLoading = document.getElementById("wa-loading");
        const waLoadingText = document.getElementById("wa-loading-text");
        const waResults = document.getElementById("wa-results");
        const witnessVoiceControls = document.getElementById("witness-voice-controls");
        const waBtnPause = document.getElementById("wa-btn-pause");
        const waBtnResume = document.getElementById("wa-btn-resume");
        const waBtnStop = document.getElementById("wa-btn-stop");
        if (!witnessMicBtn) return;
        let mediaRecorder = null;
        let audioChunks = [];
        let isRecording = false;
        let recordingTimer = null;
        let recordingSeconds = 0;
        let currentAudioBlob = null;
        witnessMicBtn.addEventListener("click", async () => {
            if (isRecording) {
                mediaRecorder.stop();
                witnessMicBtn.classList.remove("recording");
                witnessRecStatus.textContent = "Processing...";
                witnessRecTimer.style.display = "none";
                clearInterval(recordingTimer);
                isRecording = false;
                if (witnessVoiceControls) witnessVoiceControls.classList.add("hidden");
            } else {
                try {
                    const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
                    mediaRecorder = new MediaRecorder(stream, { mimeType: 'audio/webm;codecs=opus' });
                    audioChunks = [];
                    mediaRecorder.ondataavailable = (e) => {
                        if (e.data.size > 0) audioChunks.push(e.data);
                    };
                    mediaRecorder.onstop = () => {
                        currentAudioBlob = new Blob(audioChunks, { type: 'audio/webm' });
                        const url = URL.createObjectURL(currentAudioBlob);
                        witnessAudioPlayer.src = url;
                        witnessFileName.textContent = `Recorded audio (${recordingSeconds}s)`;
                        witnessAudioPreview.classList.remove("hidden");
                        witnessRecStatus.textContent = "Recording saved. Ready to analyze.";
                        btnAnalyze.disabled = false;
                        if (witnessVoiceControls) witnessVoiceControls.classList.add("hidden");
                        stream.getTracks().forEach(t => t.stop());
                    };
                    mediaRecorder.start();
                    isRecording = true;
                    recordingSeconds = 0;
                    witnessMicBtn.classList.add("recording");
                    witnessRecStatus.textContent = "Recording... Use buttons below to pause or stop";
                    witnessRecTimer.style.display = "block";
                    witnessRecTimer.textContent = "00:00";
                    if (witnessVoiceControls) witnessVoiceControls.classList.remove("hidden");
                    if (waBtnPause) waBtnPause.classList.remove("hidden");
                    if (waBtnResume) waBtnResume.classList.add("hidden");
                    recordingTimer = setInterval(() => {
                        recordingSeconds++;
                        const mins = String(Math.floor(recordingSeconds / 60)).padStart(2, '0');
                        const secs = String(recordingSeconds % 60).padStart(2, '0');
                        witnessRecTimer.textContent = `${mins}:${secs}`;
                    }, 1000);
                } catch(err) {
                    witnessRecStatus.textContent = "Microphone access denied. Please allow microphone.";
                    witnessRecStatus.style.color = "#ef4444";
                }
            }
        });
        if (waBtnPause) {
            waBtnPause.addEventListener("click", () => {
                if (!mediaRecorder || mediaRecorder.state !== "recording") return;
                mediaRecorder.pause();
                clearInterval(recordingTimer);
                waBtnPause.classList.add("hidden");
                if (waBtnResume) waBtnResume.classList.remove("hidden");
                witnessRecStatus.textContent = "Recording Paused";
            });
        }
        if (waBtnResume) {
            waBtnResume.addEventListener("click", () => {
                if (!mediaRecorder || mediaRecorder.state !== "paused") return;
                mediaRecorder.resume();
                waBtnResume.classList.add("hidden");
                if (waBtnPause) waBtnPause.classList.remove("hidden");
                witnessRecStatus.textContent = "Recording... Use buttons below to pause or stop";
                recordingTimer = setInterval(() => {
                    recordingSeconds++;
                    const mins = String(Math.floor(recordingSeconds / 60)).padStart(2, '0');
                    const secs = String(recordingSeconds % 60).padStart(2, '0');
                    witnessRecTimer.textContent = `${mins}:${secs}`;
                }, 1000);
            });
        }
        if (waBtnStop) {
            waBtnStop.addEventListener("click", () => {
                if (!mediaRecorder || !isRecording) return;
                mediaRecorder.stop();
                witnessMicBtn.classList.remove("recording");
                witnessRecStatus.textContent = "Processing audio...";
                witnessRecTimer.style.display = "none";
                clearInterval(recordingTimer);
                isRecording = false;
                if (witnessVoiceControls) witnessVoiceControls.classList.add("hidden");
            });
        }
        witnessUploadZone.addEventListener("click", () => witnessFileInput.click());
        witnessFileInput.addEventListener("change", (e) => {
            const file = e.target.files[0];
            if (file) {
                currentAudioBlob = file;
                const url = URL.createObjectURL(file);
                witnessAudioPlayer.src = url;
                witnessFileName.textContent = file.name;
                witnessAudioPreview.classList.remove("hidden");
                witnessRecStatus.textContent = "File loaded. Ready to analyze.";
                btnAnalyze.disabled = false;
            }
        });
        witnessUploadZone.addEventListener("dragover", (e) => {
            e.preventDefault();
            witnessUploadZone.style.borderColor = "var(--gold)";
        });
        witnessUploadZone.addEventListener("dragleave", () => {
            witnessUploadZone.style.borderColor = "var(--border-glass)";
        });
        witnessUploadZone.addEventListener("drop", (e) => {
            e.preventDefault();
            witnessUploadZone.style.borderColor = "var(--border-glass)";
            const file = e.dataTransfer.files[0];
            if (file && file.type.startsWith('audio/')) {
                currentAudioBlob = file;
                const url = URL.createObjectURL(file);
                witnessAudioPlayer.src = url;
                witnessFileName.textContent = file.name;
                witnessAudioPreview.classList.remove("hidden");
                witnessRecStatus.textContent = "File loaded. Ready to analyze.";
                btnAnalyze.disabled = false;
            }
        });
        btnAnalyze.addEventListener("click", async () => {
            if (!currentAudioBlob) return;
            btnAnalyze.disabled = true;
            waLoading.classList.remove("hidden");
            waResults.classList.add("hidden");
            waLoadingText.textContent = "Whisper is transcribing the audio locally...";
            const formData = new FormData();
            const fileName = currentAudioBlob.name || 'recording.webm';
            formData.append('audio', currentAudioBlob, fileName);
            formData.append('previous_statement', witnessPrevStatement.value || '');
            try {
                const response = await fetch("http://localhost:8000/api/analyze_witness", {
                    method: "POST",
                    body: formData
                });
                if (!response.ok) {
                    const err = await response.json();
                    throw new Error(err.detail || "Server error");
                }
                const data = await response.json();
                renderWitnessResults(data);
            } catch(e) {
                alert("Error analyzing audio: " + e.message);
            } finally {
                btnAnalyze.disabled = false;
                waLoading.classList.add("hidden");
            }
        });
        function renderWitnessResults(data) {
            const langMap = { hi: 'Hindi', mr: 'Marathi', ta: 'Tamil', te: 'Telugu', bn: 'Bengali', en: 'English', gu: 'Gujarati', kn: 'Kannada', ml: 'Malayalam', pa: 'Punjabi', ur: 'Urdu' };
            document.getElementById("wa-lang").textContent = langMap[data.detected_language] || data.detected_language;
            document.getElementById("wa-original").textContent = data.original_text;
            document.getElementById("wa-translation").textContent = data.legal_translation;
            const factsDiv = document.getElementById("wa-facts");
            factsDiv.innerHTML = "";
            const facts = data.key_facts || {};
            if (typeof facts === 'object' && !Array.isArray(facts)) {
                for (const [key, val] of Object.entries(facts)) {
                    const card = document.createElement("div");
                    card.className = "fact-card";
                    const label = key.replace(/_/g, ' ').replace(/\b\w/g, l => l.toUpperCase());
                    card.innerHTML = `<div class="fact-label">${label}</div><div class="fact-value">${val}</div>`;
                    factsDiv.appendChild(card);
                }
            } else if (Array.isArray(facts)) {
                facts.forEach(f => {
                    const card = document.createElement("div");
                    card.className = "fact-card";
                    card.innerHTML = `<div class="fact-value">${f}</div>`;
                    factsDiv.appendChild(card);
                });
            }
            const stressDiv = document.getElementById("wa-stress");
            stressDiv.innerHTML = "";
            const sa = data.stress_analysis || {};
            const metrics = [
                { label: "Avg Pitch", value: `${sa.pitch_mean || 0} Hz`, sub: `Std Dev: ${sa.pitch_std || 0}` },
                { label: "Speech Rate", value: `${sa.speech_rate_wps || 0} w/s`, sub: `Duration: ${sa.duration_seconds || 0}s` },
                { label: "Avg Pause", value: `${sa.avg_pause_duration || 0}s`, sub: `Between key phrases` }
            ];
            metrics.forEach(m => {
                const card = document.createElement("div");
                card.style.cssText = "background: rgba(0,0,0,0.3); padding: 16px; border-radius: 8px; text-align: center;";
                card.innerHTML = `
                    <div style="font-size: 12px; color: var(--text-secondary); margin-bottom: 4px;">${m.label}</div>
                    <div style="font-size: 20px; font-weight: 700; color: var(--text-primary);">${m.value}</div>
                    <div style="font-size: 11px; color: var(--text-secondary); margin-top: 4px;">${m.sub}</div>
                `;
                stressDiv.appendChild(card);
            });
            const alertDiv = document.getElementById("wa-stress-alert");
            const level = (sa.stress_level || "LOW").toUpperCase();
            const prob = sa.coercion_probability || 0;
            if (level === "HIGH") {
                alertDiv.style.background = "rgba(239, 68, 68, 0.1)";
                alertDiv.style.border = "1px solid rgba(239, 68, 68, 0.3)";
                alertDiv.style.color = "#ef4444";
                alertDiv.innerHTML = `<i class="ph-fill ph-warning-circle" style="font-size: 18px;"></i> HIGH STRESS DETECTED (${prob}% coercion probability). ${sa.analysis_notes || ''}`;
            } else if (level === "MEDIUM") {
                alertDiv.style.background = "rgba(245, 158, 11, 0.1)";
                alertDiv.style.border = "1px solid rgba(245, 158, 11, 0.3)";
                alertDiv.style.color = "#f59e0b";
                alertDiv.innerHTML = `<i class="ph-fill ph-info" style="font-size: 18px;"></i> MODERATE STRESS (${prob}% coercion probability). ${sa.analysis_notes || ''}`;
            } else {
                alertDiv.style.background = "rgba(16, 185, 129, 0.1)";
                alertDiv.style.border = "1px solid rgba(16, 185, 129, 0.3)";
                alertDiv.style.color = "#10b981";
                alertDiv.innerHTML = `<i class="ph-fill ph-check-circle" style="font-size: 18px;"></i> LOW STRESS — Speech patterns natural (${prob}% coercion probability). ${sa.analysis_notes || ''}`;
            }
            alertDiv.classList.remove("hidden");
            alertDiv.style.display = "flex";
            const questionsPanel = document.getElementById("wa-questions-panel");
            const questionsList = document.getElementById("wa-questions-list");
            questionsList.innerHTML = "";
            if (data.interrogation_questions && data.interrogation_questions.length > 0) {
                questionsPanel.classList.remove("hidden");
                data.interrogation_questions.forEach((q, idx) => {
                    const priorityColors = {
                        'CRITICAL': { bg: 'rgba(239, 68, 68, 0.1)', border: 'rgba(239, 68, 68, 0.4)', text: '#ef4444', icon: '🔴' },
                        'IMPORTANT': { bg: 'rgba(245, 158, 11, 0.1)', border: 'rgba(245, 158, 11, 0.4)', text: '#f59e0b', icon: '🟡' },
                        'SUPPLEMENTARY': { bg: 'rgba(59, 130, 246, 0.1)', border: 'rgba(59, 130, 246, 0.4)', text: '#3b82f6', icon: '🔵' }
                    };
                    const style = priorityColors[q.priority] || priorityColors['SUPPLEMENTARY'];
                    const categoryLabels = {
                        'IDENTIFICATION': '🪪 Identification',
                        'TIMELINE': '⏰ Timeline',
                        'EVIDENCE': '🔍 Evidence',
                        'VISIBILITY': '👁️ Visibility',
                        'ESCAPE_ROUTE': '🏃 Escape Route',
                        'CORROBORATION': '🤝 Corroboration'
                    };
                    const catLabel = categoryLabels[q.category] || q.category || '';
                    const card = document.createElement("div");
                    card.style.cssText = `background: ${style.bg}; border: 1px solid ${style.border}; border-radius: 12px; padding: 16px; animation: fadeIn 0.4s ease ${idx * 0.1}s both;`;
                    card.innerHTML = `
                        <div style="display: flex; align-items: center; gap: 8px; margin-bottom: 8px;">
                            <span style="font-size: 14px;">${style.icon}</span>
                            <span style="font-size: 11px; font-weight: 700; color: ${style.text}; text-transform: uppercase; letter-spacing: 0.5px;">${q.priority}</span>
                            <span style="margin-left: auto; font-size: 11px; background: rgba(255,255,255,0.08); padding: 2px 10px; border-radius: 20px; color: var(--text-secondary);">${catLabel}</span>
                        </div>
                        <p style="color: var(--text-primary); font-size: 14px; font-weight: 500; line-height: 1.5; margin-bottom: 6px;">"${q.question}"</p>
                        <p style="color: var(--text-secondary); font-size: 12px; line-height: 1.4;"><i class="ph ph-lightbulb" style="color: #f59e0b;"></i> ${q.purpose}</p>
                    `;
                    questionsList.appendChild(card);
                });
            } else {
                questionsPanel.classList.add("hidden");
            }
            const contPanel = document.getElementById("wa-contradictions-panel");
            const contBody = document.getElementById("wa-contradictions-body");
            contBody.innerHTML = "";
            if (data.contradictions && data.contradictions.length > 0) {
                contPanel.classList.remove("hidden");
                data.contradictions.forEach(c => {
                    const row = document.createElement("tr");
                    row.style.borderBottom = "1px solid rgba(255,255,255,0.05)";
                    const statusColor = c.status === "CONTRADICTION" ? "#ef4444" : "#10b981";
                    const statusIcon = c.status === "CONTRADICTION" ? "⚠️" : "✅";
                    row.innerHTML = `
                        <td style="padding: 12px; font-weight: 500;">${c.parameter}</td>
                        <td style="padding: 12px;">${c.previous_value}</td>
                        <td style="padding: 12px;">${c.current_value}</td>
                        <td style="padding: 12px;"><span style="color: ${statusColor}; font-weight: bold;">${statusIcon} ${c.status}</span></td>
                    `;
                    contBody.appendChild(row);
                });
            } else {
                contPanel.classList.add("hidden");
            }
            waResults.classList.remove("hidden");
            waResults.scrollIntoView({ behavior: 'smooth' });
        }
    })();
});
const chatFab = document.getElementById("chat-fab");
const chatPanel = document.getElementById("chat-panel");
const chatCloseBtn = document.getElementById("chat-close-btn");
const chatInput = document.getElementById("chat-input");
const chatSendBtn = document.getElementById("chat-send-btn");
const chatMessages = document.getElementById("chat-messages");
let chatHistoryStr = "";
chatFab.addEventListener("click", () => {
    chatPanel.classList.remove("hidden");
    chatInput.focus();
});
chatCloseBtn.addEventListener("click", () => {
    chatPanel.classList.add("hidden");
});
function formatChatText(text) {
    let formatted = text.replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>');
    formatted = formatted.replace(/\n/g, '<br/>');
    return formatted;
}
function appendMessage(role, text) {
    const msgDiv = document.createElement("div");
    msgDiv.className = `message ${role}-message`;
    const contentDiv = document.createElement("div");
    contentDiv.className = "message-content";
    if (role === 'ai') {
        contentDiv.innerHTML = formatChatText(text);
    } else {
        contentDiv.textContent = text;
    }
    msgDiv.appendChild(contentDiv);
    chatMessages.appendChild(msgDiv);
    chatMessages.scrollTop = chatMessages.scrollHeight;
}
function showTypingIndicator() {
    const msgDiv = document.createElement("div");
    msgDiv.className = "message ai-message typing-box";
    msgDiv.id = "typing-indicator";
    const contentDiv = document.createElement("div");
    contentDiv.className = "message-content typing-indicator";
    contentDiv.innerHTML = `
        <div class="typing-dot"></div>
        <div class="typing-dot"></div>
        <div class="typing-dot"></div>
    `;
    msgDiv.appendChild(contentDiv);
    chatMessages.appendChild(msgDiv);
    chatMessages.scrollTop = chatMessages.scrollHeight;
}
function removeTypingIndicator() {
    const indicator = document.getElementById("typing-indicator");
    if (indicator) {
        indicator.remove();
    }
}
async function typeMessage(text) {
    const msgDiv = document.createElement("div");
    msgDiv.className = `message ai-message`;
    const contentDiv = document.createElement("div");
    contentDiv.className = "message-content";
    msgDiv.appendChild(contentDiv);
    chatMessages.appendChild(msgDiv);
    const htmlText = formatChatText(text);
    const words = htmlText.split(' ');
    contentDiv.innerHTML = '';
    for (let i = 0; i < words.length; i++) {
        contentDiv.innerHTML += words[i] + ' ';
        chatMessages.scrollTop = chatMessages.scrollHeight;
        await new Promise(r => setTimeout(r, 20));
    }
}
async function sendChatMessage() {
    const question = chatInput.value.trim();
    if (!question) return;
    appendMessage('user', question);
    chatInput.value = "";
    chatHistoryStr += `User: ${question}\n`;
    showTypingIndicator();
    try {
        const response = await fetch("http://localhost:8000/api/legal_chat", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({
                question: question,
                history: chatHistoryStr
            })
        });
        removeTypingIndicator();
        if (!response.ok) throw new Error("API Error");
        const data = await response.json();
        chatHistoryStr += `AI: ${data.answer}\n`;
        await typeMessage(data.answer);
    } catch (error) {
        removeTypingIndicator();
        appendMessage('ai', 'Error connecting to the legal knowledge base.');
    }
}
chatSendBtn.addEventListener("click", sendChatMessage);
chatInput.addEventListener("keypress", (e) => {
    if (e.key === "Enter") {
        sendChatMessage();
    }
});
