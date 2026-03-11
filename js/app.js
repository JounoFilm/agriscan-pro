// ============================================
// AgriScan Pro - Main Application Logic
// ============================================

document.addEventListener('DOMContentLoaded', () => {
  initNavigation();
  initMobileMenu();
  initHeaderDate();
  
  // Page-specific init
  const page = document.body.dataset.page;
  if (page === 'dashboard') initDashboard();
  if (page === 'upload') initUpload();
  if (page === 'report') initReport();
  if (page === 'fields') initFields();
});

// === Navigation ===
function initNavigation() {
  const currentPage = window.location.pathname.split('/').pop() || 'index.html';
  document.querySelectorAll('.nav-item').forEach(item => {
    const href = item.getAttribute('href');
    if (href === currentPage || (currentPage === '' && href === 'index.html')) {
      item.classList.add('active');
    }
  });
}

// === Mobile Menu ===
function initMobileMenu() {
  const btn = document.querySelector('.mobile-menu-btn');
  const sidebar = document.querySelector('.sidebar');
  if (btn && sidebar) {
    btn.addEventListener('click', () => {
      sidebar.classList.toggle('open');
    });
    document.addEventListener('click', (e) => {
      if (!sidebar.contains(e.target) && !btn.contains(e.target)) {
        sidebar.classList.remove('open');
      }
    });
  }
}

// === Header Date ===
function initHeaderDate() {
  const el = document.querySelector('.header-date');
  if (el) {
    const now = new Date();
    const opts = { year: 'numeric', month: 'long', day: 'numeric', weekday: 'short' };
    el.textContent = now.toLocaleDateString('ja-JP', opts);
  }
}

// === Dashboard ===
function initDashboard() {
  animateScoreRing();
  renderAlerts();
  renderFieldList();
  renderModuleOverview();
  renderNextActions();
  renderStats();
}

function animateScoreRing() {
  const ring = document.querySelector('.ring-fill');
  const scoreNum = document.querySelector('.score-number');
  if (!ring || !scoreNum) return;

  const score = DEMO_DATA.overallScore.score;
  const circumference = 2 * Math.PI * 90;
  const offset = circumference - (score / 100) * circumference;

  setTimeout(() => {
    ring.style.strokeDashoffset = offset;
  }, 300);

  // Animate number
  let current = 0;
  const step = score / 40;
  const interval = setInterval(() => {
    current += step;
    if (current >= score) {
      current = score;
      clearInterval(interval);
    }
    scoreNum.textContent = Math.round(current);
  }, 30);
}

function renderStats() {
  const container = document.querySelector('.stats-grid');
  if (!container) return;

  const totalFields = DEMO_DATA.fields.length;
  const totalArea = DEMO_DATA.fields.reduce((sum, f) => sum + f.area_ha, 0);
  const urgentAlerts = DEMO_DATA.alerts.filter(a => a.type === 'urgent').length;
  const totalSprays = DEMO_DATA.sprayRecords.length;

  const stats = [
    { icon: '🌾', label: '管理圃場数', value: totalFields + '圃場', color: 'green', trend: null },
    { icon: '📐', label: '総管理面積', value: totalArea.toFixed(1) + 'ha', color: 'blue', trend: null },
    { icon: '🚨', label: '緊急アラート', value: urgentAlerts + '件', color: 'red', trend: null },
    { icon: '🚁', label: '散布実績（今月）', value: totalSprays + '回', color: 'cyan', trend: null }
  ];

  container.innerHTML = stats.map((s, i) => `
    <div class="stat-card animate-slide-up stagger-${i + 1}">
      <div class="stat-icon ${s.color}">${s.icon}</div>
      <div class="stat-value">${s.value}</div>
      <div class="stat-label">${s.label}</div>
    </div>
  `).join('');
}

function renderAlerts() {
  const container = document.querySelector('.alert-list');
  if (!container) return;

  container.innerHTML = DEMO_DATA.alerts.map(alert => `
    <div class="alert-item ${alert.type}">
      <div class="alert-icon ${alert.type}">
        ${alert.type === 'urgent' ? '🚨' : alert.type === 'warning' ? '⚠️' : 'ℹ️'}
      </div>
      <div class="alert-content">
        <div class="alert-title">${alert.title}</div>
        <div class="alert-desc">${alert.description}</div>
        <div class="alert-meta">
          <span class="alert-tag ${alert.type}">${alert.type === 'urgent' ? '緊急' : alert.type === 'warning' ? '注意' : '情報'}</span>
          <span>📍 ${alert.module}</span>
          <span>🕐 ${alert.timestamp}</span>
        </div>
      </div>
    </div>
  `).join('');
}

function renderFieldList() {
  const container = document.querySelector('.dashboard-fields');
  if (!container) return;

  container.innerHTML = `
    <table class="data-table">
      <thead>
        <tr>
          <th>圃場名</th>
          <th>品種</th>
          <th>面積</th>
          <th>生育ステージ</th>
          <th>健康スコア</th>
          <th>状態</th>
        </tr>
      </thead>
      <tbody>
        ${DEMO_DATA.fields.map(f => `
          <tr>
            <td>
              <div class="fw-600">${f.name}</div>
              <div class="text-muted" style="font-size:11px">${f.farmer}</div>
            </td>
            <td>${f.variety}</td>
            <td>${f.area_ha}ha</td>
            <td>${f.stage}</td>
            <td>
              <div class="flex items-center gap-sm">
                <div class="severity-bar" style="width:60px">
                  <div class="fill ${f.health_score >= 80 ? 'green' : f.health_score >= 50 ? 'amber' : 'red'}" 
                       style="width:${f.health_score}%"></div>
                </div>
                <span class="fw-600">${f.health_score}</span>
              </div>
            </td>
            <td>
              <span class="badge badge-${f.status === 'good' ? 'success' : f.status === 'caution' ? 'warning' : f.status === 'action' ? 'danger' : 'danger'}">
                ${f.status === 'good' ? '良好' : f.status === 'caution' ? '注意' : f.status === 'action' ? '要対処' : '緊急'}
              </span>
            </td>
          </tr>
        `).join('')}
      </tbody>
    </table>
  `;
}

function renderModuleOverview() {
  const container = document.querySelector('.module-grid');
  if (!container) return;

  const modules = [
    { key: 'disease', icon: '🔬', title: '生育状態・病害虫診断', desc: 'AI画像解析による病害虫の自動検出。いもち病、ウンカ類、カメムシ類等を特定。', link: 'report.html', colorClass: 'disease' },
    { key: 'weed', icon: '🌿', title: '雑草密度マップ', desc: '圃場全体の雑草被覆度をヒートマップで可視化。ノビエ、コナギ等を自動判別。', link: 'report.html', colorClass: 'weed' },
    { key: 'infra', icon: '🏗️', title: '畦畔・水路チェック', desc: '畦畔の崩れ、水路の詰まり、獣害痕等のインフラ異常を検出。', link: 'report.html', colorClass: 'infra' },
    { key: 'spray', icon: '✈️', title: '散布実績レポート', desc: 'T70Pのフライトログから散布軌跡・散布量を自動記録。スマート農業加算の証拠レポート。', link: 'report.html', colorClass: 'spray' },
    { key: 'health', icon: '📊', title: '総合圃場健康スコア', desc: '5つの指標から総合的な圃場の健康度を0-100で自動評価。データの蓄積で予測精度向上。', link: 'report.html', colorClass: 'health' }
  ];

  const moduleData = DEMO_DATA.overallScore.modules;

  container.innerHTML = modules.map(m => {
    const data = moduleData[m.key];
    return `
      <a href="${m.link}" class="module-card ${m.colorClass}">
        <div class="module-icon">${m.icon}</div>
        <div class="module-title">${m.title}</div>
        <div class="module-desc">${m.desc}</div>
        <div class="module-status">
          <span class="module-status-badge ${data.status === 'ok' ? 'ok' : data.status === 'warn' ? 'warn' : 'danger'}">
            ${data.status === 'ok' ? '良好' : data.status === 'warn' ? '注意' : '要対処'}
          </span>
          <span class="fw-600" style="font-size:20px">${data.score}</span>
        </div>
      </a>
    `;
  }).join('');
}

function renderNextActions() {
  const container = document.querySelector('.next-actions');
  if (!container) return;

  container.innerHTML = DEMO_DATA.nextActions.map(a => `
    <div class="alert-item ${a.priority === '緊急' ? 'urgent' : a.priority === '高' ? 'warning' : 'info'}">
      <div class="alert-icon ${a.priority === '緊急' ? 'urgent' : a.priority === '高' ? 'warning' : 'info'}">
        ${a.priority === '緊急' ? '🔴' : a.priority === '高' ? '🟠' : a.priority === '中' ? '🟡' : '🟢'}
      </div>
      <div class="alert-content">
        <div class="alert-title">${a.action}</div>
        <div class="alert-meta">
          <span class="alert-tag ${a.priority === '緊急' ? 'urgent' : 'warning'}">${a.priority}</span>
          <span>📅 ${a.deadline}</span>
        </div>
      </div>
    </div>
  `).join('');
}

// === Upload Page ===
function initUpload() {
  const zone = document.querySelector('.upload-zone');
  const fileInput = document.querySelector('#file-input');
  const previewArea = document.querySelector('.upload-preview');
  
  if (!zone || !fileInput) return;

  zone.addEventListener('click', () => fileInput.click());
  
  zone.addEventListener('dragover', (e) => {
    e.preventDefault();
    zone.classList.add('drag-over');
  });

  zone.addEventListener('dragleave', () => {
    zone.classList.remove('drag-over');
  });

  zone.addEventListener('drop', (e) => {
    e.preventDefault();
    zone.classList.remove('drag-over');
    handleFiles(e.dataTransfer.files);
  });

  fileInput.addEventListener('change', (e) => {
    handleFiles(e.target.files);
  });

  function handleFiles(files) {
    if (!previewArea) return;
    previewArea.innerHTML = '';
    
    Array.from(files).forEach(file => {
      if (!file.type.startsWith('image/')) return;
      
      const reader = new FileReader();
      reader.onload = (e) => {
        const div = document.createElement('div');
        div.classList.add('preview-item', 'animate-scale-in');
        div.innerHTML = `
          <img src="${e.target.result}" alt="${file.name}" style="width:100%;height:120px;object-fit:cover;border-radius:var(--radius-sm);">
          <div style="padding:8px;">
            <div class="fw-600" style="font-size:12px;white-space:nowrap;overflow:hidden;text-overflow:ellipsis;">${file.name}</div>
            <div class="text-muted" style="font-size:11px">${(file.size / 1024 / 1024).toFixed(1)}MB</div>
          </div>
        `;
        div.style.cssText = 'background:var(--bg-card);border:1px solid var(--border-color);border-radius:var(--radius-md);overflow:hidden;';
        previewArea.appendChild(div);
      };
      reader.readAsDataURL(file);
    });

    // Show analysis button
    const analyzeBtn = document.querySelector('.analyze-btn-container');
    if (analyzeBtn) analyzeBtn.style.display = 'block';
  }

  // Real analysis via API
  const analyzeBtn = document.querySelector('#analyze-btn');
  if (analyzeBtn) {
    analyzeBtn.addEventListener('click', () => {
      runAnalysis();
    });
  }
}

// API Base URL (Flask backend)
const API_BASE = window.location.port === '5001' ? '' : 'http://localhost:5001';

async function runAnalysis() {
  const progressContainer = document.querySelector('.analysis-progress');
  if (!progressContainer) return;

  progressContainer.style.display = 'block';
  const progressBar = progressContainer.querySelector('.progress-fill');
  const progressLabel = progressContainer.querySelector('.progress-label');

  // Progress animation
  const steps = [
    '画像をアップロード中...',
    '病害虫の検出中...',
    '雑草密度の解析中...',
    '畦畔・水路の確認中...',
    '総合スコアの算出中...'
  ];
  let stepIndex = 0;
  const stepInterval = setInterval(() => {
    if (stepIndex < steps.length) {
      progressLabel.textContent = steps[stepIndex];
      progressBar.style.width = ((stepIndex + 1) / (steps.length + 1) * 100) + '%';
      stepIndex++;
    }
  }, 2000);

  // Build FormData
  const formData = new FormData();
  const fileInput = document.querySelector('#file-input');
  if (fileInput && fileInput.files.length > 0) {
    Array.from(fileInput.files).forEach(f => formData.append('images', f));
  }

  // Add metadata
  const fields = {
    field_id: document.querySelector('#field-select')?.value || '',
    date: document.querySelector('#shoot-date')?.value || '',
    variety: document.querySelector('#variety-select')?.value || '',
    stage: document.querySelector('#stage-select')?.value || '',
    altitude: document.querySelector('#altitude-select')?.value || '30',
    camera: document.querySelector('#drone-select')?.value || '',
    weather_7days: document.querySelector('#weather-notes')?.value || ''
  };
  Object.entries(fields).forEach(([k, v]) => formData.append(k, v));

  try {
    const response = await fetch(`${API_BASE}/api/analyze`, {
      method: 'POST',
      body: formData
    });

    clearInterval(stepInterval);

    if (response.ok) {
      const data = await response.json();
      progressLabel.textContent = '解析完了！レポートを生成中...';
      progressBar.style.width = '100%';

      // Save result in sessionStorage for report page
      sessionStorage.setItem('agriscan_result', JSON.stringify(data.result));
      sessionStorage.setItem('agriscan_mode', data.mode);
      sessionStorage.setItem('agriscan_analysis_id', data.analysis_id);

      setTimeout(() => {
        window.location.href = 'report.html';
      }, 1000);
    } else {
      throw new Error('API error');
    }
  } catch (err) {
    clearInterval(stepInterval);
    console.log('API not available, using demo mode:', err.message);

    // Fallback: demo mode simulation
    progressLabel.textContent = '（デモモード）解析をシミュレーション中...';
    let demoStep = 0;
    const demoSteps = [
      { label: '病害虫の検出中...', duration: 800 },
      { label: '雑草密度の解析中...', duration: 600 },
      { label: '畦畔・水路の確認中...', duration: 500 },
      { label: '解析完了！', duration: 400 }
    ];

    function runDemoStep() {
      if (demoStep >= demoSteps.length) {
        setTimeout(() => { window.location.href = 'report.html'; }, 600);
        return;
      }
      const s = demoSteps[demoStep];
      progressLabel.textContent = s.label;
      progressBar.style.width = ((demoStep + 1) / demoSteps.length * 100) + '%';
      demoStep++;
      setTimeout(runDemoStep, s.duration);
    }
    runDemoStep();
  }
}

// === Report Page ===
function initReport() {
  renderDetections();
  renderWeedMap();
  renderInfrastructure();
  renderSprayTimeline();
  animateScoreRing();
  initTabs();
}

function renderDetections() {
  const container = document.querySelector('.detection-list');
  if (!container) return;

  container.innerHTML = DEMO_DATA.detections.map(d => `
    <div class="detection-item">
      <div class="detection-thumbnail">${d.icon}</div>
      <div class="detection-info">
        <div class="detection-name">
          ${d.name}
          <span class="badge badge-${d.severity === '重度' ? 'danger' : d.severity === '中度' ? 'warning' : 'info'}" style="margin-left:8px;">
            ${d.severity}
          </span>
        </div>
        <div class="detection-scientific">${d.name_scientific}</div>
        <div style="font-size:12px;color:var(--text-secondary);margin-bottom:8px;">
          📍 ${d.field_name} ｜ 被害面積: ${d.affected_area_m2}m² (${d.affected_area_ratio}%)
        </div>
        <div class="confidence-bar" style="margin-bottom:8px;">
          <span style="font-size:11px;color:var(--text-muted);min-width:50px;">確信度</span>
          <div class="bar">
            <div class="fill ${d.confidence >= 80 ? 'green' : d.confidence >= 50 ? 'amber' : 'red'}" 
                 style="width:${d.confidence}%;background:${d.confidence >= 80 ? 'linear-gradient(90deg,#43a047,#66bb6a)' : d.confidence >= 50 ? 'linear-gradient(90deg,#ff9800,#ffc107)' : 'linear-gradient(90deg,#ef5350,#ff7043)'}"></div>
          </div>
          <span class="value" style="color:${d.confidence >= 80 ? 'var(--success)' : d.confidence >= 50 ? 'var(--warning)' : 'var(--danger)'}">${d.confidence}%</span>
        </div>
        <div style="font-size:12px;color:var(--text-muted);line-height:1.5;margin-bottom:8px;">
          <strong>視覚的根拠:</strong> ${d.visual_evidence}
        </div>
        <div style="display:flex;gap:12px;flex-wrap:wrap;align-items:center;">
          <span class="badge badge-${d.urgency === '即時対応' ? 'danger' : d.urgency === '1週間以内' ? 'warning' : 'info'}">
            ⏰ ${d.urgency}
          </span>
          <span style="font-size:11px;color:var(--text-secondary);">💊 ${d.recommended_pesticide}</span>
        </div>
      </div>
    </div>
  `).join('');
}

function renderWeedMap() {
  const container = document.querySelector('.weed-density-grid');
  if (!container) return;

  const levelMap = ['', 'low', 'medium', 'high', 'very-high'];
  
  DEMO_DATA.weedDensity.grid.forEach(row => {
    row.forEach(cell => {
      const div = document.createElement('div');
      div.classList.add('weed-cell', levelMap[cell]);
      div.title = `密度レベル: ${cell}`;
      container.appendChild(div);
    });
  });

  // Render weed list
  const weedList = document.querySelector('.weed-found-list');
  if (weedList) {
    weedList.innerHTML = DEMO_DATA.weedDensity.weeds_found.map(w => `
      <div style="display:flex;align-items:center;justify-content:space-between;padding:8px 0;border-bottom:1px solid var(--border-color);">
        <span style="font-size:13px;font-weight:600;">${w.name}</span>
        <div style="display:flex;align-items:center;gap:8px;">
          <span style="font-size:12px;color:var(--text-muted);">被覆率 ${w.coverage}%</span>
          <span class="badge badge-${w.status === '注意' ? 'warning' : 'success'}">${w.status}</span>
        </div>
      </div>
    `).join('');
  }
}

function renderInfrastructure() {
  const container = document.querySelector('.infra-list');
  if (!container) return;

  container.innerHTML = DEMO_DATA.infrastructure.map(item => `
    <div class="alert-item ${item.severity === '要清掃' ? 'warning' : 'info'}">
      <div class="alert-icon ${item.severity === '要清掃' ? 'warning' : 'info'}">
        ${item.icon}
      </div>
      <div class="alert-content">
        <div class="alert-title">${item.type}</div>
        <div class="alert-desc">📍 ${item.location}</div>
        <div class="alert-desc">${item.description}</div>
        <div class="alert-meta">
          <span class="badge badge-warning">${item.severity}</span>
          <span style="font-size:11px;color:var(--text-muted);">推奨: ${item.recommendation}</span>
        </div>
      </div>
    </div>
  `).join('');
}

function renderSprayTimeline() {
  const container = document.querySelector('.spray-timeline');
  if (!container) return;

  container.innerHTML = `<div class="timeline">
    ${DEMO_DATA.sprayRecords.map(r => `
      <div class="timeline-item">
        <div class="timeline-date">${r.date} ${r.time}</div>
        <div class="timeline-content">
          <div class="timeline-title">${r.pesticide}</div>
          <div class="timeline-desc">
            📍 ${r.field}<br>
            📐 散布面積: ${r.area_ha}ha ｜ 💧 散布量: ${r.volume_l}L<br>
            🚁 ${r.drone} ｜ 👤 ${r.operator}<br>
            🌤️ ${r.weather}
          </div>
          <div style="margin-top:8px;">
            <span class="badge badge-success">✅ ${r.status}</span>
          </div>
        </div>
      </div>
    `).join('')}
  </div>`;
}

function initTabs() {
  document.querySelectorAll('.tab').forEach(tab => {
    tab.addEventListener('click', () => {
      const target = tab.dataset.tab;
      
      // Deactivate all tabs
      tab.closest('.tabs').querySelectorAll('.tab').forEach(t => t.classList.remove('active'));
      tab.classList.add('active');
      
      // Show target content
      document.querySelectorAll('.tab-content').forEach(c => c.classList.remove('active'));
      const targetEl = document.querySelector(`#${target}`);
      if (targetEl) targetEl.classList.add('active');
    });
  });
}

// === Fields Page ===
async function initFields() {
  let fields;
  try {
    const res = await fetch(`${API_BASE}/api/fields`);
    const data = await res.json();
    fields = data.fields;
  } catch (e) {
    // API不可時はデモデータにフォールバック
    fields = DEMO_DATA.fields;
  }
  renderFieldCards(fields);
  initFieldMap(fields);

  // パンくず更新
  const breadcrumb = document.querySelector('.page-breadcrumb');
  if (breadcrumb) {
    const totalArea = fields.reduce((s, f) => s + (f.area_ha || 0), 0);
    breadcrumb.textContent = `筑前町周辺 — 管理圃場${fields.length}区画（${totalArea.toFixed(1)}ha）`;
  }

  // 統計カード更新
  const totalEl = document.getElementById('stat-total-fields');
  const areaEl = document.getElementById('stat-total-area');
  const goodEl = document.getElementById('stat-good');
  const cautionEl = document.getElementById('stat-caution');
  const dangerEl = document.getElementById('stat-danger');
  if (totalEl) {
    const totalArea = fields.reduce((s, f) => s + (f.area_ha || 0), 0);
    const good = fields.filter(f => f.status === 'good').length;
    const caution = fields.filter(f => f.status === 'caution').length;
    const danger = fields.filter(f => f.status === 'action' || f.status === 'urgent').length;
    totalEl.textContent = fields.length;
    areaEl.innerHTML = `${totalArea.toFixed(1)}<span style="font-size:14px;">ha</span>`;
    goodEl.textContent = good;
    cautionEl.textContent = caution;
    dangerEl.textContent = danger;
  }
}

function renderFieldCards(fields) {
  const container = document.querySelector('.field-list');
  if (!container) return;

  container.innerHTML = fields.map((f, i) => `
    <div class="field-card animate-slide-up stagger-${(i % 5) + 1}">
      <div class="field-card-map" id="field-mini-map-${f.id}" style="background:linear-gradient(135deg, rgba(30,45,35,0.9), rgba(22,32,25,0.7));display:flex;align-items:center;justify-content:center;">
        <span style="font-size:48px;opacity:0.3;">🌾</span>
      </div>
      <div class="field-card-body">
        <div class="field-card-name">${f.name}</div>
        <div class="field-card-detail">
          <span>👤 ${f.farmer || '未設定'}</span>
          <span>📐 ${f.area_ha}ha</span>
          <span>🌾 ${f.variety || '未設定'}</span>
        </div>
        <div class="field-card-footer">
          <div>
            <div style="font-size:11px;color:var(--text-muted);">健康スコア</div>
            <div class="flex items-center gap-sm">
              <div class="severity-bar" style="width:60px">
                <div class="fill ${f.health_score >= 80 ? 'green' : f.health_score >= 50 ? 'amber' : 'red'}" 
                     style="width:${f.health_score}%"></div>
              </div>
              <span class="fw-700">${f.health_score}</span>
            </div>
          </div>
          <span class="badge badge-${f.status === 'good' ? 'success' : f.status === 'caution' ? 'warning' : 'danger'}">
            ${f.status === 'good' ? '良好' : f.status === 'caution' ? '注意' : f.status === 'action' ? '要対処' : '緊急'}
          </span>
        </div>
      </div>
    </div>
  `).join('');
}

function initFieldMap(fields) {
  const mapContainer = document.querySelector('#field-map');
  if (!mapContainer || typeof L === 'undefined') return;

  const map = L.map('field-map', {
    center: [33.4547, 130.6473],
    zoom: 15,
    zoomControl: true
  });

  // 衛星写真タイル（Esri World Imagery — 無料）
  L.tileLayer('https://server.arcgisonline.com/ArcGIS/rest/services/World_Imagery/MapServer/tile/{z}/{y}/{x}', {
    attribution: 'Tiles &copy; Esri',
    maxZoom: 19
  }).addTo(map);
  // 地名・道路ラベルのオーバーレイ
  L.tileLayer('https://server.arcgisonline.com/ArcGIS/rest/services/Reference/World_Transportation/MapServer/tile/{z}/{y}/{x}', {
    maxZoom: 19, opacity: 0.7
  }).addTo(map);

  // Add field markers
  const bounds = [];
  fields.forEach(f => {
    const loc = f.location || { lat: f.lat, lng: f.lng };
    if (!loc || !loc.lat || !loc.lng) return;

    const color = f.health_score >= 80 ? '#4caf50' : f.health_score >= 50 ? '#ff9800' : '#ef5350';
    bounds.push([loc.lat, loc.lng]);
    
    const marker = L.circleMarker([loc.lat, loc.lng], {
      radius: 12,
      fillColor: color,
      fillOpacity: 0.7,
      color: color,
      weight: 2,
      opacity: 0.9
    }).addTo(map);

    marker.bindPopup(`
      <div style="font-family:'Noto Sans JP',sans-serif;min-width:200px;">
        <div style="font-weight:700;font-size:14px;margin-bottom:4px;">${f.name}</div>
        <div style="font-size:12px;color:#666;margin-bottom:8px;">${f.farmer || ''} ｜ ${f.variety || ''} ｜ ${f.area_ha}ha</div>
        <div style="font-size:13px;">
          <strong>健康スコア: </strong><span style="color:${color};font-weight:700;">${f.health_score}</span>/100<br>
          <strong>生育ステージ: </strong>${f.stage || '未設定'}<br>
          <strong>最終診断: </strong>${f.last_inspection || '未実施'}
        </div>
      </div>
    `);
  });

  // 全圃場が見えるようにマップを調整
  if (bounds.length > 1) {
    map.fitBounds(bounds, { padding: [30, 30] });
  }
}

// === Utility Functions ===
function formatDate(dateStr) {
  const d = new Date(dateStr);
  return d.toLocaleDateString('ja-JP', { year: 'numeric', month: 'short', day: 'numeric' });
}
