from flask import Flask, request, redirect, url_for, flash, send_from_directory, jsonify
import os
from werkzeug.utils import secure_filename

app = Flask(__name__)
app.secret_key = 'minecraft_pe_cheats_secret_key'

# Конфигурация для загрузки файлов
UPLOAD_FOLDER = 'uploads'
ALLOWED_EXTENSIONS = {'txt', 'pdf', 'png', 'jpg', 'jpeg', 'gif', 'zip', 'rar', 'apk', 'mcpack', 'mcworld'}
MAX_FILE_SIZE = 16 * 1024 * 1024  # 16MB

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['MAX_CONTENT_LENGTH'] = MAX_FILE_SIZE

# Создаем папку для загрузок если её нет
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def get_base_html():
    return '''
<!DOCTYPE html>
<html lang="ru">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Minecraft PE Cheats</title>
    <style>
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }

        body {
            font-family: 'Courier New', monospace;
            background: linear-gradient(45deg, #1a1a2e, #16213e, #0f3460);
            background-size: 400% 400%;
            animation: gradientShift 15s ease infinite;
            color: #00ff00;
            min-height: 100vh;
            overflow-x: hidden;
        }

        @keyframes gradientShift {
            0% { background-position: 0% 50%; }
            50% { background-position: 100% 50%; }
            100% { background-position: 0% 50%; }
        }

        .container {
            max-width: 1200px;
            margin: 0 auto;
            padding: 20px;
            position: relative;
            z-index: 2;
        }

        .header {
            text-align: center;
            margin-bottom: 40px;
            padding: 20px;
            background: rgba(0, 0, 0, 0.7);
            border: 2px solid #00ff00;
            border-radius: 10px;
            box-shadow: 0 0 30px rgba(0, 255, 0, 0.3);
            position: relative;
            overflow: hidden;
        }

        .header::before {
            content: '';
            position: absolute;
            top: -2px;
            left: -2px;
            right: -2px;
            bottom: -2px;
            background: linear-gradient(45deg, #00ff00, #ff00ff, #00ffff, #ffff00);
            z-index: -1;
            border-radius: 10px;
            animation: borderGlow 3s linear infinite;
        }

        @keyframes borderGlow {
            0% { filter: hue-rotate(0deg); }
            100% { filter: hue-rotate(360deg); }
        }

        h1 {
            font-size: 2.5em;
            text-shadow: 0 0 20px #00ff00;
            margin-bottom: 10px;
            animation: textGlow 2s ease-in-out infinite alternate;
        }

        @keyframes textGlow {
            from { text-shadow: 0 0 20px #00ff00; }
            to { text-shadow: 0 0 30px #00ff00, 0 0 40px #00ff00; }
        }

        .subtitle {
            color: #ff00ff;
            font-size: 1.2em;
            text-shadow: 0 0 10px #ff00ff;
        }

        .nav {
            display: flex;
            justify-content: center;
            gap: 20px;
            margin-bottom: 30px;
        }

        .nav a {
            display: inline-block;
            padding: 12px 24px;
            background: linear-gradient(45deg, #ff0080, #8000ff);
            color: white;
            text-decoration: none;
            border-radius: 25px;
            font-weight: bold;
            text-transform: uppercase;
            transition: all 0.3s ease;
            border: 2px solid transparent;
            position: relative;
            overflow: hidden;
        }

        .nav a::before {
            content: '';
            position: absolute;
            top: 0;
            left: -100%;
            width: 100%;
            height: 100%;
            background: linear-gradient(90deg, transparent, rgba(255, 255, 255, 0.2), transparent);
            transition: left 0.5s;
        }

        .nav a:hover::before {
            left: 100%;
        }

        .nav a:hover {
            transform: translateY(-2px);
            box-shadow: 0 5px 15px rgba(255, 0, 128, 0.4);
            border-color: #00ff00;
        }

        .nav a.active {
            background: linear-gradient(45deg, #00ff00, #00ffff);
            color: #000;
        }

        .content {
            background: rgba(0, 0, 0, 0.8);
            border: 1px solid #00ff00;
            border-radius: 10px;
            padding: 30px;
            box-shadow: 0 0 20px rgba(0, 255, 0, 0.2);
            position: relative;
        }

        .flash-messages {
            margin-bottom: 20px;
        }

        .flash-message {
            padding: 12px;
            border-radius: 5px;
            margin-bottom: 10px;
            font-weight: bold;
        }

        .flash-message.success {
            background: rgba(0, 255, 0, 0.2);
            border: 1px solid #00ff00;
            color: #00ff00;
        }

        .flash-message.error {
            background: rgba(255, 0, 0, 0.2);
            border: 1px solid #ff0000;
            color: #ff0000;
        }

        /* Декоративные элементы */
        .matrix-bg {
            position: fixed;
            top: 0;
            left: 0;
            width: 100%;
            height: 100%;
            pointer-events: none;
            z-index: 1;
            opacity: 0.1;
        }

        .matrix-char {
            position: absolute;
            color: #00ff00;
            font-family: 'Courier New', monospace;
            animation: matrixFall linear infinite;
        }

        @keyframes matrixFall {
            0% {
                transform: translateY(-100vh);
                opacity: 1;
            }
            100% {
                transform: translateY(100vh);
                opacity: 0;
            }
        }

        @media (max-width: 768px) {
            .nav {
                flex-direction: column;
                align-items: center;
            }
            
            h1 {
                font-size: 2em;
            }
            
            .container {
                padding: 10px;
            }
        }

        .btn {
            display: inline-block;
            padding: 12px 24px;
            background: linear-gradient(45deg, #ff0080, #8000ff);
            color: white;
            text-decoration: none;
            border: none;
            border-radius: 25px;
            font-weight: bold;
            text-transform: uppercase;
            cursor: pointer;
            transition: all 0.3s ease;
            font-family: 'Courier New', monospace;
        }

        .btn:hover {
            transform: translateY(-2px);
            box-shadow: 0 5px 15px rgba(255, 0, 128, 0.4);
        }

        .btn-success {
            background: linear-gradient(45deg, #00ff00, #00ffff);
            color: #000;
        }

        .btn-danger {
            background: linear-gradient(45deg, #ff0000, #ff4444);
        }

        input[type="file"] {
            flex: 1;
            min-width: 200px;
            padding: 10px;
            background: rgba(0, 0, 0, 0.7);
            border: 1px solid #00ff00;
            border-radius: 5px;
            color: #00ff00;
            font-family: 'Courier New', monospace;
        }

        .file-item {
            display: flex;
            justify-content: space-between;
            align-items: center;
            padding: 15px;
            background: linear-gradient(45deg, rgba(255, 0, 128, 0.1), rgba(128, 0, 255, 0.1));
            border: 1px solid #ff0080;
            border-radius: 10px;
            transition: all 0.3s ease;
            margin-bottom: 15px;
        }

        .file-info {
            flex: 1;
        }

        .file-name {
            color: #00ffff;
            font-weight: bold;
            margin-bottom: 5px;
        }

        .file-size {
            color: #ffff00;
            font-size: 0.9em;
        }

        .file-actions {
            display: flex;
            gap: 10px;
        }
    </style>
</head>
<body>
    <div class="matrix-bg" id="matrixBg"></div>
    
    <div class="container">
        <div class="header">
            <h1>🎮 MINECRAFT PE CHEATS 🎮</h1>
            <div class="subtitle">Лучшие читы и моды для Minecraft Pocket Edition</div>
        </div>

        <nav class="nav">
            <a href="/" id="home-link">🏠 Главная</a>
            <a href="/files" id="files-link">📁 Файлы</a>
        </nav>

        <div class="content" id="main-content">
            <!-- Контент будет загружаться здесь -->
        </div>
    </div>

    <script>
        // Создаем эффект "Матрицы" на фоне
        function createMatrix() {
            const matrixBg = document.getElementById('matrixBg');
            const chars = '01アイウエオカキクケコサシスセソタチツテトナニヌネノハヒフヘホマミムメモヤユヨラリルレロワヲン';
            
            for (let i = 0; i < 50; i++) {
                const char = document.createElement('div');
                char.className = 'matrix-char';
                char.textContent = chars[Math.floor(Math.random() * chars.length)];
                char.style.left = Math.random() * 100 + 'vw';
                char.style.animationDuration = (Math.random() * 3 + 2) + 's';
                char.style.animationDelay = Math.random() * 2 + 's';
                char.style.fontSize = (Math.random() * 20 + 14) + 'px';
                matrixBg.appendChild(char);
            }
        }
        
        createMatrix();
        
        // Пересоздаем символы каждые 10 секунд
        setInterval(() => {
            document.getElementById('matrixBg').innerHTML = '';
            createMatrix();
        }, 10000);

        // Управление навигацией
        function setActiveLink(activeId) {
            document.querySelectorAll('.nav a').forEach(link => {
                link.classList.remove('active');
            });
            document.getElementById(activeId).classList.add('active');
        }

        // Загрузка контента
        function loadContent(page) {
            const content = document.getElementById('main-content');
            
            if (page === 'home') {
                setActiveLink('home-link');
                content.innerHTML = `
                    <div style="text-align: center;">
                        <h2 style="color: #ff00ff; margin-bottom: 30px; font-size: 2em; text-shadow: 0 0 15px #ff00ff;">
                            🚀 ДОБРО ПОЖАЛОВАТЬ В МИР ЧИТОВ! 🚀
                        </h2>
                        
                        <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(300px, 1fr)); gap: 20px; margin-top: 40px;">
                            <div style="background: linear-gradient(45deg, rgba(255, 0, 128, 0.2), rgba(128, 0, 255, 0.2)); padding: 25px; border-radius: 15px; border: 2px solid #ff0080;">
                                <h3 style="color: #00ffff; margin-bottom: 15px; font-size: 1.5em;">⚡ Скорость</h3>
                                <p>Передвигайтесь со скоростью молнии! Никто не сможет догнать вас в PvP сражениях.</p>
                                <div style="margin-top: 15px; padding: 10px; background: rgba(0, 255, 255, 0.1); border-radius: 5px;">
                                    <code style="color: #00ffff;">/effect @s speed 9999 255</code>
                                </div>
                            </div>
                            
                            <div style="background: linear-gradient(45deg, rgba(0, 255, 0, 0.2), rgba(0, 255, 255, 0.2)); padding: 25px; border-radius: 15px; border: 2px solid #00ff00;">
                                <h3 style="color: #ffff00; margin-bottom: 15px; font-size: 1.5em;">🔥 Полет</h3>
                                <p>Летайте как в креативе! Исследуйте мир с высоты птичьего полета.</p>
                                <div style="margin-top: 15px; padding: 10px; background: rgba(255, 255, 0, 0.1); border-radius: 5px;">
                                    <code style="color: #ffff00;">/gamemode creative</code>
                                </div>
                            </div>
                            
                            <div style="background: linear-gradient(45deg, rgba(255, 255, 0, 0.2), rgba(255, 0, 0, 0.2)); padding: 25px; border-radius: 15px; border: 2px solid #ffff00;">
                                <h3 style="color: #ff00ff; margin-bottom: 15px; font-size: 1.5em;">💎 Ресурсы</h3>
                                <p>Получите неограниченные ресурсы одной командой! Стройте без ограничений.</p>
                                <div style="margin-top: 15px; padding: 10px; background: rgba(255, 0, 255, 0.1); border-radius: 5px;">
                                    <code style="color: #ff00ff;">/give @s diamond 64</code>
                                </div>
                            </div>
                        </div>
                        
                        <div style="margin-top: 50px; padding: 30px; background: rgba(255, 0, 0, 0.1); border: 2px solid #ff0000; border-radius: 15px;">
                            <h3 style="color: #ff0000; margin-bottom: 20px; font-size: 1.8em;">⚠️ ВАЖНОЕ ПРЕДУПРЕЖДЕНИЕ ⚠️</h3>
                            <p style="font-size: 1.1em; line-height: 1.6;">
                                Использование читов может повлиять на ваш игровой опыт. Рекомендуется использовать только в одиночной игре 
                                или на серверах, где это разрешено. Помните о честной игре!
                            </p>
                        </div>
                        
                        <div style="margin-top: 40px; padding: 25px; background: linear-gradient(45deg, rgba(0, 255, 0, 0.1), rgba(0, 255, 255, 0.1)); border: 2px solid #00ff00; border-radius: 15px;">
                            <h3 style="color: #00ff00; margin-bottom: 20px; font-size: 1.6em;">📱 Поддерживаемые версии</h3>
                            <ul style="list-style: none; padding: 0;">
                                <li style="margin-bottom: 10px; color: #00ffff;">✅ Minecraft PE 1.19+</li>
                                <li style="margin-bottom: 10px; color: #00ffff;">✅ Minecraft Bedrock Edition</li>
                                <li style="margin-bottom: 10px; color: #00ffff;">✅ Windows 10 Edition</li>
                                <li style="margin-bottom: 10px; color: #00ffff;">✅ Xbox One Edition</li>
                            </ul>
                        </div>
                        
                        <div style="margin-top: 30px;">
                            <a href="/files" onclick="loadContent('files'); return false;" class="btn">
                                📁 Перейти к файлам →
                            </a>
                        </div>
                    </div>
                `;
            } else if (page === 'files') {
                setActiveLink('files-link');
                loadFilesPage();
            }
        }

        // Загрузка страницы файлов
        function loadFilesPage() {
            const content = document.getElementById('main-content');
            content.innerHTML = `
                <h2 style="color: #ff00ff; margin-bottom: 30px; text-align: center; font-size: 2em; text-shadow: 0 0 15px #ff00ff;">
                    📁 Файловый менеджер
                </h2>

                <div style="margin-bottom: 30px; padding: 25px; background: linear-gradient(45deg, rgba(0, 255, 0, 0.1), rgba(0, 255, 255, 0.1)); border: 2px solid #00ff00; border-radius: 15px;">
                    <h3 style="color: #00ff00; margin-bottom: 20px;">📤 Загрузить файл</h3>
                    <form method="POST" action="/upload" enctype="multipart/form-data" style="display: flex; gap: 15px; align-items: center; flex-wrap: wrap;">
                        <input type="file" name="file" required>
                        <button type="submit" class="btn">🚀 Загрузить</button>
                    </form>
                    <div style="margin-top: 15px; color: #ffff00; font-size: 0.9em;">
                        Поддерживаемые форматы: TXT, PDF, PNG, JPG, GIF, ZIP, RAR, APK, MCPACK, MCWORLD (макс. 16MB)
                    </div>
                </div>

                <div style="background: rgba(0, 0, 0, 0.7); border: 2px solid #ff00ff; border-radius: 15px; padding: 25px;">
                    <h3 style="color: #ff00ff; margin-bottom: 20px;">📋 Загруженные файлы</h3>
                    <div id="files-list">
                        <div style="text-align: center; padding: 20px;">
                            <div style="color: #ffff00;">Загрузка списка файлов...</div>
                        </div>
                    </div>
                </div>

                <div style="margin-top: 30px; padding: 20px; background: rgba(255, 255, 0, 0.1); border: 2px solid #ffff00; border-radius: 15px;">
                    <h4 style="color: #ffff00; margin-bottom: 15px;">💡 Советы по использованию:</h4>
                    <ul style="color: #00ff00; line-height: 1.8;">
                        <li>🎮 Загружайте APK файлы с читами для быстрой установки</li>
                        <li>🗺️ MCWORLD файлы - это готовые миры с читами</li>
                        <li>📦 MCPACK файлы содержат текстуры и поведения</li>
                        <li>📝 TXT файлы с командами и инструкциями</li>
                        <li>📸 Скриншоты и доказательства работы читов</li>
                    </ul>
                </div>
            `;
            
            // Загружаем список файлов
            loadFilesList();
        }

        // Загрузка списка файлов
        function loadFilesList() {
            fetch('/api/files')
                .then(response => response.json())
                .then(files => {
                    const filesList = document.getElementById('files-list');
                    
                    if (files.length === 0) {
                        filesList.innerHTML = `
                            <div style="text-align: center; padding: 40px; color: #888;">
                                <div style="font-size: 3em; margin-bottom: 15px;">📭</div>
                                <div style="font-size: 1.2em; color: #ffff00;">Файлы пока не загружены</div>
                                <div style="margin-top: 10px; color: #888;">Загрузите первый файл, используя форму выше</div>
                            </div>
                        `;
                    } else {
                        let filesHtml = '';
                        files.forEach(file => {
                            filesHtml += `
                                <div class="file-item">
                                    <div class="file-info">
                                        <div class="file-name">📄 ${file.name}</div>
                                        <div class="file-size">💾 Размер: ${file.size}</div>
                                    </div>
                                    <div class="file-actions">
                                        <a href="/download/${file.name}" class="btn btn-success">⬇️ Скачать</a>
                                        <a href="/delete/${file.name}" class="btn btn-danger" 
                                           onclick="return confirm('Вы уверены, что хотите удалить файл ${file.name}?')">
                                            🗑️ Удалить
                                        </a>
                                    </div>
                                </div>
                            `;
                        });
                        filesList.innerHTML = filesHtml;
                    }
                })
                .catch(error => {
                    console.error('Ошибка загрузки файлов:', error);
                    document.getElementById('files-list').innerHTML = `
                        <div style="text-align: center; padding: 20px; color: #ff0000;">
                            Ошибка загрузки файлов
                        </div>
                    `;
                });
        }

        // Обработка навигации
        document.getElementById('home-link').addEventListener('click', function(e) {
            e.preventDefault();
            loadContent('home');
            history.pushState(null, '', '/');
        });

        document.getElementById('files-link').addEventListener('click', function(e) {
            e.preventDefault();
            loadContent('files');
            history.pushState(null, '', '/files');
        });

        // Загрузка начального контента
        const path = window.location.pathname;
        if (path === '/files') {
            loadContent('files');
        } else {
            loadContent('home');
        }
    </script>
</body>
</html>
    '''

@app.route('/')
def index():
    return get_base_html()

@app.route('/files')
def files():
    return get_base_html()

@app.route('/api/files')
def api_files():
    # Получаем список загруженных файлов
    uploaded_files = []
    if os.path.exists(UPLOAD_FOLDER):
        for filename in os.listdir(UPLOAD_FOLDER):
            file_path = os.path.join(UPLOAD_FOLDER, filename)
            if os.path.isfile(file_path):
                file_size = os.path.getsize(file_path)
                uploaded_files.append({
                    'name': filename,
                    'size': f"{file_size / 1024:.1f} KB" if file_size < 1024*1024 else f"{file_size / (1024*1024):.1f} MB"
                })
    
    return jsonify(uploaded_files)

@app.route('/upload', methods=['POST'])
def upload_file():
    if 'file' not in request.files:
        flash('Файл не выбран', 'error')
        return redirect('/files')
    
    file = request.files['file']
    if file.filename == '':
        flash('Файл не выбран', 'error')
        return redirect('/files')
    
    if file and allowed_file(file.filename):
        filename = secure_filename(file.filename)
        file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
        flash(f'Файл {filename} успешно загружен!', 'success')
    else:
        flash('Неподдерживаемый тип файла', 'error')
    
    return redirect('/files')

@app.route('/download/<filename>')
def download_file(filename):
    return send_from_directory(app.config['UPLOAD_FOLDER'], filename, as_attachment=True)

@app.route('/delete/<filename>')
def delete_file(filename):
    try:
        file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        if os.path.exists(file_path):
            os.remove(file_path)
            flash(f'Файл {filename} удален', 'success')
        else:
            flash('Файл не найден', 'error')
    except Exception as e:
        flash('Ошибка при удалении файла', 'error')
    
    return redirect('/files')

if __name__ == '__main__':
    app.run(debug=True)
