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
import { Need } from "./need";
import { apiClient } from "../api/client";

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
  private shadowMesh: Mesh | null = null;
  private needs: PetNeeds;
  private name: string;
  private needObjects: Need[] = [];
  private proximityThreshold: number = 3.0; // Distance threshold for need interaction

  constructor(
    private scene: Scene, 
    name: string = "Pet", 
    position: Vector3 = new Vector3(0, 2, 0),
    needObjects: Need[] = []
  ) {
    this.scene = scene;
    this.name = name;
    this.needObjects = needObjects;
    this.needs = {
      hungry: 50,
      tiredness: 30,
      boredom: 40,
      toilet: 20
    };
    
    this._createPet(position);
    this._startNeedsDecay();
    this._startPetThinking();
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
      PhysicsShapeType.BOX, 
      { mass: 0.5, restitution: 0.6, friction: 1}, 
      this.scene
    );

    // Create sprite manager and sprite
    this.spriteManager = new SpriteManager("petSpriteManager", "/public/texture/bunny.png", 1, { width: 32, height: 32 }, this.scene);
    this.sprite = new Sprite("petSprite", this.spriteManager);
    this.sprite.playAnimation(0, 4, true, 100);
    this.sprite.position = position;
    this.sprite.width = 1.5;
    this.sprite.height = 1.5;
    
    // Create shadow mesh and shadow generator
    this._createShadow();
    
    // Update sprite position to follow physics body
    this.scene.registerBeforeRender(() => {
      if (this.mesh && this.sprite) {
        this.sprite.position = this.mesh.position;
        // Update shadow position to follow the pet
        if (this.shadowMesh) {
          this.shadowMesh.position = new Vector3(this.mesh.position.x, 0.01, this.mesh.position.z);
        }
      }
    });
  }

  private _createShadow(): void {
    // Create a flat circle mesh for the shadow
    this.shadowMesh = MeshBuilder.CreateDisc("petShadow", { radius: 0.4, tessellation: 32 }, this.scene);
    this.shadowMesh.position = new Vector3(0, 0.01, 0); // Slightly above ground to avoid z-fighting
    this.shadowMesh.rotation.x = Math.PI / 2; // Rotate to lay flat on the ground
    
    // Create shadow material
    const shadowMaterial = new StandardMaterial("shadowMaterial", this.scene);
    shadowMaterial.diffuseColor = new Color3(0, 0, 0);
    shadowMaterial.alpha = 0.3; // Semi-transparent
    shadowMaterial.emissiveColor = new Color3(0, 0, 0);
    shadowMaterial.specularColor = new Color3(0, 0, 0);
    this.shadowMesh.material = shadowMaterial;
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

  private _startPetThinking(): void {
    setInterval(async () => {
      console.log(`${this.name} is thinking...`);
      
      try {
        // Get pet recommendations from the API
        const response = await apiClient.getPetRecommendations({
          hungry: this.needs.hungry,
          tiredness: this.needs.tiredness,
          boredom: this.needs.boredom,
          toilet: this.needs.toilet
        });
        
        if (response.data) {
          console.log(`${this.name} AI recommendation:`, response.data);
          console.log(`Action: ${response.data.action}`);
          console.log(`Reasoning: ${response.data.reasoning}`);
          console.log(`Priority: ${response.data.priority}`);
        } else if (response.error) {
          console.error(`Failed to get recommendations for ${this.name}:`, response.error);
        }
      } catch (error) {
        console.error(`Error getting pet recommendations for ${this.name}:`, error);
      }
    }, 30000);
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
    
    // Check what needs are nearby
    const nearbyNeeds = this.getNearbyNeeds();
    const nearbyText = nearbyNeeds.length > 0 
      ? nearbyNeeds.map(need => need.getName()).join(', ')
      : 'None';
    
    statusDiv.innerHTML = `
      <strong>${this.name} Status:</strong><br/>
      🍔 Hungry: ${this.needs.hungry.toFixed(1)}<br/>
      😴 Tired: ${this.needs.tiredness.toFixed(1)}<br/>
      😑 Bored: ${this.needs.boredom.toFixed(1)}<br/>
      🚽 Toilet: ${this.needs.toilet.toFixed(1)}<br/>
      <br/>
      <strong>Most Urgent:</strong> ${urgentNeed.need} (${urgentNeed.value.toFixed(1)})<br/>
      <strong>Nearby Needs:</strong> ${nearbyText}<br/>
      <strong>Proximity Range:</strong> ${this.proximityThreshold.toFixed(1)}m<br/>
      <br/>
      <strong>Controls:</strong><br/>
      WASD - Move | SPACE - Jump | F - Feed | P - Play | Z - Sleep | T - Toilet
    `;
  }

  private getNearbyNeeds(): Need[] {
    if (!this.mesh) return [];
    
    const petPosition = this.mesh.position;
    const nearby: Need[] = [];
    
    for (const need of this.needObjects) {
      const distance = Vector3.Distance(petPosition, need.getPosition());
      if (distance <= this.proximityThreshold) {
        nearby.push(need);
      }
    }
    
    return nearby;
  }

  // Methods to check proximity to needs
  private isNearNeed(needType: string): boolean {
    if (!this.mesh) return false;
    
    const petPosition = this.mesh.position;
    
    for (const need of this.needObjects) {
      const needName = need.getName().toLowerCase();
      if (needName.includes(needType.toLowerCase())) {
        const distance = Vector3.Distance(petPosition, need.getPosition());
        if (distance <= this.proximityThreshold) {
          return true;
        }
      }
    }
    return false;
  }

  private findClosestNeed(needType: string): Need | null {
    if (!this.mesh) return null;
    
    const petPosition = this.mesh.position;
    let closestNeed: Need | null = null;
    let closestDistance = Infinity;
    
    for (const need of this.needObjects) {
      const needName = need.getName().toLowerCase();
      if (needName.includes(needType.toLowerCase())) {
        const distance = Vector3.Distance(petPosition, need.getPosition());
        if (distance < closestDistance) {
          closestDistance = distance;
          closestNeed = need;
        }
      }
    }
    
    return closestNeed;
  }

  // Methods to satisfy pet needs
  public feed(): void {
    if (!this.isNearNeed('food')) {
      const closestFood = this.findClosestNeed('food');
      if (closestFood) {
        console.log(`${this.name} needs to go to the food! It's at position ${closestFood.getPosition()}`);
        return;
      } else {
        console.log(`${this.name} can't find any food nearby!`);
        return;
      }
    }
    
    this.needs.hungry = Math.max(0, this.needs.hungry - 30);
    console.log(`${this.name} has been fed! Hunger: ${this.needs.hungry}`);
  }

  public sleep(): void {
    if (!this.isNearNeed('sleep') && !this.isNearNeed('bed')) {
      const closestSleep = this.findClosestNeed('sleep') || this.findClosestNeed('bed');
      if (closestSleep) {
        console.log(`${this.name} needs to go to the sleep area! It's at position ${closestSleep.getPosition()}`);
        return;
      } else {
        console.log(`${this.name} can't find any sleep area nearby!`);
        return;
      }
    }
    
    this.needs.tiredness = Math.max(0, this.needs.tiredness - 40);
    console.log(`${this.name} has slept! Tiredness: ${this.needs.tiredness}`);
  }

  public play(): void {
    if (!this.isNearNeed('toy') && !this.isNearNeed('play')) {
      const closestToy = this.findClosestNeed('toy') || this.findClosestNeed('play');
      if (closestToy) {
        console.log(`${this.name} needs to go to the toy! It's at position ${closestToy.getPosition()}`);
        return;
      } else {
        console.log(`${this.name} can't find any toys nearby!`);
        return;
      }
    }
    
    this.needs.boredom = Math.max(0, this.needs.boredom - 35);
    // Playing also increases tiredness slightly
    this.needs.tiredness = Math.min(100, this.needs.tiredness + 10);
    console.log(`${this.name} has played! Boredom: ${this.needs.boredom}, Tiredness: ${this.needs.tiredness}`);
  }

  public toilet(): void {
    if (!this.isNearNeed('toilet') && !this.isNearNeed('bathroom')) {
      const closestToilet = this.findClosestNeed('toilet') || this.findClosestNeed('bathroom');
      if (closestToilet) {
        console.log(`${this.name} needs to go to the toilet! It's at position ${closestToilet.getPosition()}`);
        return;
      } else {
        console.log(`${this.name} can't find any toilet nearby!`);
        return;
      }
    }
    
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

  // Method to update the need objects
  public setNeedObjects(needObjects: Need[]): void {
    this.needObjects = needObjects;
  }

  // Method to get current need objects
  public getNeedObjects(): Need[] {
    return [...this.needObjects];
  }

  // Method to set proximity threshold
  public setProximityThreshold(threshold: number): void {
    this.proximityThreshold = threshold;
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
    // Track key states for simultaneous key presses
    const keyStates: { [key: string]: boolean } = {};
    
    this.scene.onKeyboardObservable.add((kbInfo) => {
      switch (kbInfo.type) {
        case KeyboardEventTypes.KEYDOWN:
          // Update key state
          keyStates[kbInfo.event.key.toLowerCase()] = true;
          
          // Handle movement keys with simultaneous press support
          if (this.meshAggregate) {
            let impulse = new Vector3(0, 0, 0);
            
            // Check all movement keys and combine their impulses
            if (keyStates['a']) {
              impulse.addInPlace(new Vector3(1, 0, 0));
            }
            if (keyStates['d']) {
              impulse.addInPlace(new Vector3(-1, 0, 0));
            }
            if (keyStates['w']) {
              impulse.addInPlace(new Vector3(0, 0, -1));
            }
            if (keyStates['s']) {
              impulse.addInPlace(new Vector3(0, 0, 1));
            }
            
            // Apply combined impulse if any movement keys are pressed
            if (!impulse.equals(Vector3.Zero())) {
              this.meshAggregate.body.applyImpulse(impulse, this.mesh!.position);
            }
          }
          
          // Handle single-press interaction controls
          switch (kbInfo.event.key) {
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
            case " ":
              // Jump movement on spacebar
              if (this.meshAggregate) {
                this.meshAggregate.body.applyImpulse(new Vector3(0, 4, 0), this.mesh!.position);
              }
            break
          }
        break;
        
        case KeyboardEventTypes.KEYUP:
          // Update key state when key is released
          keyStates[kbInfo.event.key.toLowerCase()] = false;
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
    if (this.shadowMesh) {
      this.shadowMesh.dispose();
    }
    
    // Remove status display
    const statusDiv = document.getElementById("pet-status");
    if (statusDiv) {
      statusDiv.remove();
    }
  }
}