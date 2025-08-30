import React, { useEffect, useMemo, useRef, useState } from "react";
import { Canvas, useFrame, useThree } from "@react-three/fiber";
import { OrbitControls, Html } from "@react-three/drei";
import { EffectComposer, Bloom, Noise, Vignette } from "@react-three/postprocessing";
import * as THREE from "three";
import styles from './Nebula.module.css'



/*
Main Nebula Element:
Rendering Pipeline:
 1. Three JS Canvas <Canvas/>
 2. Ligthing        <Lights/>
 3. Starfield.      <Starfield/>
 4. Trackcloud.     <Trackcloud/>
 5. Post Effects.   <PostFX>
*/

export default function Nebula({data = []}) {
    // Create boundary limits according to data. Cache using useMemo
    const bounds = useMemo(() => {
        if (!data.length) 
            return { center: new THREE.Vector3(0,0,0), radius: 10 };

        const box = new THREE.Box3();
        const v = new THREE.Vector3();
        data.forEach(p => box.expandByPoint(v.set(p.x,p.y,p.z)));
        const center = new THREE.Vector3();
        box.getCenter(center);
        const radius = box.getSize(new THREE.Vector3()).length() * 0.6 + 10;
        return { center, radius };
    }, [data]);

    return(
        <div className={styles.nebula}>
            <Canvas dpr={[1,2]} camera={{ position: [0,0,bounds.radius], fov: 60 }}>
                <color attach="background" args={["#02010a"]} />
                <Lights />
                <Starfield count={1500} />
                <group position={[-bounds.center.x,-bounds.center.y,-bounds.center.z]}>
                      <Trackcloud data={data} />
                </group>
                <OrbitControls enableDamping dampingFactor={0.08} zoomSpeed={0.6} rotateSpeed={0.6} />
                <PostFX />
            </Canvas>
        </div>
    );
}

/* Ambient light, plus two directional light assets */
function Lights() {
    return(
    <>
        <ambientLight intensity={0.4}/>
        <pointLight position={[10, 15, 10]} intensity={1.2} />
        <pointLight position={[-12, -10, -8]} intensity={0.6} />
    </>);
}

/* Apply Vignette and additional postFX to scene. 
    Checks for GL2 web rendering support
*/
function PostFX() {
    const { gl } = useThree();
    // Check if the browser supports WebGL2
    const isWebGL2 = (() => {
    try {
        // Try to get the rendering context from the WebGL renderer
        const ctx = gl.getContext?.();
        // Check if WebGL2RenderingContext exists in the browser
        const webgl2Available = typeof WebGL2RenderingContext !== "undefined";
        // Check if the context we got is actually a WebGL2 context
        const isContextWebGL2 = ctx instanceof WebGL2RenderingContext;
        // Return true only if both conditions are met
        return webgl2Available && isContextWebGL2;
    } catch {
        return false;
    }})();

    if (!isWebGL2) return null;
    return (
        <EffectComposer>
            <Bloom intensity={0.7} luminanceThreshold={0.1} luminanceSmoothing={0.2} />
            <Noise opacity={0.03} />
            <Vignette eskil={false} offset={0.25} darkness={0.7} />
        </EffectComposer>
    );

}
/*
 * Returns a background starfield element
 */
function Starfield({ count = 1500 }) {
  const ref = useRef();

  // Generate random spherical distribution of points
  const positions = useMemo(() => {
    const arr = new Float32Array(count * 3);
    for (let i = 0; i < count; i++) {
      const r = 150 * Math.cbrt(Math.random()); // Increased radius for visibility
      const theta = Math.random() * Math.PI * 2;
      const phi = Math.acos(2 * Math.random() - 1);
      arr[i * 3] = r * Math.sin(phi) * Math.cos(theta);
      arr[i * 3 + 1] = r * Math.sin(phi) * Math.sin(theta);
      arr[i * 3 + 2] = r * Math.cos(phi);
    }
    return arr;
  }, [count]);

  return (
    <points ref={ref}>
      <bufferGeometry>
        <bufferAttribute
          attach="attributes-position"
          array={positions}
          itemSize={3}
        />
      </bufferGeometry>
      <pointsMaterial
        size={1}
        sizeAttenuation
        transparent
        opacity={1}

        color="#ffffff"
      />
    </points>
  );
}


/**
 * 
 * @param {*} data
 * @returns Trackcloud ThreeJS Scene
 */

function Trackcloud({ data }) {
    const { positions, colors, count } = useNebulaAttributes(data);
    if (count === 0) return null;
    const pointsRef = useRef();
    // Slice the positions to create a snapshot to animate
    const basePositions = useMemo(() => positions.slice(), [positions]);

    // Animate
    useNebulaDrift(pointsRef, basePositions);

    // Memoize the Geometery to only re-render if data changes.
    const geometry = useMemo(() => {
    const g = new THREE.BufferGeometry();
    g.setAttribute("position", new THREE.BufferAttribute(positions, 3));
    g.setAttribute("color", new THREE.BufferAttribute(colors, 3));
    return g;
    }, [positions, colors]);

    return (
    <points ref={pointsRef} geometry={geometry}>
        <pointsMaterial
            map={createCircleTexture()}
            vertexColors
            size={0.1}
            sizeAttenuation
            opacity={0.9}
            depthWrite={false}
            alphaTest={0.5}
        />
    </points>
  );
}

/**
 * 
 * @param {*} pointsRef 
 * @param {*} basePositions 
 * @param {*} speed 
 * @description animates the Trackcloud nebula
 */

function useNebulaDrift(pointsRef, basePositions, speed = 1) {
  const t0 = useRef(Math.random() * 1000);
  useFrame(({ clock }) => {
    const points = pointsRef.current;
    if (!points || !basePositions) return;
    const pos = points.geometry.getAttribute("position");
    if (!pos) return;
    const time = clock.getElapsedTime() + t0.current;
    for (let i = 0; i < pos.count; i++) {
      pos.array[i * 3] = basePositions[i * 3] + 0.5 * Math.sin(time * 0.25 + i * 0.1) * speed;
      pos.array[i * 3 + 1] = basePositions[i * 3 + 1] + 0.5 * Math.cos(time * 0.2 + i * 0.07) * speed;
      pos.array[i * 3 + 2] = basePositions[i * 3 + 2] + 0.5 * Math.sin(time * 0.18 + i * 0.05) * speed;
    }
    pos.needsUpdate = true;
  });
}

/**
 * 
 * @param {*} data 
 * @returns {Array} XYZ positions
 * @returns {Array} of colors depending on cluster
 * @returns {Int} count of tracks
 */
function useNebulaAttributes(data) {
  return useMemo(() => {
    const n = data.length;
    const positions = new Float32Array(n * 3);
    const colors = new Float32Array(n * 3);
    const color = new THREE.Color();

    data.forEach((p, i) => {
      positions[i * 3] = p.x;
      positions[i * 3 + 1] = p.y;
      positions[i * 3 + 2] = p.z;
      // Color by cluster if available, fallback to hash of name
      const hue = typeof p.cluster === "number" ? (p.cluster % 10) / 10 : Math.random();
      const sat = 0.6;
      const light = 0.5;
      color.setHSL(hue, sat, light);
      colors[i * 3] = color.r;
      colors[i * 3 + 1] = color.g;
      colors[i * 3 + 2] = color.b;
    });

    return { positions, colors, count: n };
  }, [data]);
}

function createCircleTexture(color = '#ffffff', size = 128) {
  const canvas = document.createElement('canvas');
  canvas.width = canvas.height = size;
  const ctx = canvas.getContext('2d');

  const center = size / 2;
  const radius = size / 2;

  ctx.beginPath();
  ctx.arc(center, center, radius, 0, Math.PI * 2);
  ctx.closePath();
  ctx.fillStyle = color;
  ctx.fill();

  const texture = new THREE.Texture(canvas);
  texture.needsUpdate = true;
  return texture;
}