# Visual product planning specification

Use this file when a product has mockups, screenshots, concept art, characters,
animation, rooms, physical composition, 2D/3D art, or UI presentation.

## Freeze reference precedence

For every source reference record:

- stable reference ID;
- absolute source path or canonical URL;
- source type and creator/provenance;
- dimensions, file size, and cryptographic hash;
- date received;
- priority: primary, secondary, inspiration-only, or rejected;
- properties it controls;
- properties it does not control;
- legal or reuse limitations.

If two references conflict, the higher-priority source wins only for the
properties assigned to it. Record user corrections as explicit decisions.

Never import a concept image as the product surface, trace its pixels, present
it as running evidence, or copy unlicensed assets. Reproduce approved
composition and mood with original implementation.

## Write a blind-person visual bible

Describe every screen, zone, object, character, UI element, effect, and state so
an implementer can reconstruct the intended result without seeing the image.

For each item define:

- stable ID and human name;
- semantic purpose and interaction role;
- parent zone and precise relative location;
- footprint, dimensions, scale, height, and orientation;
- silhouette and primary/secondary shapes;
- front, side, top, and occluded appearance where relevant;
- material or surface treatment;
- color palette, value range, saturation, and contrast role;
- light response, cast shadow, contact shadow, and emissive behavior;
- relationship to neighboring items and required negative space;
- visibility, occlusion, cutaway, and layering rules;
- interaction states and feedback;
- animation states, timing family, and transition constraints;
- accessibility and mobile readability requirements;
- placeholder quality allowed and the milestone that replaces it;
- required running-build evidence.

Use relative coordinates or anchors in addition to prose. Avoid vague phrases
such as "make it cozy," "polish it," or "match the mockup" without measurable
composition, palette, lighting, and density targets.

## Define composition and camera

For spatial products specify:

- target aspect ratios and safe areas;
- camera projection, position, rotation, field of view or orthographic size;
- whether the camera is fixed, pannable, draggable, or bounded;
- room/world bounds and how they fill the frame;
- subject focal hierarchy;
- foreground cutaway and occlusion strategy;
- acceptable off-screen extension;
- scale references for people, furniture, doors, and fixtures;
- black/empty-space prohibition or intentional background treatment;
- device-specific framing rules and screenshot comparison method.

If using a "2D look in a 3D space," define:

- real geometry and depth requirements;
- orthographic or perspective projection;
- hand-painted/albedo style;
- edge softness and shape language;
- simplified materials and controlled highlights;
- shadow/contact strategy;
- character rendering and facing method;
- which elements may use sprites, billboards, meshes, or hybrid techniques;
- proof that the world is not a flattened screenshot.

## Define registers instead of wish lists

Create stable registers for:

- room/world zones;
- fixtures and furniture;
- decorative props;
- UI elements and states;
- characters and customization parts;
- animations and ambient activities;
- VFX and lighting cues;
- audio cues when visual actions depend on them.

Every register entry needs an owner milestone and acceptance evidence. Validate
ID uniqueness mechanically.

## Plan animation as behavior

For living scenes define:

- base idle;
- secondary idle variations;
- activity locations and anchors;
- transition routes and path safety;
- look-at and reaction triggers;
- interaction pairs;
- cooldowns, weights, and repetition avoidance;
- interruption and save/load behavior;
- reduced-motion behavior;
- cat/pet/ambient creature states when applicable;
- simultaneous activity limits and mobile performance budget.

"Many idles" must become a counted catalog with named states and transitions.

## Plan customization inclusively

When users create people, households, avatars, or relationships:

- separate body, presentation, identity, pronouns, voice, role, and
  relationship data where the product needs them;
- do not encode heterosexual or binary assumptions in pairing logic;
- define broad combinations without labeling one as default-normal;
- verify UI copy, animations, save data, thumbnails, and activities work for
  every supported pairing;
- define representative test matrices without treating identity as a visual
  stereotype.

## Treat generated visuals as planning aids

Generated style studies may clarify shape, palette, or composition when the
user requests them. Store them outside runtime asset folders, record prompts,
hashes, and provenance, and mark them:

```text
PLANNING REFERENCE ONLY
NOT A RUNTIME ASSET
NOT RUNNING-BUILD EVIDENCE
NOT A CANONICAL SOURCE WHEN IT CONFLICTS WITH USER REFERENCES
```

Do not allow a generated study to silently replace the user's primary mockup.
