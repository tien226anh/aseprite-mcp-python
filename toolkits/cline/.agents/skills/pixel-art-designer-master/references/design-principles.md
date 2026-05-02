# Pixel Art Design Principles

## Core Principles

### 1. Readability Over Detail
Every pixel must earn its place. At small sizes, a single pixel can be an eye, a belt buckle, or a window. If removing a pixel doesn't lose information, remove it.

### 2. Limited Palette
- **8-16 colors** for small sprites (16×16 and below)
- **16-32 colors** for detailed work (32×32 and above)
- Always include: near-black, near-white, and 3 values per hue (highlight, midtone, shadow)
- Hue-shifting: shadows shift cool (blue/purple), highlights shift warm (yellow/orange)

### 3. Consistent Light Source
Pick a light direction (usually top-left or top-center) and stick with it across the entire asset. Every shadow and highlight must respect this.

### 4. Silhouette First
If the asset reads as its intended shape when filled with a single solid color, the design is strong. Test by filling the outline layer with one color and squinting.

### 5. Banding Avoidance
Avoid "pixel banding" — parallel lines of identical pixels that create a blurry, soft look. Break bands with color variation or pixel offsets.

### 6. Anti-Aliasing Sparingly
Pixel art uses hard edges by default. Only anti-alias (blend edge pixels) for curves that need it, and only 1 pixel of transition.

### 7. Outlines Define Form
Use darker outlines to separate the asset from the background. Consider:
- **Full outline**: Every edge has a dark border (classic style)
- **Partial outline**: Only key edges outlined (selective style)
- **No outline**: Shape defined by color contrast alone (modern style)

## Color Theory for Pixel Art

### Hue Shifting
Don't just darken a color for shadows — shift the hue:
- **Shadows**: Shift toward blue/purple (cooler)
- **Highlights**: Shift toward yellow/orange (warmer)
- Example: A red object uses orange-red highlights and purple-red shadows

### Saturation in Shadows
- Deep shadows: Desaturate slightly (add gray)
- Midtones: Full saturation
- Highlights: Slightly desaturated (specular is near-white)

### Palette Swatches
Build palettes in rows of 3-5: each row is one hue from shadow to highlight:
```
Shadow    Midtone   Highlight
#333c57   #3b5dc9   #41a6f6    (blue row)
#5d275d   #b13e53   #ef7d57    (red row)
#257179   #38b764   #a7f070    (green row)
```

## Animation Design Principles

### 1. Keyframes First
Draw the most extreme poses first, then fill inbetweens.

### 2. Animate on Twos
Hold each drawing for 2 frames (~120ms at 60fps). This is the standard for 2D animation.

### 3. Anticipation and Follow-Through
- Before an action: small movement in the opposite direction (anticipation)
- After an action: small overshoot that settles back (follow-through)

### 4. Squash and Stretch
Deform the shape slightly to convey weight and impact:
- Squash on landing/impact
- Stretch on launch/fast movement

### 5. Arcs
Natural motion follows curved paths, not straight lines. Use `tween_cel_positions_eased` with `smoothstep` for organic motion.

## Style Guides by Asset Type

| Asset | Outline Style | Palette Size | Animation Style |
|-------|-------------|-------------|----------------|
| Character | Full or partial | 12-16 | Keyframe + tween |
| Item | Partial or none | 6-10 | Float/spin cycle |
| Tile | None | 4-8 | Subtle or none |
| Background | None | 16-32 | Parallax drift |
| VFX | None | 4-8 | Expand + fade |
| Portrait | Partial | 20-32 | Subtle breathing |