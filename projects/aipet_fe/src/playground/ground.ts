import { KeyboardEventTypes } from "@babylonjs/core/Events/keyboardEvents";
import { Scene } from "@babylonjs/core/scene";
import { MeshBuilder } from "@babylonjs/core/Meshes/meshBuilder";
import { PhysicsAggregate } from "@babylonjs/core/Physics/v2/physicsAggregate";
import { PhysicsShapeType } from "@babylonjs/core/Physics/";
import type { Mesh } from "@babylonjs/core/Meshes/mesh";
import { Vector3, SpriteManager, Sprite } from "@babylonjs/core";

export class Ground {
  private mesh: Mesh | null = null;
  private meshAggregate: PhysicsAggregate | null = null;
  private spriteManagerPlayer: SpriteManager | null = null;
  private aipet: Sprite | null = null;

  constructor(private scene: Scene) {
    this.scene = scene;
    this.mesh = null;
    this._createGround();
    this._createSphere();
    this._createKeyboardControls();
    this._createAIPet();
  }

  _createGround(): void {
    const mesh = MeshBuilder.CreateGround("ground", { width: 10, height: 10 }, this.scene);
    new PhysicsAggregate(mesh, PhysicsShapeType.BOX, { mass: 0 }, this.scene);
  }

  _createSphere(): void {
    this.mesh = MeshBuilder.CreateSphere("sphere", { diameter: 2, segments: 32 }, this.scene);
    this.mesh.position.y = 4;

    this.meshAggregate = new PhysicsAggregate(this.mesh, PhysicsShapeType.SPHERE, { mass: 1, restitution: 0.75 }, this.scene);
    // this.meshAggregate.bodsy.disablePreStep = false;
  }

  _createAIPet(): void {
    // Create a sprite manager
    this.spriteManagerPlayer = new SpriteManager("playerManager", "texture/player.png", 3, 64, this.scene);
    this.aipet = new Sprite("aipet", this.spriteManagerPlayer);
    this.aipet.playAnimation(0, 40, true, 100);
  }

  _createKeyboardControls(): void {
    this.scene.onKeyboardObservable.add((kbInfo) => {
      if (!this.mesh || !this.meshAggregate) return;

      switch (kbInfo.type) {
        case KeyboardEventTypes.KEYDOWN:
          switch (kbInfo.event.key) {
            case "a":
            case "A":
              this.meshAggregate.body.applyImpulse(new Vector3(1, 0, 0), this.mesh.position);
            break
            case "d":
            case "D":
              this.meshAggregate.body.applyImpulse(new Vector3(-1, 0, 0), this.mesh.position);
            break
            case "w":
            case "W":
              this.meshAggregate.body.applyImpulse(new Vector3(0, 0, -1), this.mesh.position);
            break
            case "s":
            case "S":
              this.meshAggregate.body.applyImpulse(new Vector3(0, 0, 1), this.mesh.position);
            break
        }
        break;
      }
    });
  }
}
