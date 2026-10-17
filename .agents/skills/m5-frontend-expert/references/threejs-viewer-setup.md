# REFERENCE: THREE.JS 3D VIEWER CONFIGURATION & BEST PRACTICES (M5)

Tài liệu tham khảo thiết lập Three.js Scene, Camera, Lighting và OrbitControls cho Module M5.

---

## 1. Thiết lập Three.js Scene Chuẩn

```javascript
import * as THREE from 'three';
import { OrbitControls } from 'three/examples/jsm/controls/OrbitControls';
import { GLTFLoader } from 'three/examples/jsm/loaders/GLTFLoader';

// 1. Scene & Background
const scene = new THREE.Scene();
scene.background = new THREE.Color(0xf8fafc); // Màu nền Slate-50 thanh lịch

// 2. Camera Framing
const camera = new THREE.PerspectiveCamera(45, window.innerWidth / window.innerHeight, 0.1, 1000);
camera.position.set(0, 1.0, 2.3); // Hướng vào thân trên người mẫu

// 3. Renderer với khử răng cưa
const renderer = new THREE.WebGLRenderer({ antialias: true, alpha: true });
renderer.setPixelRatio(Math.min(window.devicePixelRatio, 2));
renderer.toneMapping = THREE.ACESFilmicToneMapping;
renderer.toneMappingExposure = 1.0;

// 4. Ánh sáng đa chiều (Studio Lighting Setup)
const ambientLight = new THREE.AmbientLight(0xffffff, 0.7);
scene.add(ambientLight);

const keyLight = new THREE.DirectionalLight(0xffffff, 1.0);
keyLight.position.set(1.5, 2.5, 2.0); // Góc trên bên phải phía trước
scene.add(keyLight);

const fillLight = new THREE.DirectionalLight(0xffffff, 0.4);
fillLight.position.set(-1.5, 1.5, 1.5); // Ánh sáng bù bên trái
scene.add(fillLight);

// 5. Controls
const controls = new OrbitControls(camera, renderer.domElement);
controls.target.set(0, 0.9, 0); // Trọng tâm xoay quanh ngực/eo
controls.enableDamping = true;
controls.dampingFactor = 0.05;
controls.maxPolarAngle = Math.PI / 2 + 0.1; // Không cho xoay xuống dưới mặt đất
```
