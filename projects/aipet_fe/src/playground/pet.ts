import { Scene } from "@babylonjs/core/scene";
import { MeshBuilder } from "@babylonjs/core/Meshes/meshBuilder";
import { PhysicsAggregate } from "@babylonjs/core/Physics/v2/physicsAggregate";
import { PhysicsShapeType } from "@babylonjs/core/Physics/";
import type { Mesh } from "@babylonjs/core/Meshes/mesh";
import { Vector3 } from "@babylonjs/core";
import { StandardMaterial } from "@babylonjs/core/Materials/standardMaterial";
import { Color3 } from "@babylonjs/core/Maths/math.color";
import { KeyboardEventTypes } from "@babylonjs/core/Events/keyboardEvents";
import { SpriteManager } from "@babylonjs/core/Sprites/spriteManager";
import { Sprite } from "@babylonjs/core/Sprites/sprite";

export interface PetNeeds {
  hungry: number;      // 0-100 (100 = very hungry)
  tiredness: number;   // 0-100 (100 = very tired)
  boredom: number;     // 0-100 (100 = very bored)
  toilet: number;      // 0-100 (100 = really needs to go)
}

export class Pet {
  private mesh: Mesh | null = null;
  private meshAggregate: PhysicsAggregate | null = null;
  private sprite: Sprite | null = null;
  private spriteManager: SpriteManager | null = null;
  private needs: PetNeeds;
  private name: string;

  constructor(private scene: Scene, name: string = "Pet", position: Vector3 = new Vector3(0, 2, 0)) {
    this.scene = scene;
    this.name = name;
    this.needs = {
      hungry: 50,
      tiredness: 30,
      boredom: 40,
      toilet: 20
    };
    
    this._createPet(position);
    this._startNeedsDecay();
    this._createKeyboardControls();
  }

  private _createPet(position: Vector3): void {
    // Create an invisible sphere for physics
    this.mesh = MeshBuilder.CreateSphere("petPhysics", { diameter: 1.5, segments: 32 }, this.scene);
    this.mesh.position = position;
    this.mesh.isVisible = false; // Make the mesh invisible

    // Add physics to the invisible sphere
    this.meshAggregate = new PhysicsAggregate(
      this.mesh, 
      PhysicsShapeType.SPHERE, 
      { mass: 0.5, restitution: 0.6 }, 
      this.scene
    );

    // Create sprite manager and sprite
    this.spriteManager = new SpriteManager("petSpriteManager", "/public/texture/player.png", 1, { width: 64, height: 64 }, this.scene);
    this.sprite = new Sprite("petSprite", this.spriteManager);
    this.sprite.playAnimation(0, 40, true, 100);
    this.sprite.position = position;
    this.sprite.width = 1.5;
    this.sprite.height = 1.5;
    
    // Update sprite position to follow physics body
    this.scene.registerBeforeRender(() => {
      if (this.mesh && this.sprite) {
        this.sprite.position = this.mesh.position;
      }
    });
  }

  private _startNeedsDecay(): void {
    // Simulate pet needs increasing over time
    setInterval(() => {
      this.needs.hungry = Math.min(100, this.needs.hungry + 0.5);
      this.needs.tiredness = Math.min(100, this.needs.tiredness + 0.3);
      this.needs.boredom = Math.min(100, this.needs.boredom + 0.4);
      this.needs.toilet = Math.min(100, this.needs.toilet + 0.2);
      
      this._updatePetAppearance();
      this._updateStatusDisplay();
    }, 1000); // Update every second
  }

  private _updatePetAppearance(): void {
    if (!this.mesh || !this.mesh.material) return;

    const material = this.mesh.material as StandardMaterial;
    
    // Change color based on needs - redder when needs are higher
    const needsAverage = (this.needs.hungry + this.needs.tiredness + this.needs.boredom + this.needs.toilet) / 4;
    const intensity = needsAverage / 100;
    
    material.diffuseColor = new Color3(
      0.8 + (intensity * 0.2), // More red when needs are high
      0.6 - (intensity * 0.3), // Less green when needs are high
      0.4 - (intensity * 0.3)  // Less blue when needs are high
    );
  }

  private _updateStatusDisplay(): void {
    // Create or update a status display element
    let statusDiv = document.getElementById("pet-status");
    if (!statusDiv) {
      statusDiv = document.createElement("div");
      statusDiv.id = "pet-status";
      statusDiv.style.position = "absolute";
      statusDiv.style.top = "10px";
      statusDiv.style.left = "10px";
      statusDiv.style.backgroundColor = "rgba(0, 0, 0, 0.7)";
      statusDiv.style.color = "white";
      statusDiv.style.padding = "10px";
      statusDiv.style.borderRadius = "5px";
      statusDiv.style.fontFamily = "Arial, sans-serif";
      statusDiv.style.fontSize = "14px";
      statusDiv.style.zIndex = "1000";
      document.body.appendChild(statusDiv);
    }

    const urgentNeed = this.getMostUrgentNeed();
    statusDiv.innerHTML = `
      <strong>${this.name} Status:</strong><br/>
      🍔 Hungry: ${this.needs.hungry.toFixed(1)}<br/>
      😴 Tired: ${this.needs.tiredness.toFixed(1)}<br/>
      😑 Bored: ${this.needs.boredom.toFixed(1)}<br/>
      🚽 Toilet: ${this.needs.toilet.toFixed(1)}<br/>
      <br/>
      <strong>Most Urgent:</strong> ${urgentNeed.need} (${urgentNeed.value.toFixed(1)})<br/>
      <br/>
      <strong>Controls:</strong><br/>
      F - Feed | P - Play | Z - Sleep | T - Toilet
    `;
  }

  // Methods to satisfy pet needs
  public feed(): void {
    this.needs.hungry = Math.max(0, this.needs.hungry - 30);
    console.log(`${this.name} has been fed! Hunger: ${this.needs.hungry}`);
  }

  public sleep(): void {
    this.needs.tiredness = Math.max(0, this.needs.tiredness - 40);
    console.log(`${this.name} has slept! Tiredness: ${this.needs.tiredness}`);
  }

  public play(): void {
    this.needs.boredom = Math.max(0, this.needs.boredom - 35);
    // Playing also increases tiredness slightly
    this.needs.tiredness = Math.min(100, this.needs.tiredness + 10);
    console.log(`${this.name} has played! Boredom: ${this.needs.boredom}, Tiredness: ${this.needs.tiredness}`);
  }

  public toilet(): void {
    this.needs.toilet = Math.max(0, this.needs.toilet - 50);
    console.log(`${this.name} used the toilet! Toilet need: ${this.needs.toilet}`);
  }

  // Getters
  public getName(): string {
    return this.name;
  }

  public getNeeds(): PetNeeds {
    return { ...this.needs };
  }

  public getMesh(): Mesh | null {
    return this.mesh;
  }

  public getPhysicsBody(): PhysicsAggregate | null {
    return this.meshAggregate;
  }

  // Method to get the most urgent need
  public getMostUrgentNeed(): { need: keyof PetNeeds; value: number } {
    const needs = this.getNeeds();
    let maxNeed: keyof PetNeeds = 'hungry';
    let maxValue = needs.hungry;

    for (const [need, value] of Object.entries(needs) as [keyof PetNeeds, number][]) {
      if (value > maxValue) {
        maxNeed = need;
        maxValue = value;
      }
    }

    return { need: maxNeed, value: maxValue };
  }

  private _createKeyboardControls(): void {
    this.scene.onKeyboardObservable.add((kbInfo) => {
      switch (kbInfo.type) {
        case KeyboardEventTypes.KEYDOWN:
          switch (kbInfo.event.key) {
            case "a":
            case "A":
              if (this.meshAggregate) {
                this.meshAggregate.body.applyImpulse(new Vector3(1, 0, 0), this.mesh!.position);
              }
            break
            case "d":
            case "D":
              if (this.meshAggregate) {
                this.meshAggregate.body.applyImpulse(new Vector3(-1, 0, 0), this.mesh!.position);
              }
            break
            case "w":
            case "W":
              if (this.meshAggregate) {
                this.meshAggregate.body.applyImpulse(new Vector3(0, 0, -1), this.mesh!.position);
              }
            break
            case "s":
            case "S":
              if (this.meshAggregate) {
                this.meshAggregate.body.applyImpulse(new Vector3(0, 0, 1), this.mesh!.position);
              }
            break
            // Pet interaction controls
            case "f":
            case "F":
              this.feed();
            break
            case "t":
            case "T":
              this.toilet();
            break
            case "p":
            case "P":
              this.play();
            break
            case "z":
            case "Z":
              this.sleep();
            break
        }
        break;
      }
    });
  }

  // Cleanup method
  public dispose(): void {
    if (this.mesh) {
      this.mesh.dispose();
    }
    if (this.meshAggregate) {
      this.meshAggregate.dispose();
    }
    
    // Remove status display
    const statusDiv = document.getElementById("pet-status");
    if (statusDiv) {
      statusDiv.remove();
    }
  }
}