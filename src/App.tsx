import React, { Suspense } from 'react';
import { Canvas } from '@react-three/fiber';
import { OrbitControls, Stage } from '@react-three/drei';

// import { Model_Debug as Model } from './components/Model_Debug';
import { Model } from './components/Model.tsx';
import { SessionSummary } from './Data/SessionSummary.tsx';

import './App.css'

function App() {

  return (
    <div className="app-container">

      <div className="canvas-container">
        <Canvas
          camera={{
            position: [-8, 8, 12], // X=0, Y=8 (up), Z=8 (back)
            fov: 60,               // Field of View, like a camera lens. 50 is a good standard.
            near: 1,
            far: 70,
          }}
          shadows
          dpr={window.devicePixelRatio} // Sets pixel ratio  
        >
          <fog attach="fog" args={['#e6d9b2', 3, 60]} />
          <ambientLight intensity={0.5} /> 
          {/* <directionalLight position={[10, 15, 5]} intensity={1} /> */}
          <directionalLight
            castShadow
            position={[12, 10, 3]} // Position the light
            intensity={2.5}
            shadow-mapSize-width={1024} // Higher resolution shadows
            shadow-mapSize-height={1024}
          />

          {/* --- GROUND PLANE --- */}
          {/* We need a surface for the shadows to fall onto. */}
          <mesh rotation={[-Math.PI / 2, 0, 0]} position={[0, -4.5, 0]} receiveShadow>
            <planeGeometry args={[40, 20]} />
            <meshStandardMaterial color="#b79d4f" roughness={1} />
          </mesh>

          <Suspense fallback={null}>
            <Stage environment="city" intensity={0.6} shadows={false}>
              <Model position={[0, 0, 0]} />
            </Stage>
            {/* <OrbitControls autoRotate autoRotateSpeed={0.025} enableZoom={false} /> */}
            <OrbitControls
              minPolarAngle={-Math.PI / 2}
              maxPolarAngle={Math.PI / 2}
              enableZoom={false} // Note the prop name change from noZoom
              enablePan={false}  // Note the prop name change from noPan
            />
          </Suspense>
        </Canvas>
      </div>

      {/* The UI layer sits on top of the canvas */}
      <SessionSummary/>
      <div className="ui-layer">
        <h1 className="headline-round">My Listening History</h1>

        <div className="credits">
          <div className="text">music streaming summary</div>
          <div className="divider">|</div>
          <div className="text">tool stack</div>
        </div>

        
      </div>

    </div>

  );

}

export default App;