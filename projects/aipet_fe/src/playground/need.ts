import { Scene } from "@babylonjs/core/scene";
import { MeshBuilder } from "@babylonjs/core/Meshes/meshBuilder";
import { PhysicsAggregate } from "@babylonjs/core/Physics/v2/physicsAggregate";
import { PhysicsShapeType } from "@babylonjs/core/Physics/";
import type { Mesh } from "@babylonjs/core/Meshes/mesh";
import { Vector3 } from "@babylonjs/core";
import { StandardMaterial } from "@babylonjs/core/Materials/standardMaterial";
import { Color3 } from "@babylonjs/core/Maths/math.color";

export interface NeedProperties {
  size: number;           // Size of the cube
  color: Color3;          // Color of the cube
  mass: number;           // Physics mass
  isStatic: boolean;      // Whether the cube is static (immovable)
  isVisible: boolean;     // Whether the cube is visible
  objectType?: string;    // Type of object (food, toy, bed, toilet, other)
}

export class Need {
  private mesh: Mesh | null = null;
  private meshAggregate: PhysicsAggregate | null = null;
  private material: StandardMaterial | null = null;
  private properties: NeedProperties;
  private name: string;

  constructor(
    private scene: Scene, 
    name: string = "Need", 
    position: Vector3 = new Vector3(0, 1, 0),
    properties: Partial<NeedProperties> = {}
  ) {
    this.scene = scene;
    this.name = name;
    
    // Set default properties
    this.properties = {
      size: 1,
      color: new Color3(0.5, 0.5, 0.5),
      mass: 1,
      isStatic: false,
      isVisible: true,
      ...properties
    };
    
    this._createNeed(position);
  }

  private _createNeed(position: Vector3): void {
    // Create cube mesh
    this.mesh = MeshBuilder.CreateBox(
      this.name, 
      { 
        size: this.properties.size,
        height: this.properties.size,
        width: this.properties.size,
        depth: this.properties.size
      }, 
      this.scene
    );
    
    this.mesh.position = position;
    this.mesh.isVisible = this.properties.isVisible;

    // Create material
    this.material = new StandardMaterial(`${this.name}Material`, this.scene);
    this.material.diffuseColor = this.properties.color;
    this.material.specularColor = new Color3(0.1, 0.1, 0.1);
    this.material.emissiveColor = new Color3(0, 0, 0);
    this.mesh.material = this.material;

    // Add physics if not static
    if (!this.properties.isStatic) {
      this.meshAggregate = new PhysicsAggregate(
        this.mesh, 
        PhysicsShapeType.BOX, 
        { 
          mass: this.properties.mass, 
          restitution: 0.3, 
          friction: 0.8
        }, 
        this.scene
      );
    }
  }

  // Methods to modify the need
  public setColor(color: Color3): void {
    this.properties.color = color;
    if (this.material) {
      this.material.diffuseColor = color;
    }
  }

  public setSize(size: number): void {
    this.properties.size = size;
    if (this.mesh) {
      this.mesh.scaling = new Vector3(size, size, size);
    }
  }

  public setPosition(position: Vector3): void {
    if (this.mesh) {
      this.mesh.position = position;
    }
  }

  public setMass(mass: number): void {
    this.properties.mass = mass;
    if (this.meshAggregate) {
      this.meshAggregate.body.setMassProperties({ mass });
    }
  }

  public setStatic(isStatic: boolean): void {
    this.properties.isStatic = isStatic;
    if (isStatic && this.meshAggregate) {
      this.meshAggregate.dispose();
      this.meshAggregate = null;
    } else if (!isStatic && !this.meshAggregate && this.mesh) {
      this.meshAggregate = new PhysicsAggregate(
        this.mesh, 
        PhysicsShapeType.BOX, 
        { 
          mass: this.properties.mass, 
          restitution: 0.3, 
          friction: 0.8
        }, 
        this.scene
      );
    }
  }

  public setVisible(isVisible: boolean): void {
    this.properties.isVisible = isVisible;
    if (this.mesh) {
      this.mesh.isVisible = isVisible;
    }
  }

  // Getters
  public getName(): string {
    return this.name;
  }

  public getProperties(): NeedProperties {
    return { ...this.properties };
  }

  public getMesh(): Mesh | null {
    return this.mesh;
  }

  public getPhysicsBody(): PhysicsAggregate | null {
    return this.meshAggregate;
  }

  public getPosition(): Vector3 {
    return this.mesh ? this.mesh.position : new Vector3(0, 0, 0);
  }

  public getMaterial(): StandardMaterial | null {
    return this.material;
  }

  public getObjectType(): string {
    return this.properties.objectType || "other";
  }

  // Utility methods
  public applyImpulse(impulse: Vector3, point?: Vector3): void {
    if (this.meshAggregate && this.mesh) {
      const impulsePoint = point || this.mesh.position;
      this.meshAggregate.body.applyImpulse(impulse, impulsePoint);
    }
  }

  public applyForce(force: Vector3, point?: Vector3): void {
    if (this.meshAggregate && this.mesh) {
      const forcePoint = point || this.mesh.position;
      this.meshAggregate.body.applyForce(force, forcePoint);
    }
  }

  public rotate(axis: Vector3, amount: number): void {
    if (this.mesh) {
      this.mesh.rotate(axis, amount);
    }
  }

  public scale(factor: Vector3): void {
    if (this.mesh) {
      this.mesh.scaling = factor;
    }
  }

  // Cleanup method
  public dispose(): void {
    if (this.mesh) {
      this.mesh.dispose();
    }
    if (this.meshAggregate) {
      this.meshAggregate.dispose();
    }
    if (this.material) {
      this.material.dispose();
    }
  }
} 