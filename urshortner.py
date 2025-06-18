from flask import Flask, request, jsonify, render_template_string, redirect, abort
from urllib.parse import urlparse
import string
import random
import threading
import time
import json
import os

app = Flask(__name__)


DATA_FILE = "url_data.json"
LOCK = threading.Lock()


if os.path.exists(DATA_FILE):
    with open(DATA_FILE, "r") as f:
        try:
            url_store = json.load(f)
        except Exception:
            url_store = {}
else:
    url_store = {}


def save_data():
    with LOCK:
        with open(DATA_FILE, "w") as f:
            json.dump(url_store, f, indent=2)


def generate_short_code(length=6):
    chars = string.ascii_letters + string.digits
    while True:
        code = ''.join(random.choices(chars, k=length))
        if code not in url_store:
            return code

def is_valid_url(url):
    try:
        result = urlparse(url)
        return result.scheme in ("http", "https") and result.netloc != ""
    except:
        return False

@app.route('/')
def index():
    
    return render_template_string("""
<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8" />
<meta name="viewport" content="width=device-width, initial-scale=1" />
<title>Premium Modern URL Shortener</title>
<link href="https://fonts.googleapis.com/css2?family=Material+Icons" rel="stylesheet" />
<style>
  /* Reset & base */
  *, *::before, *::after {
    box-sizing: border-box;
  }
  body {
    margin: 0; padding: 0;
    font-family: 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Oxygen,
      Ubuntu, Cantarell, 'Open Sans', 'Helvetica Neue', sans-serif;
    background: linear-gradient(135deg, #6366f1, #06b6d4);
    color: #fff;
    min-height: 100vh;
    display: flex;
    flex-direction: column;
  }
  /* Scrollbar */
  ::-webkit-scrollbar {
    width: 10px;
  }
  ::-webkit-scrollbar-track {
    background: #222831;
  }
  ::-webkit-scrollbar-thumb {
    background: #6366f1;
    border-radius: 10px;
  }
  /* Header */
  header {
    height: 64px;
    backdrop-filter: blur(12px);
    background: rgba(36, 40, 47, 0.6);
    box-shadow: 0 2px 12px rgb(99 102 241 / 0.6);
    display: flex;
    align-items: center;
    padding: 0 24px;
    position: sticky;
    top: 0;
    z-index: 1000;
  }
  .brand {
    font-weight: 900;
    font-size: clamp(1.25rem, 2vw, 1.75rem);
    background: linear-gradient(135deg, #818cf8, #22d3ee);
    background-clip: text;
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    user-select: none;
  }
  /* Layout */
  .app-container {
    flex: 1;
    display: flex;
    min-height: calc(100vh - 64px);
    overflow: hidden;
  }
  /* Sidebar */
  aside.sidebar {
    width: 280px;
    background: rgba(18, 22, 28, 0.85);
    backdrop-filter: blur(16px);
    padding: 24px 16px;
    display: flex;
    flex-direction: column;
    gap: 24px;
    border-right: 1px solid rgba(99, 102, 241, 0.2);
  }
  aside.sidebar nav {
    display: flex;
    flex-direction: column;
    gap: 16px;
  }
  aside.sidebar nav button {
    background: transparent;
    border: none;
    display: flex;
    align-items: center;
    gap: 16px;
    padding: 12px 16px;
    font-size: 1rem;
    color: #a5b4fc;
    cursor: pointer;
    border-radius: 12px;
    transition: background-color 0.3s ease;
  }
  aside.sidebar nav button.active,
  aside.sidebar nav button:hover {
    background: rgba(99, 102, 241, 0.3);
    color: #6366f1;
  }
  .material-icons {
    font-size: 24px;
    vertical-align: middle;
  }
  /* Notification badge */
  .badge {
    background: #ef4444;
    color: white;
    font-size: 12px;
    font-weight: 700;
    border-radius: 9999px;
    padding: 2px 8px;
    display: inline-block;
    min-width: 20px;
    text-align: center;
  }
  /* Main content */
  main.content {
    flex: 1;
    display: flex;
    flex-direction: column;
    background: rgba(24, 28, 34, 0.9);
    padding: 32px 48px;
    overflow-y: auto;
  }
  /* Title */
  .content-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-bottom: 32px;
  }
  h1 {
    font-size: clamp(1.75rem, 3vw, 2.5rem);
    font-weight: 900;
    color: #818cf8;
  }
  /* URL form */
  form#url-form {
    display: flex;
    gap: 16px;
    margin-bottom: 32px;
    flex-wrap: wrap;
  }
  form#url-form input[type="url"] {
    flex: 1 1 320px;
    padding: 12px 16px;
    font-size: 1rem;
    border-radius: 12px;
    border: none;
    outline-offset: 2px;
    outline-color: #6366f1;
    background: #1f2937;
    color: #e0e7ff;
    transition: box-shadow 0.3s ease;
  }
  form#url-form input[type="url"]:focus {
    box-shadow: 0 0 8px 2px #818cf8;
  }
  form#url-form button {
    padding: 12px 28px;
    font-size: 1rem;
    font-weight: 700;
    color: white;
    border-radius: 12px;
    border: none;
    cursor: pointer;
    background: linear-gradient(135deg, #6366f1, #22d3ee);
    transition: background 0.4s ease;
  }
  form#url-form button:hover,
  form#url-form button:focus {
    background: linear-gradient(135deg, #818cf8, #67e8f9);
  }
  /* Validation error */
  .error-message {
    color: #f87171;
    font-size: 0.85rem;
    margin-top: 4px;
  }
  /* URL list container */
  .url-list {
    flex: 1;
    overflow-y: auto;
    min-height: 200px;
  }
  /* URL card */
  .url-card {
    background: rgba(99, 102, 241, 0.1);
    border-radius: 16px;
    padding: 24px 32px;
    margin-bottom: 24px;
    box-shadow: 0 10px 20px rgb(99 102 241 / 0.1);
    display: flex;
    flex-direction: column;
    gap: 12px;
    position: relative;
  }
  .url-card:hover {
    box-shadow: 0 10px 30px rgb(99 102 241 / 0.35);
  }
  .url-row {
    display: flex;
    justify-content: space-between;
    flex-wrap: wrap;
    gap: 8px;
  }
  .url-original,
  .url-short {
    font-weight: 600;
    font-size: 1rem;
    word-break: break-all;
    color: #dbeafe;
  }
  .url-short a {
    color: #a5b4fc;
    text-decoration: none;
    transition: color 0.3s ease;
  }
  .url-short a:hover,
  .url-short a:focus {
    color: #818cf8;
  }
  /* Buttons container */
  .btn-group {
    display: flex;
    gap: 16px;
  }
  button.btn {
    background: transparent;
    border: none;
    cursor: pointer;
    color: #c7d2fe;
    font-size: 20px;
    padding: 6px;
    border-radius: 8px;
    transition: background-color 0.3s ease, color 0.3s ease;
  }
  button.btn:hover,
  button.btn:focus {
    background-color: rgba(131, 102, 241, 0.3);
    color: #818cf8;
    outline: none;
  }
  /* Footer */
  footer {
    height: auto;
    min-height: 64px;
    background: rgba(36, 40, 47, 0.8);
    backdrop-filter: blur(12px);
    box-shadow: 0 -2px 12px rgb(99 102 241 / 0.6);
    display: flex;
    justify-content: center;
    align-items: center;
    padding: 12px 24px;
    color: #a5b4fc;
    font-size: 0.9rem;
    user-select: none;
  }
  footer a {
    color: #818cf8;
    text-decoration: none;
    margin-left: 6px;
  }
  footer a:hover,
  footer a:focus {
    text-decoration: underline;
  }
  /* Toast notification */
  #toast {
    position: fixed;
    bottom: 24px;
    left: 50%;
    transform: translateX(-50%);
    background: #6366f1;
    color: white;
    padding: 14px 28px;
    border-radius: 24px;
    box-shadow: 0 10px 20px rgb(99 102 241 / 0.5);
    opacity: 0;
    pointer-events: none;
    user-select: none;
    transition: opacity 0.3s ease;
    z-index: 1500;
    font-weight: 600;
    min-width: 280px;
    text-align: center;
  }
  #toast.show {
    opacity: 1;
    pointer-events: all;
  }
  /* Responsive - Mobile */
  @media (max-width: 767px) {
    aside.sidebar {
      position: fixed;
      top: 64px;
      left: 0;
      bottom: 0;
      width: 280px;
      background: rgba(18, 22, 28, 0.95);
      transform: translateX(-100%);
      transition: transform 0.3s ease-in-out;
      z-index: 1100;
      padding-top: 24px;
      box-shadow: 2px 0 6px rgba(0,0,0,0.6);
      border-right: none;
    }
    aside.sidebar.open {
      transform: translateX(0);
    }
    .mobile-menu-btn {
      background: transparent;
      border: none;
      color: #a5b4fc;
      font-size: 28px;
      cursor: pointer;
      margin-right: 12px;
    }
    .app-container {
      flex-direction: column;
    }
    main.content {
      padding: 24px 16px;
      height: calc(100vh - 64px);
      overflow-y: auto;
    }
    form#url-form {
      flex-direction: column;
      gap: 12px;
    }
    form#url-form input[type="url"] {
      width: 100%;
    }
    /* Header flex adjustments */
    header {
      justify-content: space-between;
      padding: 0 16px;
    }
    .brand {
      user-select: text;
    }
  }
</style>
</head>
<body>
<header>
  <button class="mobile-menu-btn material-icons" aria-label="Toggle menu" aria-expanded="false" aria-controls="sidebar">menu</button>
  <div class="brand" tabindex="0" aria-label="URL Shortener Brand">Shortly</div>
</header>
<div class="app-container">
<aside id="sidebar" class="sidebar" role="navigation" aria-label="Main Navigation">
  <nav>
    <button id="nav-home" class="active" aria-current="page">
      <span class="material-icons" aria-hidden="true">home</span>
      Home
    </button>
    <button id="nav-archive" aria-current="false">
      <span class="material-icons" aria-hidden="true">archive</span>
      Archive
      <span id="badge-archive" class="badge" hidden>0</span>
    </button>
    <button id="nav-settings" aria-current="false">
      <span class="material-icons" aria-hidden="true">settings</span>
      Settings
    </button>
  </nav>
</aside>
<main role="main" class="content" tabindex="-1">
  <div class="content-header">
    <h1 id="view-title">Create Short URL</h1>
  </div>
  <section id="view-home" aria-live="polite">
    <form id="url-form" novalidate>
      <input type="url" id="input-url" name="url" placeholder="Enter your URL to shorten" aria-label="Enter URL" autocomplete="url" required />
      <button type="submit" aria-label="Shorten URL">Shorten</button>
      <span id="input-error" class="error-message" role="alert" aria-live="assertive"></span>
    </form>
    <div class="url-list" id="url-list" aria-live="polite" aria-relevant="additions removals"></div>
  </section>
  <section id="view-archive" hidden aria-live="polite">
    <h2>Archived URLs</h2>
    <div class="url-list" id="archive-list"></div>
  </section>
  <section id="view-settings" hidden aria-live="polite">
    <h2>Settings</h2>
    <form id="settings-form" novalidate>
      <fieldset>
        <legend>Theme Selection</legend>
        <label>
          <input type="radio" name="theme" value="light" /> Light
        </label>
        <label>
          <input type="radio" name="theme" value="dark" /> Dark
        </label>
      </fieldset>
    </form>
  </section>
</main>
</div>
<footer>
  Made with &lt;3 by Your Company. <a href="#" target="_blank" rel="noopener">Privacy Policy</a> | <a href="#" target="_blank" rel="noopener">Terms of Service</a>
</footer>
<div id="toast" role="alert" aria-live="assertive" aria-atomic="true"></div>
<script>
  (() => {
    // DOM elements
    const urlForm = document.getElementById('url-form');
    const urlInput = document.getElementById('input-url');
    const errorSpan = document.getElementById('input-error');
    const urlListEl = document.getElementById('url-list');
    const archiveListEl = document.getElementById('archive-list');
    const toastEl = document.getElementById('toast');
    const sidebar = document.getElementById('sidebar');
    const mobileMenuBtn = document.querySelector('.mobile-menu-btn');
    const navButtons = document.querySelectorAll('aside.sidebar nav button');
    const viewHome = document.getElementById('view-home');
    const viewArchive = document.getElementById('view-archive');
    const viewSettings = document.getElementById('view-settings');
    const viewTitle = document.getElementById('view-title');
    const settingsForm = document.getElementById('settings-form');

    // Storage keys
    const STORAGE_KEY = 'shortly_urls';
    const PREFS_KEY = 'shortly_preferences';

    // State and history for undo/redo
    let urlData = [];
    let archivedData = [];
    let undoStack = [];
    let redoStack = [];

    // Current nav state
    let currentView = 'home'; // 'home', 'archive', 'settings'

    // Accessibility helpers
    function focusMainContent() {
      document.querySelector('main.content').focus();
    }

    // Toast notification
    function showToast(message, duration = 3000) {
      toastEl.textContent = message;
      toastEl.classList.add('show');
      setTimeout(() => {
        toastEl.classList.remove('show');
      }, duration);
    }

    // Load URLs from localStorage
    function loadUrls() {
      try {
        const stored = localStorage.getItem(STORAGE_KEY);
        if(stored) {
          const parsed = JSON.parse(stored);
          if(Array.isArray(parsed.urls)) {
            urlData = parsed.urls.filter(item => !item.archived);
            archivedData = parsed.urls.filter(item => item.archived);
          } else {
            urlData = [];
            archivedData = [];
          }
        }
      } catch(e) {
        urlData = [];
        archivedData = [];
      }
    }

    // Save URLs to localStorage
    function saveUrls() {
      const all = [...urlData, ...archivedData];
      localStorage.setItem(STORAGE_KEY, JSON.stringify({urls: all}));
    }

    // Load preferences
    function loadPreferences() {
      try {
        const prefsRaw = localStorage.getItem(PREFS_KEY);
        let prefs = prefsRaw ? JSON.parse(prefsRaw) : {};
        return prefs;
      } catch {
        return {};
      }
    }

    // Save preferences
    function savePreferences(prefs) {
      localStorage.setItem(PREFS_KEY, JSON.stringify(prefs));
    }

    // Theme switching
    function applyTheme(theme) {
      if (theme === 'dark') {
        document.body.style.background = 'linear-gradient(135deg, #060606, #1b1b1b)';
        document.body.style.color = '#e0e7ff';
      } else {
        document.body.style.background = 'linear-gradient(135deg, #6366f1, #06b6d4)';
        document.body.style.color = '#fff';
      }
    }

    // Generate short code helper
    function generateShortCode(length = 6) {
      const chars = 'abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789';
      let result = '';
      for(let i=0; i<length; i++) {
        result += chars.charAt(Math.floor(Math.random() * chars.length));
      }
      return result;
    }

    // Validate URL format
    function validateUrl(url) {
      try {
        const parsed = new URL(url);
        return ['http:', 'https:'].includes(parsed.protocol);
      } catch {
        return false;
      }
    }

    // Render URL list
    function renderUrlList() {
      urlListEl.innerHTML = '';
      if(urlData.length === 0) {
        urlListEl.textContent = 'No URLs shortened yet.';
        return;
      }
      urlData.forEach(urlObj => {
        const card = document.createElement('article');
        card.className = 'url-card';
        card.setAttribute('tabindex', '0');
        card.setAttribute('aria-label', `Shortened URL card for ${urlObj.originalUrl}`);

        const original = document.createElement('div');
        original.className = 'url-original';
        original.textContent = urlObj.originalUrl;

        const shortUrl = document.createElement('div');
        shortUrl.className = 'url-short';
        const a = document.createElement('a');
        a.href = urlObj.shortUrl;
        a.target = '_blank';
        a.rel = 'noopener noreferrer';
        a.textContent = urlObj.shortUrl;
        a.setAttribute('aria-label', `Short URL link: ${urlObj.shortUrl}`);
        shortUrl.appendChild(a);

        const btnGroup = document.createElement('div');
        btnGroup.className = 'btn-group';

        // Copy button
        const btnCopy = document.createElement('button');
        btnCopy.className = 'btn';
        btnCopy.title = 'Copy short URL';
        btnCopy.setAttribute('aria-label', 'Copy short URL');
        btnCopy.innerHTML = '<span class="material-icons" aria-hidden="true">content_copy</span>';
        btnCopy.addEventListener('click', () => {
          navigator.clipboard.writeText(urlObj.shortUrl)
          .then(() => showToast('Copied to clipboard!'))
          .catch(() => showToast('Failed to copy', 3500));
        });

        // Archive button
        const btnArchive = document.createElement('button');
        btnArchive.className = 'btn';
        btnArchive.title = 'Archive this URL';
        btnArchive.setAttribute('aria-label', 'Archive URL');
        btnArchive.innerHTML = '<span class="material-icons" aria-hidden="true">archive</span>';
        btnArchive.addEventListener('click', () => {
          archiveUrl(urlObj.id);
        });

        // Delete button
        const btnDelete = document.createElement('button');
        btnDelete.className = 'btn';
        btnDelete.title = 'Delete this URL';
        btnDelete.setAttribute('aria-label', 'Delete URL');
        btnDelete.innerHTML = '<span class="material-icons" aria-hidden="true">delete</span>';
        btnDelete.addEventListener('click', () => {
          deleteUrl(urlObj.id);
        });

        btnGroup.appendChild(btnCopy);
        btnGroup.appendChild(btnArchive);
        btnGroup.appendChild(btnDelete);

        card.appendChild(original);
        card.appendChild(shortUrl);
        card.appendChild(btnGroup);

        urlListEl.appendChild(card);
      });
      document.getElementById('badge-archive').textContent = archivedData.length;
      document.getElementById('badge-archive').hidden = archivedData.length === 0;
    }

    // Render archive list
    function renderArchiveList() {
      archiveListEl.innerHTML = '';
      if(archivedData.length === 0) {
        archiveListEl.textContent = 'No archived URLs.';
        return;
      }
      archivedData.forEach(urlObj => {
        const card = document.createElement('article');
        card.className = 'url-card';
        card.setAttribute('tabindex', '0');
        card.setAttribute('aria-label', `Archived URL card for ${urlObj.originalUrl}`);

        const original = document.createElement('div');
        original.className = 'url-original';
        original.textContent = urlObj.originalUrl;

        const shortUrl = document.createElement('div');
        shortUrl.className = 'url-short';
        const a = document.createElement('a');
        a.href = urlObj.shortUrl;
        a.target = '_blank';
        a.rel = 'noopener noreferrer';
        a.textContent = urlObj.shortUrl;
        a.setAttribute('aria-label', `Short URL link: ${urlObj.shortUrl}`);
        shortUrl.appendChild(a);

        const btnGroup = document.createElement('div');
        btnGroup.className = 'btn-group';

        // Restore button
        const btnRestore = document.createElement('button');
        btnRestore.className = 'btn';
        btnRestore.title = 'Restore this URL';
        btnRestore.setAttribute('aria-label', 'Restore URL');
        btnRestore.innerHTML = '<span class="material-icons" aria-hidden="true">unarchive</span>';
        btnRestore.addEventListener('click', () => {
          restoreUrl(urlObj.id);
        });

        // Delete button
        const btnDelete = document.createElement('button');
        btnDelete.className = 'btn';
        btnDelete.title = 'Delete this URL';
        btnDelete.setAttribute('aria-label', 'Delete URL');
        btnDelete.innerHTML = '<span class="material-icons" aria-hidden="true">delete</span>';
        btnDelete.addEventListener('click', () => {
          deleteUrl(urlObj.id);
        });

        btnGroup.appendChild(btnRestore);
        btnGroup.appendChild(btnDelete);

        card.appendChild(original);
        card.appendChild(shortUrl);
        card.appendChild(btnGroup);

        archiveListEl.appendChild(card);
      });
      document.getElementById('badge-archive').textContent = archivedData.length;
      document.getElementById('badge-archive').hidden = archivedData.length === 0;
    }

    // Create a new short URL entry
    function createUrl(originalUrl) {
      // Check for existing
      const existing = urlData.find(u => u.originalUrl === originalUrl);
      if(existing) {
        showToast('URL already shortened');
        return;
      }
      // Generate unique short code
      let shortCode;
      do {
        shortCode = generateShortCode();
      } while(urlData.find(u => u.shortCode === shortCode) || archivedData.find(u => u.shortCode === shortCode));

      const shortUrl = `${window.location.origin}/${shortCode}`;
      const id = crypto.randomUUID ? crypto.randomUUID() : Math.random().toString(36).substr(2,9);

      const entry = {
        id,
        originalUrl,
        shortCode,
        shortUrl,
        createdAt: new Date().toISOString(),
        archived: false
      };
      undoStack.push({action: 'create', entry});
      redoStack.length = 0;
      urlData.unshift(entry);
      saveUrls();
      renderUrlList();
      showToast('URL shortened successfully');
    }

    // Delete URL by id
    function deleteUrl(id) {
      const idx = urlData.findIndex(item => item.id === id);
      if(idx >= 0) {
        undoStack.push({action: 'delete', entry: urlData[idx]});
        redoStack.length = 0;
        urlData.splice(idx, 1);
        saveUrls();
        renderUrlList();
        showToast('URL deleted');
        return;
      }
      const arIdx = archivedData.findIndex(item => item.id === id);
      if(arIdx >= 0) {
        undoStack.push({action: 'delete', entry: archivedData[arIdx]});
        redoStack.length = 0;
        archivedData.splice(arIdx, 1);
        saveUrls();
        renderArchiveList();
        showToast('Archived URL deleted');
      }
    }

    // Archive URL by id
    function archiveUrl(id) {
      const idx = urlData.findIndex(item => item.id === id);
      if(idx >= 0) {
        const item = urlData.splice(idx, 1)[0];
        item.archived = true;
        archivedData.unshift(item);
        undoStack.push({action: 'archive', entry: item});
        redoStack.length = 0;
        saveUrls();
        renderUrlList();
        renderArchiveList();
        showToast('URL archived');
      }
    }

    // Restore archived URL by id
    function restoreUrl(id) {
      const idx = archivedData.findIndex(item => item.id === id);
      if(idx >= 0) {
        const item = archivedData.splice(idx, 1)[0];
        item.archived = false;
        urlData.unshift(item);
        undoStack.push({action: 'restore', entry: item});
        redoStack.length = 0;
        saveUrls();
        renderUrlList();
        renderArchiveList();
        showToast('URL restored');
      }
    }

    // Undo last action
    function undo() {
      if(undoStack.length === 0) {
        showToast('Nothing to undo');
        return;
      }
      const action = undoStack.pop();
      redoStack.push(action);
      switch(action.action) {
        case 'create':
          // Remove created entry
          urlData = urlData.filter(e => e.id !== action.entry.id);
          saveUrls();
          renderUrlList();
          showToast('Undo: URL creation reverted');
          break;
        case 'delete':
          // Re-add deleted entry
          if(action.entry.archived) {
            archivedData.unshift(action.entry);
            renderArchiveList();
          } else {
            urlData.unshift(action.entry);
            renderUrlList();
          }
          saveUrls();
          showToast('Undo: URL deletion reverted');
          break;
        case 'archive':
          // Move back from archive to active
          archivedData = archivedData.filter(e => e.id !== action.entry.id);
          action.entry.archived = false;
          urlData.unshift(action.entry);
          saveUrls();
          renderUrlList();
          renderArchiveList();
          showToast('Undo: URL archive reverted');
          break;
        case 'restore':
          // Move back from active to archive
          urlData = urlData.filter(e => e.id !== action.entry.id);
          action.entry.archived = true;
          archivedData.unshift(action.entry);
          saveUrls();
          renderUrlList();
          renderArchiveList();
          showToast('Undo: URL restore reverted');
          break;
      }
    }

    // Redo last undone action
    function redo() {
      if(redoStack.length === 0) {
        showToast('Nothing to redo');
        return;
      }
      const action = redoStack.pop();
      undoStack.push(action);
      switch(action.action) {
        case 'create':
          urlData.unshift(action.entry);
          saveUrls();
          renderUrlList();
          showToast('Redo: URL creation reapplied');
          break;
        case 'delete':
          if(action.entry.archived) {
            archivedData = archivedData.filter(e => e.id !== action.entry.id);
            renderArchiveList();
          } else {
            urlData = urlData.filter(e => e.id !== action.entry.id);
            renderUrlList();
          }
          saveUrls();
          showToast('Redo: URL deletion reapplied');
          break;
        case 'archive':
          urlData = urlData.filter(e => e.id !== action.entry.id);
          action.entry.archived = true;
          archivedData.unshift(action.entry);
          saveUrls();
          renderUrlList();
          renderArchiveList();
          showToast('Redo: URL archive reapplied');
          break;
        case 'restore':
          archivedData = archivedData.filter(e => e.id !== action.entry.id);
          action.entry.archived = false;
          urlData.unshift(action.entry);
          saveUrls();
          renderUrlList();
          renderArchiveList();
          showToast('Redo: URL restore reapplied');
          break;
      }
    }

    // Navigation switch
    function setView(view) {
      if(view === currentView) return;
      currentView = view;
      navButtons.forEach(btn => {
        btn.classList.remove('active');
        if(btn.id === 'nav-' + view) {
          btn.classList.add('active');
          btn.setAttribute('aria-current', 'page');
        } else {
          btn.setAttribute('aria-current', 'false');
        }
      });
      // Show correct view and update title
      viewHome.hidden = view !== 'home';
      viewArchive.hidden = view !== 'archive';
      viewSettings.hidden = view !== 'settings';
      viewTitle.textContent = {
        home: 'Create Short URL',
        archive: 'Archived URLs',
        settings: 'Settings'
      }[view];
      focusMainContent();
    }

    // Form submit handler
    urlForm.addEventListener('submit', e => {
      e.preventDefault();
      const urlVal = urlInput.value.trim();
      errorSpan.textContent = '';
      if(!urlVal) {
        errorSpan.textContent = 'URL is required';
        urlInput.focus();
        return;
      }
      if(!validateUrl(urlVal)) {
        errorSpan.textContent = 'Invalid URL format';
        urlInput.focus();
        return;
      }
      createUrl(urlVal);
      urlInput.value = '';
      urlInput.focus();
    });

    // Navigation buttons events
    navButtons.forEach(btn => {
      btn.addEventListener('click', () => {
        const id = btn.id.replace('nav-', '');
        setView(id);
      });
    });

    // Mobile menu toggle
    mobileMenuBtn.addEventListener('click', () => {
      if(sidebar.classList.contains('open')) {
        sidebar.classList.remove('open');
        mobileMenuBtn.setAttribute('aria-expanded', 'false');
      } else {
        sidebar.classList.add('open');
        mobileMenuBtn.setAttribute('aria-expanded', 'true');
      }
    });

    // Theme settings form
    settingsForm.addEventListener('change', e => {
      if(e.target.name === 'theme') {
        applyTheme(e.target.value);
        const prefs = loadPreferences();
        prefs.theme = e.target.value;
        savePreferences(prefs);
      }
    });

    // Keyboard shortcuts: Ctrl+Z Undo, Ctrl+Y Redo
    window.addEventListener('keydown', (e) => {
      if((e.ctrlKey || e.metaKey) && !e.shiftKey && e.key.toLowerCase() === 'z') {
        e.preventDefault();
        undo();
      } else if((e.ctrlKey || e.metaKey) && e.key.toLowerCase() === 'y') {
        e.preventDefault();
        redo();
      }
    });

    // Init app
    function init() {
      loadUrls();
      renderUrlList();
      renderArchiveList();
      const prefs = loadPreferences();
      if(prefs.theme === 'dark') {
        applyTheme('dark');
        settingsForm.theme.value = 'dark';
      } else {
        applyTheme('light');
        settingsForm.theme.value = 'light';
      }
    }
    init();
  })();
</script>
</body>
</html>
    """)


@app.route('/<short_code>')
def redirect_to_url(short_code):
    # Redirect to original URL if exists
    url_obj = url_store.get(short_code)
    if url_obj and not url_obj.get("archived", False):
        return redirect(url_obj["originalUrl"], code=302)
    else:
        abort(404)


@app.route('/api/urls', methods=['GET', 'POST', 'PUT', 'DELETE'])
def api_urls():
    global url_store
    data = request.json
    if request.method == 'GET':
        
        all_urls = [dict(shortCode=k, **v) for k, v in url_store.items() if not v.get('archived', False)]
        return jsonify(urls=all_urls)

    elif request.method == 'POST':
        
        orig_url = data.get('originalUrl', '')
        if not orig_url or not is_valid_url(orig_url):
            return jsonify(error='Invalid URL'), 400
        # Check if already shortened
        for short_code, details in url_store.items():
            if details['originalUrl'] == orig_url and not details.get('archived', False):
                return jsonify(shortCode=short_code, url=details), 200
        short_code = generate_short_code()
        url_store[short_code] = {
            "originalUrl": orig_url,
            "createdAt": time.time(),
            "archived": False
        }
        save_data()
        return jsonify(shortCode=short_code, url=url_store[short_code]), 201

    elif request.method == 'PUT':
        short_code = data.get('shortCode')
        if not short_code or short_code not in url_store:
            return jsonify(error='Short code not found'), 404
        # Update entry fields (allow archiving)
        fields = ['originalUrl', 'archived']
        updated = False
        for f in fields:
            if f in data:
                url_store[short_code][f] = data[f]
                updated = True
        if updated:
            save_data()
            return jsonify(success=True)
        return jsonify(error='No valid fields provided'), 400

    elif request.method == 'DELETE':
        short_code = data.get('shortCode')
        if not short_code or short_code not in url_store:
            return jsonify(error='Short code not found'), 404
        del url_store[short_code]
        save_data()
        return jsonify(success=True)


if __name__ == '__main__':
    app.run(debug=True, port=5000)



