# Images and motion

Only when the UI still reads as code-shapes, or the user asked for generated visuals. Never invent API keys. Never write keys into source, prompts committed to the repo, or client bundles.

Product chrome usually does not need this. A narrative walkthrough, onboarding, or empty state might.

## Images

If an image-generation tool is already available in the session, use it.

Otherwise look for a gitignored `.env.agents` (or project env) and use those keys **locally**. If none exist, skip — do not block the UI on image gen.

One distinctive image, shader, or 3D treatment beats a set of generic assets. Verify in the browser.

## Looping graphic

1. Generate a short loop on a solid-color background.
2. Chroma-key or matte the background out.
3. Layer it in the UI so it reads as part of the surface, not a video player.

For refraction/glass: render the subject over the **actual background colors** first, then matte.

## Scroll-scrubbed transitions

1. Still of state A (image gen or screenshot).
2. Video from A → B with a physics-strong model.
3. Last frame of that clip seeds B → C so the join is seamless.
4. Scrub the clip(s) from scroll/swipe, don’t autoplay a movie.

Skip this unless the user wants a motion-led surface and a video API is already configured.
