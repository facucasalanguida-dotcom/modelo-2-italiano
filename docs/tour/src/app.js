// Café Napoli — recorrido virtual en primera persona (planta baja)
import * as THREE from 'three';
import { RoomEnvironment } from 'three/examples/jsm/environments/RoomEnvironment.js';

const NAP = window.NAP;

// ------------------------------------------------------------- decodificar
const raw = atob(NAP.bin);
const bytes = new Uint8Array(raw.length);
for (let i = 0; i < raw.length; i++) bytes[i] = raw.charCodeAt(i);
const buf = bytes.buffer;
const dv = new DataView(buf);
const jlen = dv.getUint32(4, true);
const meta = JSON.parse(new TextDecoder().decode(new Uint8Array(buf, 8, jlen)));
const offsets = NAP.offsets;

// ------------------------------------------------------------- render base
const canvas = document.getElementById('c');
const renderer = new THREE.WebGLRenderer({ canvas, antialias: true });
renderer.setPixelRatio(Math.min(devicePixelRatio, 2));
renderer.toneMapping = THREE.ACESFilmicToneMapping;
renderer.toneMappingExposure = 1.06;
renderer.outputColorSpace = THREE.SRGBColorSpace;
renderer.shadowMap.enabled = true;
renderer.shadowMap.type = THREE.PCFSoftShadowMap;

const scene = new THREE.Scene();
scene.background = new THREE.Color(0xd3e4ef);
scene.fog = new THREE.Fog(0xd7e6ef, 45, 110);
// entorno PBR para reflejos y ambiente realistas
const pmrem = new THREE.PMREMGenerator(renderer);
scene.environment = pmrem.fromScene(new RoomEnvironment(), 0.04).texture;
scene.environmentIntensity = 0.4;

const camera = new THREE.PerspectiveCamera(66, 1, 0.05, 240);
camera.up.set(0, 0, 1);
scene.add(camera);

// ------------------------------------------------------------- texturas
const texLoader = new THREE.TextureLoader();
const texCache = {};
function getTex(name, uvmin, uvsize) {
  const key = name + '|' + uvmin + '|' + uvsize;
  if (texCache[key]) return texCache[key];
  const t = texLoader.load(NAP.tex[name]);
  t.colorSpace = THREE.SRGBColorSpace;
  t.wrapS = t.wrapT = THREE.RepeatWrapping;
  t.anisotropy = Math.min(8, renderer.capabilities.getMaxAnisotropy());
  t.offset.set(uvmin[0], uvmin[1]);
  t.repeat.set(uvsize[0], uvsize[1]);
  texCache[key] = t;
  return t;
}

// ------------------------------------------------------------- geometria
meta.mats.forEach((m, gi) => {
  const o = offsets[gi];
  const sp = m.spec;
  const g = new THREE.BufferGeometry();
  g.setAttribute('position', new THREE.BufferAttribute(
    new Uint16Array(buf, o.p, m.nv * 3), 3, true));
  g.setAttribute('normal', new THREE.BufferAttribute(
    new Int8Array(buf, o.n, m.nv * 3), 3, true));
  if (sp.tex) {
    g.setAttribute('uv', new THREE.BufferAttribute(
      new Uint16Array(buf, o.u, m.nv * 2), 2, true));
  }
  g.setIndex(new THREE.BufferAttribute(new Uint32Array(buf, o.i, m.ni), 1));
  g.boundingSphere = new THREE.Sphere(new THREE.Vector3(0.5, 0.5, 0.5), 0.9);

  const params = {
    color: new THREE.Color(sp.color[0], sp.color[1], sp.color[2]),
    roughness: Math.max(0.06, sp.rough),
    metalness: Math.min(0.92, sp.metal),
  };
  if (sp.tex && NAP.tex[sp.tex]) params.map = getTex(sp.tex, m.uvmin, m.uvsize);
  const mat = new THREE.MeshStandardMaterial(params);
  if (sp.alpha < 1) {
    mat.transparent = true;
    mat.opacity = sp.alpha < 0.1 ? 0.12 : sp.alpha;
    mat.depthWrite = false;
    mat.side = THREE.DoubleSide;
    mat.roughness = 0.05;
  }
  if (sp.emit) {
    mat.emissive = new THREE.Color(sp.emit[0], sp.emit[1], sp.emit[2]);
    mat.emissiveIntensity = Math.min(1.7, sp.emit[3] * 0.7);
  }
  const mesh = new THREE.Mesh(g, mat);
  mesh.position.set(m.pmin[0], m.pmin[1], m.pmin[2]);
  mesh.scale.set(m.psize[0], m.psize[1], m.psize[2]);
  mesh.castShadow = sp.alpha >= 1 && !sp.emit;
  mesh.receiveShadow = true;
  if (sp.alpha < 1) mesh.renderOrder = 4;
  scene.add(mesh);
});

// ------------------------------------------------------------- iluminacion
const hemi = new THREE.HemisphereLight(0xe8f0f6, 0x8a7a66, 0.55);
hemi.position.set(0, 0, 1);
scene.add(hemi);

// relleno calido en la doble altura de la entrada
const fill = new THREE.PointLight(0xfff0dc, 3.2, 10, 1.6);
fill.position.set(7.9, 1.9, 4.3);
scene.add(fill);

const sun = new THREE.DirectionalLight(0xfff0dc, 1.5);
sun.position.set(13, -17, 15);
sun.target.position.set(5, 4.5, 0);
sun.castShadow = true;
sun.shadow.mapSize.set(2048, 2048);
sun.shadow.camera.left = -13; sun.shadow.camera.right = 13;
sun.shadow.camera.top = 13; sun.shadow.camera.bottom = -13;
sun.shadow.camera.near = 2; sun.shadow.camera.far = 60;
sun.shadow.bias = -0.0004;
sun.shadow.normalBias = 0.025;
scene.add(sun); scene.add(sun.target);

const lampSorted = [...meta.lights].sort((a, b) => b[3] - a[3]).slice(0, 9);
for (const [lx, ly, lz] of lampSorted) {
  const pl = new THREE.PointLight(0xffd9a8, 5.5, 5.5, 1.8);
  pl.position.set(lx, ly, lz - 0.1);
  scene.add(pl);
}
for (const [kx, ky] of [[1.05, 7.75], [1.75, 8.35]]) {
  const pl = new THREE.PointLight(0xfff2e0, 4, 4.5, 1.8);
  pl.position.set(kx, ky, 2.3);
  scene.add(pl);
}

// ------------------------------------------------------------- jugador
const EYE = 1.60, R = 0.26;
const pos = new THREE.Vector2(meta.spawn[0], meta.spawn[1]);
let yaw = meta.spawn[2] * Math.PI / 180, pitch = -0.02;
const keys = {};
const cols = meta.cols, bounds = meta.bounds;

function blocked(x, y) {
  if (x < bounds[0] + R || y < bounds[1] + R ||
      x > bounds[2] - R || y > bounds[3] - R) return true;
  for (let i = 0; i < cols.length; i++) {
    const c = cols[i];
    const cx = Math.max(c[0], Math.min(x, c[2]));
    const cy = Math.max(c[1], Math.min(y, c[3]));
    const dx = x - cx, dy = y - cy;
    if (dx * dx + dy * dy < R * R) return true;
  }
  return false;
}

addEventListener('keydown', e => {
  keys[e.code] = true;
  if (['ArrowUp', 'ArrowDown', 'ArrowLeft', 'ArrowRight', 'Space'].includes(e.code))
    e.preventDefault();
});
addEventListener('keyup', e => { keys[e.code] = false; });

// raton: pointer lock con respaldo de arrastre
const overlay = document.getElementById('start');
let dragging = false, px = 0, py = 0;
function look(dx, dy) {
  yaw -= dx * 0.0023;
  pitch = Math.max(-1.45, Math.min(1.45, pitch - dy * 0.0023));
}
canvas.addEventListener('click', () => {
  if (document.pointerLockElement !== canvas && canvas.requestPointerLock)
    canvas.requestPointerLock();
});
document.addEventListener('pointerlockchange', () => {
  document.getElementById('hint').style.opacity =
    document.pointerLockElement === canvas ? 1 : 0.85;
});
addEventListener('mousemove', e => {
  if (document.pointerLockElement === canvas) look(e.movementX, e.movementY);
  else if (dragging) { look(e.clientX - px, e.clientY - py); px = e.clientX; py = e.clientY; }
});
canvas.addEventListener('mousedown', e => { dragging = true; px = e.clientX; py = e.clientY; });
addEventListener('mouseup', () => { dragging = false; });

// tactil: mitad izquierda mueve, mitad derecha mira
let moveTouch = null, lookTouch = null, moveVec = { x: 0, y: 0 };
canvas.addEventListener('touchstart', e => {
  for (const t of e.changedTouches) {
    if (t.clientX < innerWidth / 2 && moveTouch === null)
      moveTouch = { id: t.identifier, x: t.clientX, y: t.clientY };
    else if (lookTouch === null)
      lookTouch = { id: t.identifier, x: t.clientX, y: t.clientY };
  }
  e.preventDefault();
}, { passive: false });
canvas.addEventListener('touchmove', e => {
  for (const t of e.changedTouches) {
    if (moveTouch && t.identifier === moveTouch.id) {
      moveVec.x = (t.clientX - moveTouch.x) / 46;
      moveVec.y = (t.clientY - moveTouch.y) / 46;
    } else if (lookTouch && t.identifier === lookTouch.id) {
      look((t.clientX - lookTouch.x) * 2.2, (t.clientY - lookTouch.y) * 2.2);
      lookTouch.x = t.clientX; lookTouch.y = t.clientY;
    }
  }
  e.preventDefault();
}, { passive: false });
canvas.addEventListener('touchend', e => {
  for (const t of e.changedTouches) {
    if (moveTouch && t.identifier === moveTouch.id) { moveTouch = null; moveVec = { x: 0, y: 0 }; }
    if (lookTouch && t.identifier === lookTouch.id) lookTouch = null;
  }
}, { passive: false });

document.getElementById('enter').addEventListener('click', () => {
  overlay.style.display = 'none';
  if (canvas.requestPointerLock && matchMedia('(pointer:fine)').matches)
    canvas.requestPointerLock();
});

// ------------------------------------------------------------- bucle
function resize() {
  const w = innerWidth, h = innerHeight;
  renderer.setSize(w, h, false);
  camera.aspect = w / h;
  camera.updateProjectionMatrix();
}
addEventListener('resize', resize);
resize();

const clock = new THREE.Clock();
const dir = new THREE.Vector3();
function tick() {
  const dt = Math.min(clock.getDelta(), 0.05);
  const run = keys.ShiftLeft || keys.ShiftRight ? 2 : 1;
  const sp = 2.3 * run * dt;
  let f = 0, s = 0;
  if (keys.KeyW || keys.ArrowUp) f += 1;
  if (keys.KeyS || keys.ArrowDown) f -= 1;
  if (keys.KeyA || keys.ArrowLeft) s += 1;
  if (keys.KeyD || keys.ArrowRight) s -= 1;
  f += -moveVec.y; s += -moveVec.x;
  const cy = Math.cos(yaw), sy = Math.sin(yaw);
  const vx = (cy * f - sy * s) * sp;
  const vy = (sy * f + cy * s) * sp;
  if (vx || vy) {
    if (!blocked(pos.x + vx, pos.y)) pos.x += vx;
    if (!blocked(pos.x, pos.y + vy)) pos.y += vy;
  }
  camera.position.set(pos.x, pos.y, EYE);
  dir.set(Math.cos(pitch) * cy, Math.cos(pitch) * sy, Math.sin(pitch));
  camera.lookAt(pos.x + dir.x, pos.y + dir.y, EYE + dir.z);
  renderer.render(scene, camera);
  requestAnimationFrame(tick);
}
tick();
