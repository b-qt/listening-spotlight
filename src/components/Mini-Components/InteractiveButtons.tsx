import * as THREE from 'three';
import React, { useState } from 'react';
import { useCursor } from '@react-three/drei';

// Define the props our button component will accept.
// It needs the geometry, and we'll accept any other standard mesh props.
type InteractiveButtonProps = JSX.IntrinsicElements['mesh'] & {
  geometry: THREE.BufferGeometry;
};


// Define materials once to be reused.
const brassMaterial = <meshStandardMaterial color="#b08d57" metalness={0.8} roughness={0.4} />;
const brassHoverMaterial = <meshStandardMaterial color="#fff346" metalness={0.8} roughness={0.3} />;

export function InteractiveButton({ geometry, ...props }: InteractiveButtonProps) {
  // This component now manages its own hover state. It's self-contained.
  const [hovered, setHovered] = useState(false);
  useCursor(hovered); /* ->>> Set the 'hovered' based on the mouse position */

  return (
    <mesh
     
      {...props} // Pass down all props like name, castShadow, onClick, etc.
      geometry={geometry}
      // Use event handlers to update this component's local state.
      onPointerOver={(e) => {
        e.stopPropagation(); // Stop the event from bubbling up to parents
        setHovered(true);
      }}
      onPointerOut={() => setHovered(false)}
      position={hovered ? [0,-0.045, 0] : 0} /* Dynamically change position based on the local 'hovered' state. */
    >      
      {hovered ? brassHoverMaterial : brassMaterial} {/* Change material based on the local 'hovered' state. */}
    </mesh>
  );
}