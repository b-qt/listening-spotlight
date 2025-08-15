import React, { useRef } from "react";
import * as THREE from "three";

// The component now accepts an `isSpinning` prop to control its state.
type InteractiveSpinnerProps = JSX.IntrinsicElements['group'] & {
  isSpinning: boolean;
};

export function InteractiveSpinner({ isSpinning, ...props }: InteractiveSpinnerProps) {
  const groupRef = useRef<THREE.Group>(null!);

  return (
    // The parent group is now just for positioning and holding the ref.
    <group ref={groupRef} {...props}>
      {/* The CD mesh is the visual part. */}
      <mesh castShadow receiveShadow>
        <cylinderGeometry args={[0.6, 0.6, 0.04, 24]} />
        <meshStandardMaterial color="#1a1a1a" metalness={0.2} roughness={0.3} />

        {/* The "Hole" is a child of the main CD mesh */}
        <mesh position={[0, 0.021, 0]}>
          <cylinderGeometry args={[0.1, 0.1, 0.01, 24]} />
          <meshStandardMaterial color="silver" />
        </mesh>
      </mesh>
    </group>
  );
}
