# Prueba Mermaid — PCM sobre PCT

```mermaid
block-beta
  columns 10
  hMeta["NIVEL META ═══════════════════════════════════════════════════"]:10
  lGrande["PCM grande (sobre todo el PCT)"]:4 space:6
  space:3 lApr("lo aprendido"):4 space:3
  PLAN["PLANIFICAR<br/>objetivo general"]:2
  block:MC:6
    columns 3
    MON["MONITOREAR"] space CTRL["CONTROLAR"]
    space mLoop("↺") space
  end
  EVAL["EVALUAR<br/>¿se logró?"]:2
  space:3 cambio["↓ ↑ (en cada cambio de FT)"]:4 space:3
  space:2 lChicos["PCM chicos (uno por FT)"]:4 space:4
  block:C1:2
    columns 2
    block:CI1:2
      columns 1
      ct1["P→[M⇄C]→E"]
    end
    cd1[" "] cu1[" "]
  end
  block:C2:2
    columns 2
    block:CI2:2
      columns 1
      ct2["P→[M⇄C]→E"]
    end
    cd2[" "] cu2[" "]
  end
  block:C3:2
    columns 2
    block:CI3:2
      columns 1
      ct3["P→[M⇄C]→E"]
    end
    cd3[" "] cu3[" "]
  end
  block:C4:2
    columns 2
    block:CI4:2
      columns 1
      ct4["P→[M⇄C]→E"]
    end
    cd4[" "] cu4[" "]
  end
  block:C5:2
    columns 2
    block:CI5:2
      columns 1
      ct5["P→[M⇄C]→E"]
    end
    cd5[" "] cu5[" "]
  end
  hObj["NIVEL OBJETO ══════════════════════════════════════════════════"]:10
  block:F1:2
    columns 2
    fd1[" "] fu1[" "]
    block:FI1:2
      columns 1
      ft1["EXPLORAR"]
    end
  end
  block:F2:2
    columns 2
    fd2[" "] fu2[" "]
    block:FI2:2
      columns 1
      ft2["CREAR"]
    end
  end
  block:F3:2
    columns 2
    fd3[" "] fu3[" "]
    block:FI3:2
      columns 1
      ft3["DECIDIR"]
    end
  end
  block:F4:2
    columns 2
    fd4[" "] fu4[" "]
    block:FI4:2
      columns 1
      ft4["IMPLEMENTAR"]
    end
  end
  block:F5:2
    columns 2
    fd5[" "] fu5[" "]
    block:FI5:2
      columns 1
      ft5["VERIFICAR"]
    end
  end
  lPCT["PCT"] space:2 rTxt("volver a una FT anterior"):3 space:4

  PLAN --> MON
  MON --> CTRL
  CTRL --> EVAL
  CTRL --- mLoop
  mLoop --> MON
  EVAL --- lApr
  lApr --> PLAN
  PLAN --> ct1
  ct5 --> EVAL
  cd1 --> fd1
  fu1 --> cu1
  cd2 --> fd2
  fu2 --> cu2
  cd3 --> fd3
  fu3 --> cu3
  cd4 --> fd4
  fu4 --> cu4
  cd5 --> fd5
  fu5 --> cu5
  ft1 --> ft2
  ft2 --> ft3
  ft3 --> ft4
  ft4 --> ft5
  ft3 --- rTxt
  rTxt --> ft1

  classDef txt fill:none,stroke:none
  classDef box fill:#ECECFF,stroke:#9370DB
  class hMeta,hObj,lGrande,cambio,lChicos,lPCT,ct1,ct2,ct3,ct4,ct5,cd1,cd2,cd3,cd4,cd5,cu1,cu2,cu3,cu4,cu5,fd1,fd2,fd3,fd4,fd5,fu1,fu2,fu3,fu4,fu5,ft1,ft2,ft3,ft4,ft5 txt
  classDef fb fill:#fff,stroke:#666,stroke-dasharray:4 3
  class lApr,rTxt,mLoop fb
  class CI1,CI2,CI3,CI4,CI5 txt
  class FI1,FI2,FI3,FI4,FI5 txt
  class C1,C2,C3,C4,C5,F1,F2,F3,F4,F5,MC box
```

▼ control (baja ajustes) · ▲ monitoreo (sube información)

- PCM = proceso cíclico metacognitivo
- PCT = proceso cíclico de trabajo
- FT = fase del proceso cíclico de trabajo
- P = planificar · M = monitorear · C = controlar · E = evaluar
