import React, { useState, useRef, useEffect } from "react";
import { useFrame } from "@react-three/fiber";
import { OrbitControls, useGLTF } from "@react-three/drei";
import * as THREE from "three";


// --- The Spinning Component ---
// This component now handles its own click logic internally for simplicity.
function PhysicsSpinner() {
    const meshRef = useRef();
    const [isSpinning, setIsSpinning] = useState(false);
    const [finalRotation, setFinalRotation] = useState(0);
    const spinStartTime = useRef(0);
    const initialRotation = useRef(0);
    const spinDuration = useRef(0);

    const { nodes } = useGLTF('../../Model.glb')

    const startSpin = () => {
        if (isSpinning) return;
        const fullRotations = 3 + Math.floor(Math.random() * 5);
        const totalRotation = fullRotations * Math.PI * 2;
        setFinalRotation(totalRotation);
        setIsSpinning(true);
    };

    useEffect(() => {
        if (isSpinning && meshRef.current) {
            spinStartTime.current = Date.now();
            initialRotation.current = meshRef.current.rotation.y;
            const rotations = finalRotation / (Math.PI * 2);
            spinDuration.current = Math.min(2 + rotations * 0.3, 5);
        }
    }, [isSpinning, finalRotation]);

    useFrame((state, delta) => {
        if (!meshRef.current || !isSpinning) return;

        const elapsed = (Date.now() - spinStartTime.current) / 1000;
        const progress = Math.min(elapsed / spinDuration.current, 1);

        if (progress < 1) {
            let angularVelocity;
            if (progress < 0.3) {
                angularVelocity = THREE.MathUtils.lerp(0, 25, progress / 0.3);
            } else {
                angularVelocity = THREE.MathUtils.lerp(25, 0, (progress - 0.3) / 0.7);
            }
            meshRef.current.rotateY(angularVelocity * delta);
        } else {
            meshRef.current.rotation.y = initialRotation.current + finalRotation;
            setIsSpinning(false);
            spinStartTime.current = 0;
        }
    });

    return (
        <group onClick={startSpin} >
            {/* 
            <mesh
                ref={meshRef}
                name="Disk1"
                castShadow
                receiveShadow
                geometry={nodes.Disk1.geometry} // Use the geometry passed down from the parent
            >
                <meshStandardMaterial color="#1a1a1a" roughness={0.3} />
            </mesh> */}

            <mesh
                ref={meshRef}
                name="Disk1"
                castShadow
                rotation={[Math.PI / 12, 0, 0]}
                position={[-0.5, 0.5, 0]}
                scale={1.95}
            >
                <cylinderGeometry args={[0.6, 0.6, 0.04, 18]} /> {/* args: [radiusTop, radiusBottom, height, segments] */}
                <meshStandardMaterial color="#1a1a1a" metalness={0.2} roughness={0.3} wireframe={false} />

                {/* The "Hole" - a smaller, darker cylinder placed slightly on top */}
                <mesh position={[0, 0.021, 0]}> {/* Position it just above the surface */}
                    <cylinderGeometry args={[0.1, 0.1, 0.01, 18]} />
                    <meshStandardMaterial color="silver" />
                </mesh>
            </mesh>

        </group>
    );
}

// --- The Main Exported Component ---
// NOTICE: It no longer returns a <Canvas>. It returns a fragment of 3D objects.
export function Model_Debug() {
    return (
        <>
            {/* Basic lighting for realism */}
            <ambientLight intensity={0.5} />
            <directionalLight position={[5, 5, 5]} intensity={1.5} castShadow />

            {/* Our self-contained spinner component */}
            <PhysicsSpinner />

            {/* A simple ground plane to receive shadows */}
            <mesh rotation={[-Math.PI / 2, 0, 0]} position={[0, -0.5, 0]} receiveShadow>
                <planeGeometry args={[10, 10]} />
                <meshStandardMaterial color="#dddddd" />
            </mesh>

            <OrbitControls />
        </>
    );
}