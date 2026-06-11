(() => {
  const scrollKey = "archiveScrollY";
  const homePaths = new Set(["/", "/index.html"]);

  const isHome = () => homePaths.has(window.location.pathname);
  const saveScroll = () => {
    if (isHome()) {
      sessionStorage.setItem(scrollKey, String(window.scrollY));
    }
  };

  if (isHome()) {
    const saved = Number(sessionStorage.getItem(scrollKey));
    if (Number.isFinite(saved) && saved > 0) {
      requestAnimationFrame(() => window.scrollTo(0, saved));
    }

    document.addEventListener("click", (event) => {
      const link = event.target.closest("a[href]");
      if (!link) return;
      const url = new URL(link.href, window.location.href);
      if (url.origin === window.location.origin && url.pathname !== window.location.pathname) {
        saveScroll();
      }
    });

    window.addEventListener("pagehide", saveScroll);
  }

  document.addEventListener("click", (event) => {
    const link = event.target.closest("[data-go-back-home]");
    if (!link) return;
    const referrer = document.referrer ? new URL(document.referrer) : null;
    if (referrer && referrer.origin === window.location.origin && history.length > 1) {
      event.preventDefault();
      history.back();
    }
  });

  const patternConfig = {
    asset: "/broken-brick-icon-grey.png",
    gap: 38,
    minRail: 64,
    size: 46,
    minVerticalSpacing: 190,
    horizontalCell: 118,
    padding: 18,
    scrollDrift: 0.18,
    fadeZone: 150,
  };

  let patternFrame = 0;

  const clearPattern = () => {
    document.querySelectorAll(".brick-rail-pattern").forEach((node) => node.remove());
  };

  const updatePatternDrift = () => {
    patternFrame = 0;
    const drift = Math.round(window.scrollY * patternConfig.scrollDrift);
    document.querySelectorAll(".brick-rail-pattern").forEach((rail) => {
      rail.querySelectorAll("span").forEach((box, index) => {
        const depth = Number(box.dataset.depth || "1");
        const baseY = Number(box.dataset.baseY || "0");
        const boxSize = box.offsetHeight || 70;
        const minY = -boxSize - patternConfig.padding;
        const maxY = window.innerHeight + patternConfig.padding;
        const range = Math.max(1, maxY - minY);
        const shifted = minY + (((baseY - drift * depth - minY) % range) + range) % range;
        box.style.top = `${Math.round(shifted)}px`;
        const center = shifted + boxSize / 2;
        const topFade = Math.min(1, Math.max(0, center / patternConfig.fadeZone));
        const bottomFade = Math.min(1, Math.max(0, (window.innerHeight - center) / patternConfig.fadeZone));
        const edgeFade = Math.min(topFade, bottomFade);
        const image = box.firstElementChild;
        if (image) image.style.opacity = String((0.12 * edgeFade).toFixed(3));
      });
    });
  };

  const requestPatternDrift = () => {
    if (patternFrame) return;
    patternFrame = window.requestAnimationFrame(updatePatternDrift);
  };

  const buildRail = (side, bounds, viewportHeight) => {
    const railWidth = Math.floor(bounds.width);
    const rail = document.createElement("div");
    rail.className = `brick-rail-pattern brick-rail-pattern--${side}`;
    Object.assign(rail.style, {
      position: "fixed",
      top: "0",
      bottom: "0",
      width: `${railWidth}px`,
      left: `${Math.floor(bounds.left)}px`,
      pointerEvents: "none",
      overflow: "hidden",
      zIndex: "0",
    });

    const rotations = [-10, -6, 5, 9, -4, 7];
    const size = Math.min(patternConfig.size, Math.max(30, railWidth - patternConfig.padding * 2));
    const boxSize = Math.ceil(size * 1.5);
    const columns = Math.max(1, Math.min(3, Math.floor(railWidth / patternConfig.horizontalCell)));
    const columnWidth = railWidth / columns;
    const rowOffset = side === "left" ? 38 : 96;
    const rowCount = Math.max(0, Math.floor((viewportHeight - rowOffset - boxSize - patternConfig.padding) / patternConfig.minVerticalSpacing) + 1);
    const maxY = viewportHeight - boxSize - patternConfig.padding;

    for (let row = 0; row < rowCount; row += 1) {
      const column = (row + (side === "left" ? 0 : 1)) % columns;
      const cellLeft = column * columnWidth;
      const jitterLimit = Math.max(0, columnWidth - boxSize - patternConfig.padding * 2);
      const jitter = columns === 1 || !jitterLimit ? 0 : ((row * 37 + (side === "left" ? 11 : 23)) % jitterLimit);
      const centeredSingleColumnX = Math.max(patternConfig.padding, (railWidth - boxSize) / 2);
      const columnX = cellLeft + patternConfig.padding + jitter;
      const x = columns === 1
        ? centeredSingleColumnX
        : Math.min(railWidth - boxSize - patternConfig.padding, Math.max(patternConfig.padding, columnX));
      const y = Math.min(maxY, rowOffset + row * patternConfig.minVerticalSpacing);
      const rotation = rotations[(row + (side === "left" ? 0 : 2)) % rotations.length];
      const box = document.createElement("span");
      Object.assign(box.style, {
        position: "absolute",
        width: `${boxSize}px`,
        height: `${boxSize}px`,
        left: `${x}px`,
        top: `${y}px`,
        willChange: "top",
      });
      box.dataset.baseY = String(y);
      box.dataset.depth = String(0.75 + ((row % 3) * 0.18));
      const img = document.createElement("img");
      img.src = patternConfig.asset;
      img.alt = "";
      img.decoding = "async";
      img.loading = "eager";
      Object.assign(img.style, {
        position: "absolute",
        width: `${size}px`,
        height: `${size}px`,
        left: `${Math.floor((boxSize - size) / 2)}px`,
        top: `${Math.floor((boxSize - size) / 2)}px`,
        opacity: "0.12",
        transform: `rotate(${rotation}deg)`,
        transformOrigin: "50% 50%",
      });
      box.appendChild(img);
      rail.appendChild(box);
    }

    document.body.appendChild(rail);
  };

  const renderPattern = () => {
    clearPattern();
    const isNarrow = window.matchMedia("(max-width: 620px)").matches;
    const main = document.querySelector("main");
    if (isNarrow || !main) return;
    const rect = main.getBoundingClientRect();
    const leftBounds = { left: 0, width: Math.max(0, Math.floor(rect.left - patternConfig.gap)) };
    const rightStart = Math.ceil(rect.right + patternConfig.gap);
    const rightBounds = { left: rightStart, width: Math.max(0, window.innerWidth - rightStart) };
    if (leftBounds.width >= patternConfig.minRail) buildRail("left", leftBounds, window.innerHeight);
    if (rightBounds.width >= patternConfig.minRail) buildRail("right", rightBounds, window.innerHeight);
  };

  renderPattern();
  updatePatternDrift();
  let resizeTimer = 0;
  window.addEventListener("resize", () => {
    window.clearTimeout(resizeTimer);
    resizeTimer = window.setTimeout(() => {
      renderPattern();
      updatePatternDrift();
    }, 100);
  });
  window.addEventListener("scroll", requestPatternDrift, { passive: true });
})();
