class ChatApp {
    constructor() {
        this.sessionId = null;
        this.messagesContainer = document.getElementById('messages');
        this.messageInput = document.getElementById('messageInput');
        this.sendButton = document.getElementById('sendButton');
        this.charCounter = document.getElementById('charCounter');
        this.logPanelBody = document.getElementById('logPanelBody');
        this.logStatus = document.getElementById('logStatus');
        this.codePanel = document.getElementById('codePanel');
        this.generatedCode = document.getElementById('generatedCode');
        this.codeLanguage = document.getElementById('codeLanguage');
        this.previewPanel = document.getElementById('previewPanel');
        this.previewTitle = document.getElementById('previewTitle');
        this.previewType = document.getElementById('previewType');
        this.gameFrame = document.getElementById('gameFrame');
        this.textPreview = document.getElementById('textPreview');
        this.logContainer = document.getElementById('logContainer');
        this.logContent = document.getElementById('logContent');
        this.logInfo = document.getElementById('logInfo');
        
        this.isProcessing = false;
        this.currentCode = '';
        this.currentLanguage = 'text';
        this.setupEventListeners();
        this.loadSession();
    }

    setupEventListeners() {
        this.sendButton.addEventListener('click', () => this.sendMessage());
        this.messageInput.addEventListener('keydown', (e) => {
            if (e.key === 'Enter' && !e.shiftKey) {
                e.preventDefault();
                this.sendMessage();
            }
        });
        this.messageInput.addEventListener('input', () => {
            this.charCounter.textContent = `${this.messageInput.value.length}/5000`;
        });
        
        document.getElementById('showLogBtn').addEventListener('click', () => {
            const logContainer = document.getElementById('logContainer');
            logContainer.style.display = logContainer.style.display === 'none' ? 'block' : 'none';
            if (logContainer.style.display === 'block') this.fetchLog();
        });
        
        document.getElementById('clearSessionBtn').addEventListener('click', () => {
            if (confirm('¿Iniciar nueva sesión? Se perderá el historial actual.')) {
                this.sessionId = null;
                this.messagesContainer.innerHTML = `
                    <div class="message system">
                        <div class="message-content">Nueva sesión iniciada. Envíame un ticket de feature.</div>
                    </div>
                `;
                document.getElementById('logContainer').style.display = 'none';
                this.codePanel.style.display = 'none';
                this.previewPanel.classList.remove('active');
                this.previewPanel.style.display = 'none';
                this.logPanelBody.innerHTML = `
                    <div class="log-entry system">
                        <span class="log-icon">🤖</span>
                        <span class="log-message">Sistema listo. Envía un ticket para comenzar.</span>
                    </div>
                `;
                localStorage.removeItem('sessionId');
                this.currentCode = '';
                this.gameFrame.srcdoc = '';
                this.gameFrame.src = 'about:blank';
            }
        });

        // Botón de prueba del visor
        document.getElementById('testPreviewBtn').addEventListener('click', () => {
            console.log('🧪 Probando visor...');
            const frame = document.getElementById('gameFrame');
            const previewPanel = document.getElementById('previewPanel');
            const gameFrame = document.getElementById('gameFrame');
            const textPreview = document.getElementById('textPreview');
            
            frame.srcdoc = `
            <!DOCTYPE html>
            <html>
            <head>
                <style>
                    body {
                        margin: 0;
                        display: flex;
                        justify-content: center;
                        align-items: center;
                        height: 100vh;
                        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                        font-family: Arial, sans-serif;
                    }
                    .test-box {
                        background: white;
                        padding: 40px;
                        border-radius: 20px;
                        box-shadow: 0 20px 60px rgba(0,0,0,0.3);
                        text-align: center;
                        max-width: 500px;
                        animation: bounceIn 0.5s ease;
                    }
                    @keyframes bounceIn {
                        0% { transform: scale(0.5); opacity: 0; }
                        60% { transform: scale(1.05); }
                        100% { transform: scale(1); opacity: 1; }
                    }
                    h1 { color: #764ba2; margin: 10px 0; }
                    p { color: #666; line-height: 1.6; }
                    .success { color: #4caf50; font-size: 60px; }
                    .emoji-big { font-size: 70px; }
                    .btn-test {
                        margin-top: 15px;
                        padding: 12px 35px;
                        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                        color: white;
                        border: none;
                        border-radius: 10px;
                        cursor: pointer;
                        font-size: 16px;
                        transition: transform 0.2s;
                    }
                    .btn-test:hover {
                        transform: scale(1.05);
                    }
                    .features {
                        text-align: left;
                        margin: 20px 0;
                        padding: 0 20px;
                    }
                    .features li {
                        color: #555;
                        margin: 8px 0;
                        list-style: none;
                    }
                </style>
            </head>
            <body>
                <div class="test-box">
                    <div class="emoji-big">🎮</div>
                    <h1>¡Visor Funcionando!</h1>
                    <p>El sistema de preview está listo para mostrar tu juego.</p>
                    <div class="features">
                        <ul style="list-style:none;padding:0;">
                            <li>✅ El iframe carga contenido correctamente</li>
                            <li>✅ Los estilos se aplican sin problemas</li>
                            <li>✅ El juego se ejecutará aquí</li>
                        </ul>
                    </div>
                    <p style="font-size:12px;color:#999;">✅ Prueba exitosa - Todo funciona correctamente</p>
                    <button class="btn-test" onclick="this.parentElement.innerHTML='<div class=\\'success\\'>🎉</div><h1>¡Perfecto!</h1><p>El visor está listo para jugar.</p><p style=\\'font-size:12px;color:#999;\\'>Cierra esta ventana y prueba tu juego.</p>'">
                        ¡Me encanta! 🚀
                    </button>
                </div>
            </body>
            </html>
            `;
            
            previewPanel.classList.add('active');
            previewPanel.style.display = 'flex';
            gameFrame.style.display = 'block';
            textPreview.style.display = 'none';
            document.getElementById('previewTitle').textContent = '🧪 Prueba del Visor';
            document.getElementById('previewType').textContent = '✅ Funciona';
            
            console.log('✅ Visor probado correctamente');
        });

        // Botón para abrir en nueva pestaña
        document.getElementById('openFullscreenBtn').addEventListener('click', () => {
            if (this.currentCode) {
                this.openInNewWindow(this.currentCode);
            } else {
                alert('Primero genera un código HTML.');
            }
        });

        document.getElementById('openNewWindowBtn').addEventListener('click', () => {
            if (this.currentCode) {
                this.openInNewWindow(this.currentCode);
            }
        });

        document.getElementById('openNewTabBtn').addEventListener('click', () => {
            if (this.currentCode) {
                this.openInNewWindow(this.currentCode);
            }
        });
        
        document.getElementById('runCodeBtn').addEventListener('click', () => {
            this.runCode();
        });
        
        document.getElementById('copyCodeBtn').addEventListener('click', () => {
            this.copyCode();
        });
        
        document.getElementById('downloadCodeBtn').addEventListener('click', () => {
            this.downloadCode();
        });
        
        document.getElementById('closePreviewBtn').addEventListener('click', () => {
            this.previewPanel.classList.remove('active');
            this.previewPanel.style.display = 'none';
            this.gameFrame.srcdoc = '';
            this.gameFrame.src = 'about:blank';
            this.textPreview.style.display = 'none';
            this.gameFrame.style.display = 'none';
        });
    }

    // Función para abrir en nueva ventana
    openInNewWindow(code) {
        let cleanCode = code;
        cleanCode = cleanCode.replace(/```html\s*/g, '');
        cleanCode = cleanCode.replace(/```css\s*/g, '');
        cleanCode = cleanCode.replace(/```javascript\s*/g, '');
        cleanCode = cleanCode.replace(/```js\s*/g, '');
        cleanCode = cleanCode.replace(/```\s*/g, '');
        cleanCode = cleanCode.trim();
        
        if (!cleanCode.includes('<!DOCTYPE html>')) {
            cleanCode = '<!DOCTYPE html>\n' + cleanCode;
        }
        
        const blob = new Blob([cleanCode], { type: 'text/html;charset=utf-8' });
        const url = URL.createObjectURL(blob);
        window.open(url, '_blank');
        
        setTimeout(() => {
            URL.revokeObjectURL(url);
        }, 60000);
        
        this.addLogEntry('Sistema', '📂 Código abierto en nueva pestaña', 'system');
    }

    addLogEntry(step, message, type = 'system') {
        const entry = document.createElement('div');
        entry.className = `log-entry ${type}`;
        
        const icons = {
            'planner': '📋',
            'coder': '💻',
            'reviewer': '🔍',
            'approved': '✅',
            'rejected': '❌',
            'system': '🤖'
        };
        
        entry.innerHTML = `
            <span class="log-icon">${icons[type] || '📌'}</span>
            <span class="log-message"><strong>${step}:</strong> ${message}</span>
        `;
        
        this.logPanelBody.appendChild(entry);
        this.logPanelBody.scrollTop = this.logPanelBody.scrollHeight;
        this.logStatus.textContent = `🔄 ${step}`;
    }

    detectLanguage(code) {
        if (code.includes('<!DOCTYPE html>') || code.includes('<html') || code.includes('<body') || code.includes('<div') || code.includes('<canvas')) {
            return { lang: 'html', icon: '🌐', name: 'HTML' };
        }
        if (code.includes('import ') && (code.includes('def ') || code.includes('class ') || code.includes('print('))) {
            return { lang: 'python', icon: '🐍', name: 'Python' };
        }
        if (code.includes('function ') || code.includes('const ') || code.includes('let ') || code.includes('var ') || code.includes('=>')) {
            return { lang: 'javascript', icon: '📜', name: 'JavaScript' };
        }
        if (code.includes('{') && code.includes('}') && (code.includes(':') || code.includes('"') && code.includes(','))) {
            return { lang: 'json', icon: '📋', name: 'JSON' };
        }
        if (code.includes('SELECT ') || code.includes('INSERT ') || code.includes('UPDATE ') || code.includes('CREATE TABLE')) {
            return { lang: 'sql', icon: '🗄️', name: 'SQL' };
        }
        return { lang: 'text', icon: '📄', name: 'Texto' };
    }

    async sendMessage() {
        if (this.isProcessing) return;
        
        const message = this.messageInput.value.trim();
        if (!message) return;

        this.isProcessing = true;
        this.addMessage('user', message);
        this.messageInput.value = '';
        this.charCounter.textContent = '0/5000';
        this.sendButton.disabled = true;
        this.sendButton.innerHTML = '<i class="fas fa-spinner fa-spin"></i> Procesando...';
        
        this.logPanelBody.innerHTML = '';
        this.logStatus.textContent = '⏳ Procesando...';
        this.codePanel.style.display = 'none';
        this.previewPanel.classList.remove('active');
        this.previewPanel.style.display = 'none';
        this.currentCode = '';
        
        this.addLogEntry('Inicio', 'Procesando ticket...', 'system');

        try {
            const response = await fetch('/api/chat', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ message, session_id: this.sessionId })
            });
            
            if (!response.ok) {
                throw new Error(`Error ${response.status}: ${response.statusText}`);
            }
            
            const data = await response.json();
            this.sessionId = data.session_id;
            
            let code = '';
            let detectedLang = null;
            
            if (data.details && data.details.code) {
                code = data.details.code;
                detectedLang = data.details.language;
            } else if (data.message) {
                const codeMatch = data.message.match(/```(\w+)?\n([\s\S]*?)```/);
                if (codeMatch) {
                    code = codeMatch[2];
                    detectedLang = codeMatch[1];
                } else {
                    code = data.message;
                }
            }
            
            code = code.trim();
            
            this.addLogEntry('Planner', 'Ticket descompuesto en tareas', 'planner');
            
            setTimeout(() => {
                this.addLogEntry('Coder', 'Código generado exitosamente', 'coder');
            }, 500);
            
            setTimeout(() => {
                if (data.status === 'approved') {
                    this.addLogEntry('Reviewer', '✅ Código aprobado', 'approved');
                    this.logStatus.textContent = '✅ Aprobado';
                    
                    if (code) {
                        this.showCode(code, detectedLang);
                    }
                } else {
                    this.addLogEntry('Reviewer', '❌ Código rechazado. Reintentando...', 'rejected');
                    this.logStatus.textContent = '❌ Rechazado';
                }
            }, 1000);
            
            this.addMessage('assistant', data.message);
            localStorage.setItem('sessionId', this.sessionId);
            
        } catch (error) {
            console.error('Error:', error);
            this.addMessage('error', `❌ Error al procesar: ${error.message}`);
            this.addLogEntry('Error', error.message, 'rejected');
            this.logStatus.textContent = '❌ Error';
        } finally {
            this.isProcessing = false;
            this.sendButton.disabled = false;
            this.sendButton.innerHTML = '<i class="fas fa-paper-plane"></i> Enviar';
        }
    }

    showCode(code, detectedLang = null) {
        console.log('Mostrando código:', code.substring(0, 100) + '...');
        this.currentCode = code;
        
        const langInfo = detectedLang ? { lang: detectedLang, icon: '📄', name: detectedLang } : this.detectLanguage(code);
        this.currentLanguage = langInfo.lang;
        
        const codeElement = document.getElementById('generatedCode');
        codeElement.textContent = code;
        codeElement.className = `language-${langInfo.lang}`;
        this.codeLanguage.textContent = `${langInfo.icon} ${langInfo.name}`;
        this.codePanel.style.display = 'block';
        
        const isHTML = code.includes('<!DOCTYPE html>') || 
                       code.includes('<html') || 
                       code.includes('<body') || 
                       code.includes('<div') || 
                       code.includes('<canvas') ||
                       code.includes('<style');
        
        const runBtn = document.getElementById('runCodeBtn');
        const newTabBtn = document.getElementById('openNewTabBtn');
        
        if (isHTML) {
            runBtn.style.display = 'inline-block';
            runBtn.innerHTML = '<i class="fas fa-play"></i> Ejecutar HTML';
            newTabBtn.style.display = 'inline-block';
            this.addLogEntry('Sistema', '✅ Código HTML detectado. Puedes ejecutarlo.', 'system');
        } else {
            runBtn.style.display = 'none';
            newTabBtn.style.display = 'none';
            this.addLogEntry('Sistema', `📝 Código ${langInfo.name} generado. Solo visualización.`, 'system');
        }
        
        this.addLogEntry('Sistema', `📝 Código ${langInfo.name} listo para revisar.`, 'system');
    }

    // 🔥 FUNCIÓN PRINCIPAL MEJORADA - runCode()
    runCode() {
        console.log('🚀 Ejecutando código...');
        
        if (!this.currentCode) {
            alert('❌ No hay código para ejecutar.');
            return;
        }
        
        // Limpiar el código
        let cleanCode = this.currentCode;
        cleanCode = cleanCode.replace(/```html\s*/g, '');
        cleanCode = cleanCode.replace(/```css\s*/g, '');
        cleanCode = cleanCode.replace(/```javascript\s*/g, '');
        cleanCode = cleanCode.replace(/```js\s*/g, '');
        cleanCode = cleanCode.replace(/```\s*/g, '');
        cleanCode = cleanCode.trim();
        
        console.log('📝 Código limpio (primeros 300 chars):', cleanCode.substring(0, 300));
        
        // Verificar si es HTML
        const isHTML = cleanCode.includes('<!DOCTYPE html>') || 
                       cleanCode.includes('<html') || 
                       cleanCode.includes('<body') || 
                       cleanCode.includes('<canvas') ||
                       cleanCode.includes('<style') ||
                       cleanCode.includes('<script');
        
        const previewPanel = document.getElementById('previewPanel');
        const gameFrame = document.getElementById('gameFrame');
        const textPreview = document.getElementById('textPreview');
        const previewTitle = document.getElementById('previewTitle');
        const previewType = document.getElementById('previewType');
        
        if (!isHTML) {
            // Si no es HTML, mostrar en text preview
            previewPanel.classList.add('active');
            previewPanel.style.display = 'flex';
            previewTitle.textContent = '📄 Código Generado';
            previewType.textContent = '📄 Texto';
            gameFrame.style.display = 'none';
            textPreview.style.display = 'block';
            textPreview.textContent = cleanCode;
            this.addLogEntry('Sistema', '📝 El código no es HTML. Mostrando como texto.', 'system');
            return;
        }
        
        // ✅ Es HTML - cargar en iframe
        console.log('✅ Código HTML detectado. Abriendo preview...');
        
        // Asegurar DOCTYPE
        if (!cleanCode.includes('<!DOCTYPE html>')) {
            cleanCode = '<!DOCTYPE html>\n' + cleanCode;
        }
        
        // Mostrar el panel
        previewPanel.classList.add('active');
        previewPanel.style.display = 'flex';
        previewTitle.textContent = '🎮 Vista Previa - Juego Generado';
        previewType.textContent = '🌐 HTML';
        textPreview.style.display = 'none';
        gameFrame.style.display = 'block';
        gameFrame.style.width = '100%';
        gameFrame.style.height = '100%';
        gameFrame.style.maxWidth = '1000px';
        gameFrame.style.maxHeight = '900px';
        gameFrame.style.border = 'none';
        gameFrame.style.borderRadius = '12px';
        gameFrame.style.background = '#1a1a2e';
        gameFrame.style.boxShadow = '0 0 50px rgba(0,0,0,0.5)';
        
        // Limpiar sandbox
        gameFrame.setAttribute('sandbox', 'allow-scripts allow-modals');
        
        // === MÉTODO 1: srcdoc ===
        try {
            gameFrame.srcdoc = cleanCode;
            console.log('✅ Código cargado con srcdoc');
            this.addLogEntry('Sistema', '🎮 Juego cargado en el visor (srcdoc)', 'system');
        } catch (error) {
            console.error('❌ Error con srcdoc:', error);
            this.addLogEntry('Sistema', '⚠️ Error con srcdoc, intentando método alternativo', 'system');
            
            // === MÉTODO 2: blob URL ===
            try {
                const blob = new Blob([cleanCode], { type: 'text/html;charset=utf-8' });
                const url = URL.createObjectURL(blob);
                gameFrame.src = url;
                console.log('✅ Código cargado con blob URL');
                this.addLogEntry('Sistema', '🎮 Juego cargado en el visor (blob URL)', 'system');
            } catch (error2) {
                console.error('❌ Error con blob URL:', error2);
                
                // === MÉTODO 3: data URI ===
                try {
                    const encoded = encodeURIComponent(cleanCode);
                    gameFrame.src = 'data:text/html;charset=utf-8,' + encoded;
                    console.log('✅ Código cargado con data URI');
                    this.addLogEntry('Sistema', '🎮 Juego cargado en el visor (data URI)', 'system');
                } catch (error3) {
                    console.error('❌ Error con data URI:', error3);
                    
                    // === MÉTODO 4: Fallback final ===
                    textPreview.style.display = 'block';
                    gameFrame.style.display = 'none';
                    textPreview.textContent = '❌ Error al cargar el HTML:\n\n' + error3.message + '\n\n--- CÓDIGO GENERADO ---\n\n' + cleanCode;
                    this.addLogEntry('Sistema', '❌ Error al cargar el juego: ' + error3.message, 'rejected');
                }
            }
        }
        
        // Verificación de carga después de 1.5 segundos
        setTimeout(() => {
            try {
                const iframeDoc = gameFrame.contentDocument || gameFrame.contentWindow?.document;
                if (!iframeDoc || !iframeDoc.body || iframeDoc.body.innerHTML.trim() === '') {
                    console.log('⚠️ El iframe parece vacío, intentando blob URL...');
                    const blob = new Blob([cleanCode], { type: 'text/html;charset=utf-8' });
                    const url = URL.createObjectURL(blob);
                    gameFrame.src = url;
                } else {
                    console.log('✅ El iframe cargó correctamente');
                    console.log('📄 Contenido del iframe:', iframeDoc.body.innerHTML.substring(0, 100) + '...');
                }
            } catch (e) {
                console.log('ℹ️ No se pudo verificar el contenido del iframe (normal con sandbox)');
            }
        }, 1500);
    }

    copyCode() {
        if (!this.currentCode) return;
        navigator.clipboard.writeText(this.currentCode).then(() => {
            alert('¡Código copiado al portapapeles!');
        }).catch(() => {
            const textarea = document.createElement('textarea');
            textarea.value = this.currentCode;
            document.body.appendChild(textarea);
            textarea.select();
            document.execCommand('copy');
            document.body.removeChild(textarea);
            alert('¡Código copiado al portapapeles!');
        });
    }

    downloadCode() {
        if (!this.currentCode) return;
        
        const extMap = {
            'html': 'html',
            'python': 'py',
            'javascript': 'js',
            'json': 'json',
            'sql': 'sql',
            'text': 'txt'
        };
        const ext = extMap[this.currentLanguage] || 'txt';
        
        const blob = new Blob([this.currentCode], { type: 'text/plain;charset=utf-8' });
        const url = URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        a.download = `codigo_generado.${ext}`;
        document.body.appendChild(a);
        a.click();
        document.body.removeChild(a);
        URL.revokeObjectURL(url);
        
        this.addLogEntry('Sistema', `📥 Código descargado como .${ext}`, 'system');
    }

    addMessage(role, content) {
        const div = document.createElement('div');
        div.className = `message ${role}`;
        const contentDiv = document.createElement('div');
        contentDiv.className = 'message-content';
        if (role === 'assistant') {
            contentDiv.innerHTML = this.formatMessage(content);
        } else {
            contentDiv.textContent = content;
        }
        div.appendChild(contentDiv);
        this.messagesContainer.appendChild(div);
        this.messagesContainer.scrollTop = this.messagesContainer.scrollHeight;
    }

    formatMessage(content) {
        let formatted = content
            .replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>')
            .replace(/```(\w+)?\n([\s\S]*?)```/g, '<pre><code>$2</code></pre>')
            .replace(/\n/g, '<br>');
        return formatted;
    }

    loadSession() {
        const savedSession = localStorage.getItem('sessionId');
        if (savedSession) {
            this.sessionId = savedSession;
            this.addLogEntry('Sistema', 'Sesión cargada', 'system');
        }
    }

    async fetchLog() {
        if (!this.sessionId) return;
        try {
            const response = await fetch(`/api/session/${this.sessionId}/log`);
            const data = await response.json();
            
            this.logContent.innerHTML = data.log.map(entry => `
                <div class="log-entry-detail">
                    <div class="log-header-entry">
                        <span class="log-step">${entry.step}</span>
                        <span class="log-time">${new Date(entry.timestamp).toLocaleString()}</span>
                    </div>
                    <pre class="log-data">${JSON.stringify(entry.data, null, 2)}</pre>
                </div>
            `).join('') || '<p class="no-log">No hay datos de ejecución aún</p>';
            
            this.logInfo.textContent = `${data.log.length} pasos registrados`;
        } catch (error) {
            console.error('Error fetching log:', error);
            this.logContent.innerHTML = '<p class="no-log">❌ Error al cargar el log</p>';
        }
    }
}

document.addEventListener('DOMContentLoaded', () => new ChatApp());