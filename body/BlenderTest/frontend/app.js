/**
 * BodyForge — Main Application JS
 * Three.js 3D Viewer + FastAPI Integration + Body Controls
 */

import * as THREE from 'three';
import { GLTFLoader } from 'three/addons/loaders/GLTFLoader.js';
import { OrbitControls } from 'three/addons/controls/OrbitControls.js';
import { RGBELoader } from 'three/addons/loaders/RGBELoader.js';

// ══════════════════════════════════════════════════════════════
//   CONSTANTS & CONFIG
// ══════════════════════════════════════════════════════════════

const API_BASE = 'http://localhost:8000';
const POLL_INTERVAL_MS = 1500;

const CLOTHING_CATALOG = [
  { id: 'tshirt_basic',    name: 'T-Shirt',     emoji: '👕', category: 'tops' },
  { id: 'hoodie',          name: 'Hoodie',       emoji: '🧥', category: 'tops' },
  { id: 'jacket',          name: 'Jacket',       emoji: '🥼', category: 'tops' },
  { id: 'jeans_straight',  name: 'Quần Jeans',  emoji: '👖', category: 'bottoms' },
  { id: 'shorts',          name: 'Quần Short',  emoji: '🩳', category: 'bottoms' },
  { id: 'dress_summer',    name: 'Váy Hè',      emoji: '👗', category: 'dresses' },
  { id: 'dress_formal',    name: 'Đầm Dạ Hội',  emoji: '👘', category: 'dresses' },
  { id: 'skirt',           name: 'Chân Váy',    emoji: '🩱', category: 'bottoms' },
];

const COLOR_PALETTE = [
  '#FFFFFF', '#1C1C1E', '#FF3B30', '#FF9500',
  '#FFCC00', '#34C759', '#007AFF', '#5856D6',
  '#FF2D55', '#AF52DE', '#5AC8FA', '#4CD964',
];

const PRESETS = {
  slim:     { height: 170, weight: 50, proportions: { shoulder_width: 0.3, waist: 0.25, hips: 0.3, chest: 0.3, belly: 0.05, muscle_tone: 0.2, leg_length: 0.6, arm_length: 0.5 } },
  athletic: { height: 175, weight: 70, proportions: { shoulder_width: 0.75, waist: 0.4, hips: 0.5, chest: 0.7, belly: 0.1, muscle_tone: 0.8, leg_length: 0.6, arm_length: 0.6 } },
  curvy:    { height: 163, weight: 68, proportions: { shoulder_width: 0.5, waist: 0.45, hips: 0.85, chest: 0.75, belly: 0.3, muscle_tone: 0.2, leg_length: 0.45, arm_length: 0.45 } },
  petite:   { height: 155, weight: 45, proportions: { shoulder_width: 0.3, waist: 0.3, hips: 0.4, chest: 0.35, belly: 0.1, muscle_tone: 0.15, leg_length: 0.35, arm_length: 0.35 } },
};

// ══════════════════════════════════════════════════════════════
//   APPLICATION STATE
// ══════════════════════════════════════════════════════════════

const state = {
  gender: 'female',
  height: 170,
  weight: 65,
  age: 25,
  proportions: {
    shoulder_width: 0.5, waist: 0.5, hips: 0.5, chest: 0.5,
    belly: 0.2, muscle_tone: 0.3, leg_length: 0.5, arm_length: 0.5, buttocks: 0.5,
  },
  skin: { tone: 'medium', color_hex: '#C68642' },
  currentJobId: null,
  currentModelId: null,
  currentGlbUrl: null,
  isGenerating: false,
  selectedClothingId: null,
  selectedClothingColor: '#FFFFFF',
  wireframe: false,
};

// ══════════════════════════════════════════════════════════════
//   THREE.JS SETUP
// ══════════════════════════════════════════════════════════════

let scene, camera, renderer, controls, currentModel, loader;

function initThree() {
  const canvas = document.getElementById('three-canvas');
  const container = document.getElementById('viewport');

  // Renderer
  renderer = new THREE.WebGLRenderer({ canvas, antialias: true, alpha: true });
  renderer.setPixelRatio(window.devicePixelRatio);
  renderer.outputColorSpace = THREE.SRGBColorSpace;
  renderer.toneMapping = THREE.ACESFilmicToneMapping;
  renderer.toneMappingExposure = 1.0;
  renderer.shadowMap.enabled = true;
  renderer.shadowMap.type = THREE.PCFSoftShadowMap;

  // Scene
  scene = new THREE.Scene();
  scene.background = null;

  // Camera
  camera = new THREE.PerspectiveCamera(45, 1, 0.01, 100);
  camera.position.set(0, 1.2, 3.5);

  // Lights
  const ambientLight = new THREE.AmbientLight(0xffffff, 0.6);
  scene.add(ambientLight);

  const keyLight = new THREE.DirectionalLight(0xA78BFA, 1.8); // purple tint
  keyLight.position.set(2, 4, 3);
  keyLight.castShadow = true;
  scene.add(keyLight);

  const fillLight = new THREE.DirectionalLight(0x22D3EE, 0.8); // cyan tint
  fillLight.position.set(-2, 2, -1);
  scene.add(fillLight);

  const rimLight = new THREE.DirectionalLight(0xffffff, 0.4);
  rimLight.position.set(0, -2, -3);
  scene.add(rimLight);

  // Floor plane (subtle)
  const floorGeo = new THREE.CircleGeometry(2, 64);
  const floorMat = new THREE.MeshStandardMaterial({
    color: 0x151829, roughness: 1, metalness: 0, transparent: true, opacity: 0.5,
  });
  const floor = new THREE.Mesh(floorGeo, floorMat);
  floor.rotation.x = -Math.PI / 2;
  floor.position.y = -0.01;
  floor.receiveShadow = true;
  scene.add(floor);

  // Grid helper
  const grid = new THREE.GridHelper(4, 20, 0x222640, 0x1a1e38);
  grid.position.y = 0;
  scene.add(grid);

  // Controls
  controls = new OrbitControls(camera, renderer.domElement);
  controls.enableDamping = true;
  controls.dampingFactor = 0.08;
  controls.target.set(0, 0.85, 0);
  controls.minDistance = 0.5;
  controls.maxDistance = 8;
  controls.maxPolarAngle = Math.PI * 0.85;
  controls.update();

  // GLTFLoader
  loader = new GLTFLoader();

  // Handle resize
  const ro = new ResizeObserver(() => resizeRenderer());
  ro.observe(container);
  resizeRenderer();

  // Animate loop
  animate();
}

function resizeRenderer() {
  const container = document.getElementById('viewport');
  const w = container.clientWidth;
  const h = container.clientHeight;
  renderer.setSize(w, h, false);
  camera.aspect = w / h;
  camera.updateProjectionMatrix();
}

function animate() {
  requestAnimationFrame(animate);
  controls.update();
  renderer.render(scene, camera);
}

// ── Load GLB from URL ──────────────────────────────────────────
function loadGLBModel(url) {
  // Remove old model
  if (currentModel) {
    scene.remove(currentModel);
    currentModel = null;
  }

  loader.load(
    url,
    (gltf) => {
      currentModel = gltf.scene;

      // Center model
      const box = new THREE.Box3().setFromObject(currentModel);
      const center = box.getCenter(new THREE.Vector3());
      const size = box.getSize(new THREE.Vector3());
      currentModel.position.sub(center);
      currentModel.position.y += size.y / 2;

      // Enable shadows on all meshes
      currentModel.traverse((node) => {
        if (node.isMesh) {
          node.castShadow = true;
          node.receiveShadow = true;
        }
      });

      scene.add(currentModel);

      // Focus camera on model
      const height = size.y;
      controls.target.set(0, height * 0.45, 0);
      camera.position.set(0, height * 0.5, height * 1.8);
      controls.update();

      // Show canvas
      document.getElementById('three-canvas').style.display = 'block';
      document.getElementById('empty-state').style.display = 'none';

      // Update info bar
      document.getElementById('model-info').textContent =
        `Model: ${url.split('/').pop()} • ${size.y.toFixed(2)}m tall`;

      // Enable download
      document.getElementById('btn-download').disabled = false;
      document.getElementById('btn-apply-clothing').disabled = false;

      showToast('✅ Mô hình đã tải xong!', 'success');
    },
    (progress) => {
      // Loading progress
    },
    (error) => {
      console.error('GLB load error:', error);
      showToast('❌ Lỗi tải mô hình 3D', 'error');
    }
  );
}

// ══════════════════════════════════════════════════════════════
//   API CALLS
// ══════════════════════════════════════════════════════════════

async function checkServerHealth() {
  const badge = document.getElementById('connection-status');
  const text = document.getElementById('status-text');
  try {
    const res = await fetch(`${API_BASE}/`, { signal: AbortSignal.timeout(3000) });
    if (res.ok) {
      badge.className = 'status-badge status-online';
      text.textContent = 'Server Online';
    } else {
      throw new Error('not ok');
    }
  } catch {
    badge.className = 'status-badge status-offline';
    text.textContent = 'Server Offline';
  }
}

async function generateModel() {
  if (state.isGenerating) return;

  const btn = document.getElementById('btn-generate');
  state.isGenerating = true;
  btn.disabled = true;

  // Show loading
  const overlay = document.getElementById('loading-overlay');
  overlay.style.display = 'flex';
  setLoadingMessage('Gửi yêu cầu đến Blender...');

  try {
    // Build params
    const params = {
      height: state.height / 100,
      weight: state.weight,
      age: state.age,
      gender: state.gender,
      proportions: { ...state.proportions },
      skin: { ...state.skin },
    };

    // POST to API
    const res = await fetch(`${API_BASE}/api/generate`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(params),
    });

    if (!res.ok) {
      const err = await res.json();
      throw new Error(err.detail || 'API error');
    }

    const { job_id } = await res.json();
    state.currentJobId = job_id;

    setLoadingMessage('Blender đang xử lý...');
    await pollJobStatus(job_id);

  } catch (err) {
    console.error(err);
    showToast(`❌ Lỗi: ${err.message}`, 'error');
    overlay.style.display = 'none';
    state.isGenerating = false;
    btn.disabled = false;
  }
}

async function pollJobStatus(jobId) {
  const overlay = document.getElementById('loading-overlay');
  const messages = [
    'Blender khởi tạo scene...',
    'Áp dụng MPFB morphs...',
    'Tạo skin material...',
    'Export GLB model...',
    'Hoàn thiện...',
  ];
  let msgIdx = 0;
  const msgInterval = setInterval(() => {
    setLoadingMessage(messages[Math.min(msgIdx++, messages.length - 1)]);
  }, 2000);

  return new Promise((resolve, reject) => {
    const interval = setInterval(async () => {
      try {
        const res = await fetch(`${API_BASE}/api/status/${jobId}`);
        const data = await res.json();

        if (data.status === 'done') {
          clearInterval(interval);
          clearInterval(msgInterval);
          overlay.style.display = 'none';
          state.isGenerating = false;
          document.getElementById('btn-generate').disabled = false;

          state.currentModelId = jobId;
          state.currentGlbUrl = `${API_BASE}${data.glb_url}`;

          loadGLBModel(state.currentGlbUrl);
          resolve();

        } else if (data.status === 'error') {
          clearInterval(interval);
          clearInterval(msgInterval);
          overlay.style.display = 'none';
          state.isGenerating = false;
          document.getElementById('btn-generate').disabled = false;

          showToast(`❌ Blender lỗi: ${data.error}`, 'error');
          reject(new Error(data.error));
        }
        // else: still queued/processing, keep polling

      } catch (err) {
        clearInterval(interval);
        clearInterval(msgInterval);
        overlay.style.display = 'none';
        state.isGenerating = false;
        document.getElementById('btn-generate').disabled = false;
        reject(err);
      }
    }, POLL_INTERVAL_MS);
  });
}

async function applyClothing() {
  if (!state.currentModelId || !state.selectedClothingId) {
    showToast('⚠️ Cần tạo body model trước!', 'info');
    return;
  }

  const overlay = document.getElementById('loading-overlay');
  overlay.style.display = 'flex';
  setLoadingMessage('Đang mặc quần áo...');

  try {
    const res = await fetch(`${API_BASE}/api/clothing`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        model_id: state.currentModelId,
        clothing_id: state.selectedClothingId,
        color_hex: state.selectedClothingColor,
      }),
    });

    if (!res.ok) throw new Error('Clothing API error');

    const { job_id } = await res.json();
    await pollJobStatus(job_id);

  } catch (err) {
    overlay.style.display = 'none';
    showToast(`❌ Lỗi: ${err.message}`, 'error');
  }
}

// ══════════════════════════════════════════════════════════════
//   UI CONTROLS
// ══════════════════════════════════════════════════════════════

function updateSlider(key, value, unit) {
  const numVal = parseFloat(value);
  state[key] = numVal;
  document.getElementById(`val-${key}`).textContent = `${numVal} ${unit}`;
}

function updatePropSlider(key, value) {
  const norm = parseInt(value) / 100;
  state.proportions[key] = norm;

  // Map slider IDs to keys
  const labelMap = {
    shoulder_width: 'shoulder', waist: 'waist', hips: 'hips',
    chest: 'chest', belly: 'belly', muscle_tone: 'muscle',
    leg_length: 'leg', arm_length: 'arm',
  };
  const labelId = labelMap[key] || key;
  const el = document.getElementById(`val-${labelId}`);
  if (el) el.textContent = `${parseInt(value)}%`;

  // Live update mannequin preview (if model exists)
  updateLivePreview();
}

function updateLivePreview() {
  if (!currentModel) return;
  // Subtle real-time visual feedback via scale morphing
  const p = state.proportions;
  const shoulderScale = 0.8 + p.shoulder_width * 0.4;
  currentModel.traverse((node) => {
    if (node.isMesh && node.name.includes('shoulder')) {
      node.scale.x = shoulderScale;
    }
  });
}

function setGender(gender) {
  state.gender = gender;
  document.getElementById('btn-female').classList.toggle('active', gender === 'female');
  document.getElementById('btn-male').classList.toggle('active', gender === 'male');
}

function setSkin(hex) {
  state.skin.color_hex = hex;
  document.getElementById('custom-skin').value = hex;

  document.querySelectorAll('.skin-btn').forEach(btn => {
    const btnColor = btn.style.background?.replace(/\s/g,'').toUpperCase();
    btn.classList.toggle('active', btnColor === hex.toUpperCase());
  });
}

function loadPreset(name) {
  const preset = PRESETS[name];
  if (!preset) return;

  state.height = preset.height;
  state.weight = preset.weight || state.weight;
  document.getElementById('sl-height').value = preset.height;
  document.getElementById('val-height').textContent = `${preset.height} cm`;

  Object.entries(preset.proportions).forEach(([key, val]) => {
    state.proportions[key] = val;
    const labelMap = {
      shoulder_width: 'shoulder', waist: 'waist', hips: 'hips',
      chest: 'chest', belly: 'belly', muscle_tone: 'muscle',
      leg_length: 'leg', arm_length: 'arm',
    };
    const sliderMap = {
      shoulder_width: 'shoulder', waist: 'waist', hips: 'hips',
      chest: 'chest', belly: 'belly', muscle_tone: 'muscle',
      leg_length: 'leg', arm_length: 'arm',
    };

    const sliderId = `sl-${sliderMap[key] || key}`;
    const labelId = `val-${labelMap[key] || key}`;
    const slEl = document.getElementById(sliderId);
    const lbEl = document.getElementById(labelId);

    if (slEl) slEl.value = Math.round(val * 100);
    if (lbEl) lbEl.textContent = `${Math.round(val * 100)}%`;
  });

  showToast(`✨ Đã áp dụng preset "${name}"`, 'info');
}

function resetParams() {
  ['sl-height', 'sl-weight', 'sl-age'].forEach(id => {
    const el = document.getElementById(id);
    if (el) el.value = el.defaultValue;
  });

  state.height = 170; state.weight = 65; state.age = 25; state.gender = 'female';
  document.getElementById('val-height').textContent = '170 cm';
  document.getElementById('val-weight').textContent = '65 kg';
  document.getElementById('val-age').textContent = '25 tuổi';

  ['shoulder_width', 'waist', 'hips', 'chest', 'belly', 'leg_length', 'arm_length'].forEach(k => {
    state.proportions[k] = 0.5;
  });
  state.proportions.belly = 0.2;
  state.proportions.muscle_tone = 0.3;

  const defaults = {
    shoulder: 50, waist: 50, hips: 50, chest: 50,
    belly: 20, muscle: 30, leg: 50, arm: 50,
  };

  Object.entries(defaults).forEach(([k, v]) => {
    const el = document.getElementById(`sl-${k}`);
    if (el) el.value = v;
    const vEl = document.getElementById(`val-${k}`);
    if (vEl) vEl.textContent = `${v}%`;
  });

  setGender('female');
  showToast('🔄 Đã đặt lại', 'info');
}

function switchTab(tab) {
  document.getElementById('panel-body').classList.toggle('hidden', tab !== 'body');
  document.getElementById('panel-clothing').classList.toggle('hidden', tab !== 'clothing');
  document.getElementById('nav-body').classList.toggle('active', tab === 'body');
  document.getElementById('nav-clothing').classList.toggle('active', tab === 'clothing');
}

// ── Clothing panel ─────────────────────────────────────────────
function buildClothingGrid(filter = 'all') {
  const grid = document.getElementById('clothing-grid');
  const items = filter === 'all'
    ? CLOTHING_CATALOG
    : CLOTHING_CATALOG.filter(c => c.category === filter);

  grid.innerHTML = items.map(item => `
    <div class="clothing-item ${state.selectedClothingId === item.id ? 'selected' : ''}"
         id="cloth-${item.id}"
         onclick="selectClothing('${item.id}')">
      <div class="clothing-preview">${item.emoji}</div>
      <div class="clothing-name">${item.name}</div>
    </div>
  `).join('');
}

function selectClothing(id) {
  state.selectedClothingId = id;
  document.querySelectorAll('.clothing-item').forEach(el => el.classList.remove('selected'));
  const el = document.getElementById(`cloth-${id}`);
  if (el) el.classList.add('selected');
  document.getElementById('clothing-color-section').style.display = 'block';
  document.getElementById('btn-apply-clothing').disabled = !state.currentModelId;
}

function buildColorPalette() {
  const el = document.getElementById('color-palette');
  el.innerHTML = COLOR_PALETTE.map(c => `
    <div class="color-swatch ${state.selectedClothingColor === c ? 'active' : ''}"
         style="background:${c}"
         onclick="selectClothingColor('${c}', this)"
         title="${c}">
    </div>
  `).join('');
}

function selectClothingColor(hex, el) {
  state.selectedClothingColor = hex;
  document.querySelectorAll('.color-swatch').forEach(s => s.classList.remove('active'));
  if (el) el.classList.add('active');
}

function filterClothing(cat, el) {
  document.querySelectorAll('.cat-btn').forEach(b => b.classList.remove('active'));
  if (el) el.classList.add('active');
  buildClothingGrid(cat);
}

// ── Viewport controls ──────────────────────────────────────────
function resetCamera() {
  camera.position.set(0, 1.2, 3.5);
  controls.target.set(0, 0.85, 0);
  controls.update();
}

function toggleWireframe() {
  state.wireframe = !state.wireframe;
  const btn = document.getElementById('btn-wireframe');
  btn.classList.toggle('active', state.wireframe);

  if (currentModel) {
    currentModel.traverse((node) => {
      if (node.isMesh) {
        node.material.wireframe = state.wireframe;
      }
    });
  }
}

function downloadModel() {
  if (!state.currentGlbUrl) return;
  const a = document.createElement('a');
  a.href = state.currentGlbUrl;
  a.download = `bodyforge_${state.currentModelId}.glb`;
  a.click();
  showToast('⬇️ Đang tải model...', 'info');
}

// ── Toast ──────────────────────────────────────────────────────
function showToast(msg, type = 'info') {
  const toast = document.getElementById('toast');
  toast.textContent = msg;
  toast.className = `toast show ${type}`;
  setTimeout(() => toast.classList.remove('show'), 3000);
}

function setLoadingMessage(msg) {
  const el = document.getElementById('loading-sub');
  if (el) el.textContent = msg;
}

// ══════════════════════════════════════════════════════════════
//   INIT
// ══════════════════════════════════════════════════════════════

// Expose functions to HTML onclick handlers
window.updateSlider = updateSlider;
window.updatePropSlider = updatePropSlider;
window.setGender = setGender;
window.setSkin = setSkin;
window.loadPreset = loadPreset;
window.resetParams = resetParams;
window.generateModel = generateModel;
window.applyClothing = applyClothing;
window.switchTab = switchTab;
window.selectClothing = selectClothing;
window.selectClothingColor = selectClothingColor;
window.filterClothing = filterClothing;
window.resetCamera = resetCamera;
window.toggleWireframe = toggleWireframe;
window.downloadModel = downloadModel;

document.addEventListener('DOMContentLoaded', () => {
  initThree();
  buildClothingGrid();
  buildColorPalette();

  // Check server health
  checkServerHealth();
  setInterval(checkServerHealth, 15000);
});
