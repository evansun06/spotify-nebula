import React, { useEffect, useMemo, useRef, useState } from "react";
import { Instances, Instance, useTexture} from "@react-three/drei";
import { Canvas, useFrame, useThree, extend } from "@react-three/fiber";
import { OrbitControls, Html } from "@react-three/drei";
import { EffectComposer, Bloom, Noise, Vignette } from "@react-three/postprocessing";
import { ConvexGeometry } from "three/examples/jsm/geometries/ConvexGeometry.js";
import { MarchingCubes } from "three/examples/jsm/objects/MarchingCubes.js";

import * as THREE from "three";
import styles from './Nebula.module.css'
import cloud from '../../../assets/cloud.png'




/*
Main Nebula Element:
Rendering Pipeline:
 1. Three JS Canvas <Canvas/>
 2. Ligthing        <Lights/>
 3. Starfield.      <Starfield/>
 4. Trackcloud.     <Trackcloud/>
 5. Post Effects.   <PostFX>
*/

export default function Nebula({ data = [], highlighted, setHighlighted}) {
  const bounds = useMemo(() => {
    if (!data.length)
      return { center: new THREE.Vector3(0, 0, 0), radius: 10 };

    const box = new THREE.Box3();
    const v = new THREE.Vector3();
    data.forEach(p => box.expandByPoint(v.set(p.x, p.y, p.z)));
    const center = new THREE.Vector3();
    box.getCenter(center);
    const radius = box.getSize(new THREE.Vector3()).length() * 0.6 + 10;
    return { center, radius };
  }, [data]);

  const handleClick = (point, index) => {
    setHighlighted(point.cluster)
    console.log("Clicked point:", point, "at index:", index);
    // You can also update state here to highlight, open info, etc.
  };
  return (
    <div className={styles.nebula}>
      <Canvas dpr={[1, 2]} camera={{ position: [0, 0, bounds.radius/3], fov: 60 }}>
        <color attach="background" args={["black"]} />
        <Lights />
        <group position={[-bounds.center.x, -bounds.center.y, -bounds.center.z]}>

          <NebulaMetaballs data={data}/>
          <TrackcloudPoints data={data} highlighted={highlighted} />
          <TrackcloudInstance data={data}  onPointClick={handleClick} />
          <Starfield count={1500} />
        </group>
        <OrbitControls 
            enableDamping 
            dampingFactor={0.08} 
            zoomSpeed={0.6} 
            rotateSpeed={0.6} 

            // 👇 makes the camera slowly orbit around center
            autoRotate={true}
            autoRotateSpeed={0.5}   // lower = slower

            // 👇 limit zoom distance
            minDistance={bounds.radius * 0.1}
            maxDistance={bounds.radius * 2}

            // 👇 limit vertical movement (up/down tilt)
            minPolarAngle={Math.PI / 3}   // 60°
            maxPolarAngle={Math.PI / 1.7} // ~105°

  />
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
function Starfield({count = 1500}) {
  const ref = useRef();

  // Generate random spherical distribution of points
  const positions = useMemo(() => {
  const arr = new Float32Array(count * 3);
  for (let i = 0; i < count; i++) {
    arr[i * 3]     = (Math.random() - 0.5) * 800;
    arr[i * 3 + 1] = (Math.random() - 0.5) * 800;
    arr[i * 3 + 2] = (Math.random() - 0.5) * 800;
  }
  return arr;
}, [count]);
  const geometry = useMemo(() => {
    const g = new THREE.BufferGeometry();
    g.setAttribute("position", new THREE.BufferAttribute(positions, 3));
    return g;
  }, []);

  return (
    <points ref={ref} geometry={geometry}>
      <pointsMaterial
        size={1}
        sizeAttenuation
        transparent
        opacity={1}
        map={createCircleTexture()}
        color="white"
      />
    </points>
  );
}


function TrackcloudInstance({ data, onPointClick }) {
  const [hoveredIndex, setHoveredIndex] = useState(null);

  return (
    <Instances
      limit={data.length}
      castShadow={false}
      receiveShadow={false}
      geometry={new THREE.SphereGeometry(0.1, 8, 8)}
      material={
        new THREE.MeshStandardMaterial({
          transparent: true,
          opacity: 0,
          depthWrite: false,
        })
      }
    >
      {data.map((p, i) => (
        <Instance
          key={i}
          position={[p.x, p.y, p.z]}
          scale={1}
          onClick={(e) => {
            e.stopPropagation();
            onPointClick?.(p, i);
          }}
          onPointerOver={(e) => {
            e.stopPropagation();
            setHoveredIndex(i);
          }}
          onPointerOut={(e) => {
            e.stopPropagation();
            setHoveredIndex(null);
          }}
        >
          {hoveredIndex === i && (
            <Html
                position={[0, 0.02, 0]}
                style={{
                    fontFamily: "Arial",
                    fontSize: "60px",
                    background: "transparent",
                    pointerEvents: "none",
                    whiteSpace: "nowrap",
                }}
                center
                distanceFactor={1}
                >
                {p.name}<br />by {p.artist}
            </Html>
          )}
        </Instance>
      ))}
    </Instances>
  );
}


function TrackcloudPoints({ data, highlighted}) {
  const { positions, colors, count } = useNebulaAttributes(data, highlighted);

  const pointsRef = useRef();
  const basePositions = useMemo(() => positions.slice(), [positions]);
  useNebulaDrift(pointsRef, basePositions);

  const geometry = useMemo(() => {
    const g = new THREE.BufferGeometry();
    g.setAttribute("position", new THREE.BufferAttribute(positions, 3));
    g.setAttribute("color", new THREE.BufferAttribute(colors, 3));
    return g;
  }, [positions, colors, highlighted]);

  if (count === 0) {
    return null;
  }

  useFrame(({ clock }) => {
  const t = clock.getElapsedTime();
  pointsRef.current.material.opacity = 1.1 + 0.2 * Math.sin(t * 2.0);
  });

  return (
    <points ref={pointsRef} geometry={geometry}>
      <pointsMaterial
        map={createStarTexture()}
        vertexColors
        size={0.3}
        sizeAttenuation
        opacity={0.9}
        depthWrite={false}
        alphaTest={0.5}
        blending={THREE.AdditiveBlending} // makes stars glow when overlapping
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

function useNebulaDrift(pointsRef, basePositions, speed = 0.1) {
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
function useNebulaAttributes(data, highlighted) {
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
      
      if (p.cluster === highlighted) {
        color.setHSL(0, 0, 1);
        
      }  else {
        const hue = typeof p.cluster === "number" ? (p.cluster % 10) / 10 : Math.random();
        const sat = 0.6;
        const light = 0.5;
        color.setHSL(hue, sat, light);
      } 
      
      colors[i * 3] = color.r;
      colors[i * 3 + 1] = color.g;
      colors[i * 3 + 2] = color.b;
    });

    return { positions, colors, count: n };
    }, [data, highlighted]);
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

function createStarTexture(size = 128) {
  const canvas = document.createElement('canvas');
  canvas.width = canvas.height = size;
  const ctx = canvas.getContext('2d');

  const center = size / 2;
  const gradient = ctx.createRadialGradient(center, center, 0, center, center, center);

  // white in the middle, fading to transparent
  gradient.addColorStop(0, "rgba(255,255,255,1)");
  gradient.addColorStop(0.2, "rgba(255,255,255,0.8)");
  gradient.addColorStop(1, "rgba(255,255,255,0)");

  ctx.fillStyle = gradient;
  ctx.fillRect(0, 0, size, size);

  const texture = new THREE.Texture(canvas);
  texture.needsUpdate = true;
  return texture;
}




extend({ MarchingCubes });

export function NebulaMetaballs({
  data,               // array of {x,y,z}
  resolution = 100,      // resolution of marching cubes grid
  strength = 1.2,       // influence of each metaball
  subtract = 12,        // iso level threshold
  radius = 3,           // radius of each metaball in the field
  opacity = 1,
}) {
  const meshRef = useRef();
  const texture = useTexture(cloud);

  const fieldSize = useMemo(() => 50, []);

  const marching = useMemo(() => {
    const mc = new MarchingCubes(
      resolution,
      new THREE.MeshStandardMaterial({
        map: texture,
        transparent: true,
        opacity,
        depthWrite: false,
        blending: THREE.AdditiveBlending,
        side: THREE.DoubleSide,
      }),
      true, // enable smooth shading
      true  // enable render geometry
    );
    mc.scale.set(fieldSize, fieldSize, fieldSize);
    mc.position.set(0, 0, 0);
    mc.enableUvs = false;
    mc.enableColors = false;
    return mc;
  }, [resolution, texture, opacity]);

  useFrame(() => {
    if (!marching) return;

    marching.reset();

    data.forEach((c) => {
      // normalize positions to marching cubes [0,resolution] grid
      const x = ((c.x + fieldSize / 2) / fieldSize) * resolution;
      const y = ((c.y + fieldSize / 2) / fieldSize) * resolution;
      const z = ((c.z + fieldSize / 2) / fieldSize) * resolution;

      marching.addBall(x, y, z, radius, strength);
    });

    marching.update();
  });

  return <primitive object={marching} ref={meshRef} />;
}