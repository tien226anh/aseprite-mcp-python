```
                    ┌─────────────────────┐
                    │  Asset Design        │
                    │  Orchestrator        │──── delegates to all 8
                    └────────┬────────────┘
                             │
        ┌────────┬───────────┼───────────┬────────┐
        ▼        ▼           ▼           ▼        ▼
  ┌──────────┐ ┌────────┐ ┌─────┐ ┌──────────┐ ┌──────┐
  │Character │ │  Tile  │ │ VFX │ │Background│ │ Item │
  │ Designer │ │Designer│ │Des. │ │ Designer │ │Des.  │
  └────┬─────┘ └───┬────┘ └──┬──┘ └────┬─────┘ └──┬───┘
       │            │         │         │          │
       └────────────┴────┬────┴─────────┴──────────┘
                         │
                    ┌────▼─────┐
                    │ Animator  │  (adds animation to completed sprites)
                    └────┬─────┘
                         │
                    ┌────▼─────┐
                    │  Asset    │  (reviews AND fixes)
                    │ Reviewer  │
                    └────┬─────┘
                         │
                    ┌────▼─────┐
                    │  Asset   │  (exports, packages)
                    │ Exporter │
                    └──────────┘
```
