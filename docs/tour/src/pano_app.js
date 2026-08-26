// Café Napoli — recorrido fotorrealista 360 (panorámicas Cycles)
import * as THREE from 'three';

const NAP = window.NAP;
const NODES = NAP.nodes;      // {name: [x, y]}  coords Blender (z arriba)
const LINKS = NAP.links;      // {name: [name...]}
const EYE = 1.55;

const canvas = document.getElementById('c');
const renderer = new THREE.WebGLRenderer({ canvas, antialias: true });
renderer.setPixelRatio(Math.min(devicePixelRatio, 2));
renderer.outputColorSpace = THREE.SRGBColorSpace;

const scene = new THREE.Scene();
const camera = new THREE.PerspectiveCamera(68, 1, 0.1, 120);
scene.add(camera);

// dos esferas para fundido entre posiciones
function makeSphere() {
  const g = new THREE.SphereGeometry(50, 72, 48);
  g.scale(-1, 1, 1);
  const m = new THREE.MeshBasicMaterial({ transparent: true, opacity: 0 });
  const mesh = new THREE.Mesh(g, m);
  mesh.rotation.y = -Math.PI / 2;   // centro de la imagen = +Y de Blender
  scene.add(mesh);
  return mesh;
}
const sphA = makeSphere(), sphB = makeSphere();
let front = sphA, back = sphB;

const texCache = {};
const loader = new THREE.TextureLoader();
function getPano(name) {
  if (!texCache[name]) {
    texCache[name] = new Promise(res => loader.load(NAP.panos[name], t => {
      t.colorSpace = THREE.SRGBColorSpace;
      t.anisotropy = Math.min(8, renderer.capabilities.getMaxAnisotropy());
      res(t);
    }));
  }
  return texCache[name];
}

// direccion Blender -> three (y arriba): (x, y, z) -> (x, z, -y)
function dirTo(from, to) {
  const dx = NODES[to][0] - NODES[from][0];
  const dy = NODES[to][1] - NODES[from][1];
  return { v: new THREE.Vector3(dx, -EYE + 0.05, -dy), d: Math.hypot(dx, dy) };
}

// hotspots: anillos en el suelo hacia cada nodo enlazado
const hotGroup = new THREE.Group();
scene.add(hotGroup);
const ringGeo = new THREE.RingGeometry(0.42, 0.62, 40);
const ringGeo2 = new THREE.RingGeometry(0.16, 0.24, 32);
function buildHotspots(node) {
  hotGroup.clear();
  for (const other of LINKS[node]) {
    const { v } = dirTo(node, other);
    const p = v.clone().normalize().multiplyScalar(16);
    for (const [g, op] of [[ringGeo, 0.85], [ringGeo2, 0.55]]) {
      const m = new THREE.Mesh(g, new THREE.MeshBasicMaterial({
        color: 0xffffff, transparent: true, opacity: op,
        side: THREE.DoubleSide, depthTest: false }));
      m.position.copy(p);
      m.rotation.x = -Math.PI / 2;
      m.renderOrder = 10;
      m.userData.target = other;
      hotGroup.add(m);
    }
  }
}

let current = null, moving = false;
async function goTo(node, instant) {
  if (moving || node === current) return;
  moving = true;
  const tex = await getPano(node);
  back.material.map = tex;
  back.material.needsUpdate = true;
  back.material.opacity = 0;
  hotGroup.visible = false;
  const dur = instant ? 0 : 480;
  const t0 = performance.now();
  const f0 = camera.fov;
  await new Promise(res => {
    function step(t) {
      const k = dur ? Math.min(1, (t - t0) / dur) : 1;
      back.material.opacity = k;
      camera.fov = f0 - Math.sin(k * Math.PI) * 7;   // pequeño empuje
      camera.updateProjectionMatrix();
      if (k < 1) requestAnimationFrame(step); else res();
    }
    requestAnimationFrame(step);
  });
  const tmp = front; front = back; back = tmp;
  back.material.opacity = 0;
  current = node;
  buildHotspots(node);
  hotGroup.visible = true;
  moving = false;
  // precarga de los vecinos
  for (const o of LINKS[node]) getPano(o);
}

// ------------------------------------------------------------- mirar
let yaw = NAP.yaw0 || 0, pitch = 0;
const raycaster = new THREE.Raycaster();
const pointer = new THREE.Vector2();
let dragging = false, px = 0, py = 0, moved = 0;

function look(dx, dy) {
  yaw -= dx * 0.0028;
  pitch = Math.max(-1.35, Math.min(1.35, pitch + dy * 0.0028));
}
canvas.addEventListener('pointerdown', e => {
  dragging = true; moved = 0; px = e.clientX; py = e.clientY;
  canvas.setPointerCapture(e.pointerId);
});
canvas.addEventListener('pointermove', e => {
  if (!dragging) return;
  moved += Math.abs(e.clientX - px) + Math.abs(e.clientY - py);
  look(e.clientX - px, e.clientY - py);
  px = e.clientX; py = e.clientY;
});
canvas.addEventListener('pointerup', e => {
  dragging = false;
  if (moved < 6) {           // fue un toque: ¿hotspot?
    pointer.x = (e.clientX / innerWidth) * 2 - 1;
    pointer.y = -(e.clientY / innerHeight) * 2 + 1;
    raycaster.setFromCamera(pointer, camera);
    const hit = raycaster.intersectObjects(hotGroup.children, false)[0];
    if (hit) goTo(hit.object.userData.target);
  }
});
addEventListener('wheel', e => {
  camera.fov = Math.max(38, Math.min(85, camera.fov + e.deltaY * 0.02));
  camera.updateProjectionMatrix();
}, { passive: true });

// WASD / flechas: ir al nodo mas alineado con la vista
addEventListener('keydown', e => {
  const map = { KeyW: 1, ArrowUp: 1, KeyS: -1, ArrowDown: -1 };
  const s = map[e.code];
  if (!s || moving || !current) return;
  e.preventDefault();
  const vd = new THREE.Vector3();
  camera.getWorldDirection(vd);
  let best = null, bestDot = 0.35;
  for (const o of LINKS[current]) {
    const { v } = dirTo(current, o);
    const d = v.clone().setY(0).normalize().dot(
      new THREE.Vector3(vd.x, 0, vd.z).normalize()) * s;
    if (d > bestDot) { bestDot = d; best = o; }
  }
  if (best) goTo(best);
});

document.getElementById('enter').addEventListener('click', () => {
  document.getElementById('start').style.display = 'none';
});

function resize() {
  renderer.setSize(innerWidth, innerHeight, false);
  camera.aspect = innerWidth / innerHeight;
  camera.updateProjectionMatrix();
}
addEventListener('resize', resize);
resize();

function tick() {
  const cp = Math.cos(pitch);
  camera.lookAt(Math.sin(yaw) * cp, Math.sin(pitch), -Math.cos(yaw) * cp);
  // los anillos laten suavemente
  const s = 1 + 0.06 * Math.sin(performance.now() * 0.004);
  hotGroup.children.forEach(h => h.scale.setScalar(s));
  renderer.render(scene, camera);
  requestAnimationFrame(tick);
}
goTo(NAP.start, true).then(() => {
  front.material.opacity = 1;
});
tick();
