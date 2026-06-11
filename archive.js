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
    const hash = window.location.hash;
    if (hash && hash.length > 1) {
      requestAnimationFrame(() => {
        const target = document.querySelector(hash);
        if (target) target.scrollIntoView();
      });
    } else {
      const saved = Number(sessionStorage.getItem(scrollKey));
      if (Number.isFinite(saved) && saved > 0) {
        requestAnimationFrame(() => window.scrollTo(0, saved));
      }
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

  const setupArchiveFilters = () => {
    const form = document.querySelector("[data-archive-filters]");
    const groups = Array.from(document.querySelectorAll(".group[data-group]"));
    if (!form || !groups.length) return;

    const search = form.querySelector("[data-filter-search]");
    const status = form.querySelector("[data-filter-status]");
    const results = form.querySelector("[data-filter-results]");
    const clearBtn = form.querySelector("[data-filter-clear]");
    const topicsToggle = form.querySelector("[data-filter-topics-toggle]");
    const topicsPanel = form.querySelector("[data-filter-topics-panel]");
    const empty = document.querySelector("[data-filter-empty]");

    const groupLabels = new Map([
      ["all", "all topics"],
      ["1", "Franchise FDD"],
      ["2", "Financing & Legally Mine"],
      ["2L", "Legally Mine"],
      ["2F", "Financing records"],
      ["3", "Ammon McNeff federal"],
      ["4", "Chrystal Law"],
      ["5", "AFPD & Reckless Ben"],
      ["6", "Reckless Ben Utah lawsuit"],
      ["7", "Reckless Ben small claims"],
    ]);

    const caseLabels = new Map([
      ["all", "all cases"],
      ["7.A", "v. L2 Bricks"],
      ["7.B", "v. L2 Bricks (2)"],
      ["7.C", "v. Joshua Johnson"],
    ]);

    let activeGroup = "all";
    let activeCase = "all";
    let urlTimer = 0;

    const normalize = (value) => value.toLowerCase().replace(/\s+/g, " ").trim();

    const syncUrl = () => {
      window.clearTimeout(urlTimer);
      urlTimer = window.setTimeout(() => {
        const params = new URLSearchParams();
        const query = (search?.value || "").trim();
        if (query) params.set("q", query);
        if (activeGroup !== "all") params.set("group", activeGroup);
        if (activeGroup === "7" && activeCase !== "all") params.set("case", activeCase);
        const next = params.toString();
        const nextUrl = next ? `${window.location.pathname}?${next}` : window.location.pathname;
        if (`${window.location.pathname}${window.location.search}` !== nextUrl) {
          window.history.replaceState(null, "", nextUrl);
        }
      }, 200);
    };

    const readUrl = () => {
      const params = new URLSearchParams(window.location.search);
      const group = params.get("group");
      const caseValue = params.get("case");
      const query = params.get("q") || "";

      if (group && groupLabels.has(group)) activeGroup = group;
      if (caseValue && ["7.A", "7.B", "7.C"].includes(caseValue)) activeCase = caseValue;
      if (search) search.value = query;
    };

    const subdocHeaderText = (subdoc) => {
      const clone = subdoc.cloneNode(true);
      clone.querySelectorAll(".case-docs").forEach((node) => node.remove());
      return normalize(clone.textContent || "");
    };

    const update = () => {
      const query = normalize(search?.value || "");
      let visibleGroupCount = 0;
      let visibleItemCount = 0;
      const isFiltered = Boolean(query) || activeGroup !== "all" || activeCase !== "all";

      groups.forEach((group) => {
        const groupNum = group.dataset.group || "";
        const groupMatch = activeGroup === "all" || activeGroup === groupNum;
        const subdocs = Array.from(group.querySelectorAll(".subdocs > li"));
        let visibleSubdocs = 0;

        subdocs.forEach((subdoc) => {
          const caseLabel = subdoc.dataset.case || "";
          const caseMatch = activeCase === "all" || !caseLabel || activeCase === caseLabel;
          const caseDocs = Array.from(subdoc.querySelectorAll(".case-docs > li"));

          if (caseDocs.length) {
            const headerMatch = !query || subdocHeaderText(subdoc).includes(query);
            let matchingFilings = 0;

            caseDocs.forEach((filing) => {
              const filingRef = filing.dataset.docNum || "";
              const filingText = normalize(`${filingRef} ${filing.textContent || ""}`);
              if (!query || filingText.includes(query)) matchingFilings += 1;
            });

            const showAllFilings = headerMatch && matchingFilings === 0 && Boolean(query);
            const subdocVisible = groupMatch && caseMatch && (matchingFilings > 0 || headerMatch);

            caseDocs.forEach((filing) => {
              const filingRef = filing.dataset.docNum || "";
              const filingText = normalize(`${filingRef} ${filing.textContent || ""}`);
              const filingMatch = !query || filingText.includes(query);
              const visible = subdocVisible && (showAllFilings || filingMatch);
              filing.hidden = !visible;
              if (visible) visibleItemCount += 1;
            });

            subdoc.hidden = !subdocVisible;
            if (subdocVisible) visibleSubdocs += 1;
            return;
          }

          const textMatch = !query || normalize(subdoc.textContent || "").includes(query);
          const subdocVisible = groupMatch && textMatch;
          subdoc.hidden = !subdocVisible;
          if (subdocVisible) {
            visibleSubdocs += 1;
            visibleItemCount += 1;
          }
        });

        const groupVisible = groupMatch && visibleSubdocs > 0;
        group.hidden = !groupVisible;
        if (groupVisible) visibleGroupCount += 1;
      });

      if (clearBtn) clearBtn.hidden = !isFiltered;

      if (empty) empty.classList.toggle("is-visible", visibleGroupCount === 0);

      if (results) {
        const scopeParts = [];
        if (activeGroup !== "all") scopeParts.push(groupLabels.get(activeGroup) || "");
        if (activeGroup === "7" && activeCase !== "all") {
          scopeParts.push(caseLabels.get(activeCase) || activeCase);
        }
        const scopeLabel = scopeParts.filter(Boolean).join(", ");

        if (!isFiltered) {
          results.textContent = `${visibleItemCount} items`;
        } else if (visibleItemCount === 0) {
          results.textContent = scopeLabel ? `No results, ${scopeLabel}` : "No results";
        } else {
          const itemPart = `${visibleItemCount} item${visibleItemCount === 1 ? "" : "s"}`;
          results.textContent = scopeLabel ? `${itemPart}, ${scopeLabel}` : itemPart;
        }
      }

      if (status) {
        let label = groupLabels.get(activeGroup) || "all topics";
        if (activeGroup === "7" && activeCase !== "all") {
          label = `${label} — ${caseLabels.get(activeCase) || activeCase}`;
        }
        const scope = query ? `matching "${search.value.trim()}" in ${label}` : `in ${label}`;
        status.textContent = visibleItemCount
          ? `Showing ${visibleItemCount} item${visibleItemCount === 1 ? "" : "s"} ${scope}.`
          : `No items ${scope}.`;
      }

      syncUrl();
    };

    clearBtn?.addEventListener("click", () => {
      activeGroup = "all";
      activeCase = "all";
      if (search) search.value = "";
      update();
    });

    topicsToggle?.addEventListener("click", () => {
      const open = topicsPanel?.hidden ?? true;
      if (topicsPanel) topicsPanel.hidden = !open;
      topicsToggle.setAttribute("aria-expanded", open ? "true" : "false");
    });

    search?.addEventListener("input", update);
    form.addEventListener("submit", (event) => event.preventDefault());

    document.addEventListener("keydown", (event) => {
      if (event.key === "/" && !event.metaKey && !event.ctrlKey && !event.altKey) {
        const tag = (event.target?.tagName || "").toLowerCase();
        if (tag === "input" || tag === "textarea" || tag === "select" || event.target?.isContentEditable) return;
        event.preventDefault();
        search?.focus();
      }
      if (event.key === "Escape" && document.activeElement === search) {
        const hasFilter = Boolean(search?.value) || activeGroup !== "all" || activeCase !== "all";
        if (hasFilter) clearBtn?.click();
      }
    });

    const openTopicsPanel = () => {
      if (!topicsPanel || !topicsToggle) return;
      topicsPanel.hidden = false;
      topicsToggle.setAttribute("aria-expanded", "true");
    };

    readUrl();
    update();
    if (activeGroup !== "all" || activeCase !== "all") openTopicsPanel();
  };

  if (isHome()) setupArchiveFilters();

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

  // === Top legal notice banner ===
  // Injected via the shared script so it appears on the homepage and every document page.
  // Dismissible for 14 days via localStorage for usability.
  (() => {
    const DISMISS_KEY = "legalBannerDismissedUntil";
    const DISMISS_DAYS = 14;
    const now = Date.now();

    const dismissedUntil = Number(localStorage.getItem(DISMISS_KEY) || 0);
    if (dismissedUntil > now) return;
    if (document.getElementById("legal-banner")) return;

    const banner = document.createElement("div");
    banner.id = "legal-banner";
    banner.setAttribute("role", "note");
    banner.setAttribute("aria-label", "Notice");

    banner.innerHTML = `
      <div class="legal-banner-inner" style="max-width:1000px;margin:0 auto;padding:8px 20px 8px 20px;display:flex;align-items:flex-start;gap:16px;">
        <div style="flex:1;min-width:0;line-height:1.3;">
          <strong style="font-size:13.5px;letter-spacing:0.5px;font-weight:700;">NOTICE:</strong>
          <span style="font-size:12.5px; display:block; margin-top:3px;">
            This site is a neutral public archive of verbatim court documents, police reports, docket records, and regulatory filings from the Bricks and Minifigs litigation and related proceedings. All materials are sourced exclusively from official public records. This archive is maintained for transparency, accountability, and the public's right of access to judicial proceedings (protected by the First Amendment and common-law public records doctrine). This site does not publish home addresses, personal phone numbers, personal email addresses, family information or other doxxing information beyond what is already contained in the official public filings, and does not organize or encourage threats of physical harm or physical interference.
          </span>
        </div>
        <button id="legal-banner-close" aria-label="Dismiss this notice" style="background:transparent;border:0;font-size:22px;line-height:1;cursor:pointer;padding:0 2px;color:#854d0e;flex-shrink:0;opacity:0.85;">×</button>
      </div>
    `;

    Object.assign(banner.style, {
      background: "#fefce8",
      borderBottom: "1px solid #854d0e",
      color: "#3f2a00",
      padding: "9px 0",
      fontFamily: 'system-ui, -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif',
      position: "relative",
      zIndex: "50"
    });

    // Insert at the top so it appears above existing page content
    const mainEl = document.querySelector("main");
    if (mainEl && mainEl.parentNode) {
      mainEl.parentNode.insertBefore(banner, mainEl);
    } else {
      document.body.insertBefore(banner, document.body.firstChild);
    }

    const closeBtn = banner.querySelector("#legal-banner-close");
    if (closeBtn) {
      closeBtn.addEventListener("click", () => {
        banner.remove();
        const expiry = now + (DISMISS_DAYS * 24 * 60 * 60 * 1000);
        localStorage.setItem(DISMISS_KEY, String(expiry));
      });
    }
  })();

  // === Group navigation bar for individual document reader pages ===
  // When you're inside one specific document (e.g. a police report or a court filing),
  // this injects "Back to [Greater Group]" + Previous/Next buttons within that group.
  (() => {
    const GROUP_DATA = {
      "franchise-background": {
        num: "1",
        title: "Bricks and Minifigs franchise background",
        items: [
          {num: "1A", slug: "bricks-minifigs-2023-fdd", title: "Bricks and Minifigs 2023 FDD"},
          {num: "1B", slug: "bam-franchising-2026-fdd", title: "Bricks and Minifigs 2026 FDD"},
          {num: "1C", slug: "bam-franchising-fdd-registration-history", title: "Bricks and Minifigs state registration list"}
        ]
      },
      "utah-ucc-financing-records": {
        num: "2",
        title: "Financing & Legally Mine records",
        items: [
          {num: "2A", slug: "utah-ucc-bam-franchising-summary", title: "Bricks and Minifigs Utah UCC summary"},
          {num: "2B", slug: "utah-ucc-bam-franchising-detail", title: "Bricks and Minifigs Utah UCC detailed filing"},
          {num: "2C", slug: "utah-ucc-legally-mine-summary", title: "Legally Mine Utah UCC summary"},
          {num: "2D", slug: "utah-ucc-legally-mine-detail", title: "Legally Mine Utah UCC detailed filing"},
          {num: "2E", slug: "legally-mine-ohio-upl-order-2025-0037", title: "Legally Mine Ohio unauthorized practice order"}
        ]
      },
      "mcneff-v-mcneff-utah-federal-2-21-cv-00048": {
        num: "3",
        title: "Ammon McNeff / Legally Mine federal court documents",
        items: [
          {num: "3A", slug: "mcneff-v-mcneff-2-21-cv-00048-doc-1-civil-cover-sheet", title: "Civil cover sheet"},
          {num: "3B", slug: "mcneff-v-mcneff-2-21-cv-00048-doc-2-complaint", title: "Federal complaint"},
          {num: "3C", slug: "mcneff-v-mcneff-2-21-cv-00048-doc-2-1-civil-cover-sheet", title: "Complaint attachment civil cover sheet"},
          {num: "3D", slug: "mcneff-v-mcneff-2-21-cv-00048-doc-2-2-exhibit-a", title: "Exhibit A"},
          {num: "3E", slug: "mcneff-v-mcneff-2-21-cv-00048-doc-2-3-exhibit-b", title: "Exhibit B"},
          {num: "3F", slug: "mcneff-v-mcneff-2-21-cv-00048-doc-2-4-exhibit-c", title: "Exhibit C"},
          {num: "3G", slug: "mcneff-v-mcneff-2-21-cv-00048-doc-2-5-exhibit-d", title: "Exhibit D"},
          {num: "3H", slug: "mcneff-v-mcneff-2-21-cv-00048-doc-2-6-exhibit-e", title: "Exhibit E"},
          {num: "3I", slug: "mcneff-v-mcneff-2-21-cv-00048-doc-2-7-exhibit-f", title: "Exhibit F"},
          {num: "3J", slug: "mcneff-v-mcneff-2-21-cv-00048-doc-3-order-to-propose-schedule", title: "Order to propose schedule"},
          {num: "3K", slug: "mcneff-v-mcneff-2-21-cv-00048-doc-12-filing", title: "Doc. 12 filing (voluntary dismissal)"}
        ]
      },
      "business-chancery-260200029": {
        num: "4",
        title: "Chrystal Law / Benjamin Gorman case",
        items: [
          {num: "4A", slug: "chrystal-law-bricks-minifigs-lawsuit", title: "Complaint"},
          {num: "4B", slug: "chrystal-law-bricks-minifigs-exhibit-a-lego-email", title: "Exhibit A - LEGO customer service email"},
          {num: "4C", slug: "chrystal-law-bricks-minifigs-exhibit-b-franchise-agreement", title: "Exhibit B - Franchise agreement"},
          {num: "4D", slug: "chrystal-law-bricks-minifigs-exhibit-d-termination-letter", title: "Exhibit D - Immediate termination letter"},
          {num: "4E", slug: "bricks-minifigs-motion-stay-compel-mediation-arbitration-260200029", title: "Motion to stay and compel mediation / arbitration"}
        ]
      },
      "american-fork-police-records": {
        num: "5",
        title: "American Fork police records",
        items: [
          {num: "5A", slug: "american-fork-police-26af01974-trespass", title: "Trespass incident report"},
          {num: "5B", slug: "american-fork-police-26af02007-harassment", title: "Harassment incident report"},
          {num: "5C", slug: "american-fork-police-26af02033-stalking-harassment", title: "Stalking / harassment incident report"},
          {num: "5E", slug: "american-fork-police-26af02033-probable-cause", title: "Probable cause statement"},
          {num: "5F", slug: "american-fork-police-26af02033-booking-sheet", title: "Booking sheet"},
          {num: "5G", slug: "search-warrant-3352981", title: "Search warrant 3352981"}
        ]
      },
      "case-260402353": {
        num: "6",
        title: "Bricks and Minifigs civil case in Utah",
        items: [
          {num: "6A", slug: "bricks-minifigs-v-reckless-ben-verified-complaint", title: "Verified Complaint"},
          {num: "6B", slug: "bricks-minifigs-v-reckless-ben-tro", title: "Temporary Restraining Order"},
          {num: "6C", slug: "bricks-minifigs-v-reckless-ben-errata", title: "Errata"},
          {num: "6D", slug: "bricks-minifigs-v-reckless-ben-filing-receipt", title: "Filing Receipt"},
          {num: "6E", slug: "utah-case-260402353-case-history", title: "Utah Case 260402353 Case History"},
          {num: "6F", slug: "utah-case-260402353-docket-events", title: "Utah Case 260402353 Docket Events"},
          {num: "6G", slug: "bricks-minifigs-v-reckless-ben-order-alternative-service", title: "Bricks and Minifigs Ex Parte Order"},
          {num: "6H", slug: "bricks-minifigs-v-reckless-ben-exhibit-a-consignment-agreement", title: "Exhibit A - Consignment Agreement"},
          {num: "6I", slug: "bricks-minifigs-v-reckless-ben-exhibit-b-sold-sets-mansell-investigation", title: "Exhibit B - Sold Sets / POS Data"},
          {num: "6I-IND", slug: "bricks-minifigs-v-reckless-ben-exhibit-b-independent-bam-pos-reconcile", title: "Exhibit B - Independent BAM POS / Inventory Reconciliation"},
          {num: "6J", slug: "bricks-minifigs-v-reckless-ben-exhibit-g-community-note-salem-store", title: "Exhibit G - Community Note"},
          {num: "6K", slug: "bricks-minifigs-v-reckless-ben-exhibit-i-incident-log", title: "Exhibit I - Incident Log"},
          {num: "6L", slug: "bricks-minifigs-v-reckless-ben-exhibit-j-notice-trespass", title: "Exhibit J - Notice of Trespass"},
          {num: "6M", slug: "bricks-minifigs-v-reckless-ben-exhibit-k-threat-email", title: "Exhibit K - Threat Email"},
          {num: "6N", slug: "bricks-minifigs-v-reckless-ben-ex-parte-motion-tro-preliminary-injunction", title: "Ex Parte Motion for TRO / Preliminary Injunction"},
          {num: "6O", slug: "bricks-minifigs-v-reckless-ben-tro-entered-june-02-2026", title: "TRO (Entered June 2, 2026)"},
          {num: "6P", slug: "bricks-minifigs-v-reckless-ben-case-proceedings-summary-05-28-2026", title: "Case Proceedings Summary (05-28-2026)"}
        ]
      },
      "oregon-small-claims-files": {
        num: "7",
        title: "Small claims involving Reckless Ben / Benjamin Schneider",
        caseAnchors: {
          "7.A": { id: "oregon-small-claims-25sc26531", title: "25SC26531 - Benjamin Schneider v. L2 Bricks, LLC" },
          "7.B": { id: "oregon-small-claims-25sc30722", title: "25SC30722 - Benjamin Schneider v. L2 Bricks, LLC" },
          "7.C": { id: "oregon-small-claims-26sc06134", title: "26SC06134 - Benjamin Schneider v. Joshua Johnson" }
        },
        items: [
          {num: "7.A.1", slug: "oregon-small-claims-25sc26531-claim-amended-ccam-166809996", title: "25SC26531 - Claim - Amended - CCAM"},
          {num: "7.A.2", slug: "oregon-small-claims-25sc26531-judgment-housecleaning-dismissal-mar-169869745", title: "25SC26531 - Judgment - Housecleaning Dismissal - MAR"},
          {num: "7.A.3", slug: "oregon-small-claims-25sc26531-notice-entry-of-judgment-169875697", title: "25SC26531 - Notice - Entry of Judgment"},
          {num: "7.A.4", slug: "oregon-small-claims-25sc26531-notice-entry-of-judgment-169875698", title: "25SC26531 - Notice - Entry of Judgment"},
          {num: "7.A.5", slug: "oregon-small-claims-25sc26531-small-claim-complaint-165556863", title: "25SC26531 - Small Claim Complaint"},
          {num: "7.B.1", slug: "oregon-small-claims-25sc30722-judgment-housecleaning-dismissal-mar-174337147", title: "25SC30722 - Judgment - Housecleaning Dismissal - MAR"},
          {num: "7.B.2", slug: "oregon-small-claims-25sc30722-letter-168333371", title: "25SC30722 - Letter"},
          {num: "7.B.3", slug: "oregon-small-claims-25sc30722-motion-default-order-modf-169758129", title: "25SC30722 - Motion - Default Order - MODF"},
          {num: "7.B.4", slug: "oregon-small-claims-25sc30722-motion-default-order-modf-171485058", title: "25SC30722 - Motion - Default Order - MODF"},
          {num: "7.B.5", slug: "oregon-small-claims-25sc30722-notice-entry-of-judgment-174337844", title: "25SC30722 - Notice - Entry of Judgment"},
          {num: "7.B.6", slug: "oregon-small-claims-25sc30722-notice-entry-of-judgment-174337845", title: "25SC30722 - Notice - Entry of Judgment"},
          {num: "7.B.7", slug: "oregon-small-claims-25sc30722-order-denial-170474785", title: "25SC30722 - Order - Denial"},
          {num: "7.B.8", slug: "oregon-small-claims-25sc30722-order-denial-170485650", title: "25SC30722 - Order - Denial"},
          {num: "7.B.9", slug: "oregon-small-claims-25sc30722-proof-service-prsv-169492090", title: "25SC30722 - Proof - Service - PRSV"},
          {num: "7.B.10", slug: "oregon-small-claims-25sc30722-proof-service-prsv-171384311", title: "25SC30722 - Proof - Service - PRSV"},
          {num: "7.B.11", slug: "oregon-small-claims-25sc30722-small-claim-complaint-167756667", title: "25SC30722 - Small Claim Complaint"},
          {num: "7.C.1", slug: "oregon-small-claims-26sc06134-claim-cc-172657761", title: "26SC06134 - Claim - CC"},
          {num: "7.C.2", slug: "oregon-small-claims-26sc06134-consent-cn-176214847", title: "26SC06134 - Consent - CN"},
          {num: "7.C.3", slug: "oregon-small-claims-26sc06134-mediation-no-agreement-mena-176214854", title: "26SC06134 - Mediation - No Agreement - MENA"},
          {num: "7.C.4", slug: "oregon-small-claims-26sc06134-notice-hearing-176235961", title: "26SC06134 - Notice - Hearing"},
          {num: "7.C.5", slug: "oregon-small-claims-26sc06134-notice-hearing-176236001", title: "26SC06134 - Notice - Hearing"},
          {num: "7.C.6", slug: "oregon-small-claims-26sc06134-notice-hearing-176236002", title: "26SC06134 - Notice - Hearing"},
          {num: "7.C.7", slug: "oregon-small-claims-26sc06134-notice-hearing-176236129", title: "26SC06134 - Notice - Hearing"},
          {num: "7.C.8", slug: "oregon-small-claims-26sc06134-notice-hearing-mediation-n2n-mar-173174720", title: "26SC06134 - Notice - Hearing Mediation N2N-MAR"},
          {num: "7.C.9", slug: "oregon-small-claims-26sc06134-notice-hearing-mediation-n2n-mar-173174721", title: "26SC06134 - Notice - Hearing Mediation N2N-MAR"},
          {num: "7.C.10", slug: "oregon-small-claims-26sc06134-notice-hearing-mediation-n2n-mar-173174722", title: "26SC06134 - Notice - Hearing Mediation N2N-MAR"},
          {num: "7.C.11", slug: "oregon-small-claims-26sc06134-notice-hearing-mediation-n2n-mar-174691859", title: "26SC06134 - Notice - Hearing Mediation N2N-MAR"},
          {num: "7.C.12", slug: "oregon-small-claims-26sc06134-notice-hearing-mediation-n2n-mar-174691865", title: "26SC06134 - Notice - Hearing Mediation N2N-MAR"},
          {num: "7.C.13", slug: "oregon-small-claims-26sc06134-notice-hearing-mediation-n2n-mar-174691866", title: "26SC06134 - Notice - Hearing Mediation N2N-MAR"},
          {num: "7.C.14", slug: "oregon-small-claims-26sc06134-notice-hearing-mediation-n2n-mar-174691867", title: "26SC06134 - Notice - Hearing Mediation N2N-MAR"},
          {num: "7.C.15", slug: "oregon-small-claims-26sc06134-small-claim-response-173126684", title: "26SC06134 - Small Claim Response"}
        ]
      }
    };

    const getSlug = () => {
      let p = window.location.pathname || "";
      if (p.endsWith("/")) p = p.slice(0, -1);
      if (p.startsWith("/")) p = p.slice(1);
      // handle any index.html suffix just in case
      if (p.endsWith("/index.html")) p = p.replace(/\/index\.html$/, "");
      return p;
    };

    const slug = getSlug();
    if (!slug || slug === "" || slug === "index.html" || slug === "reckless-ben-community-archive") return;

    let currentGroup = null;
    let currentIndex = -1;
    let currentItem = null;

    for (const [gid, gdata] of Object.entries(GROUP_DATA)) {
      const idx = gdata.items.findIndex(it => it.slug === slug);
      if (idx !== -1) {
        currentGroup = { id: gid, ...gdata };
        currentIndex = idx;
        currentItem = gdata.items[idx];
        break;
      }
    }

    if (!currentGroup || !currentItem) return;

    const topLinks = document.querySelector("nav.top-links");
    if (!topLinks) return;

    // "Go Back Home" is redundant on group pages — Group N / Home covers it on the left.
    document.querySelectorAll("[data-go-back-home]").forEach((link) => link.remove());
    topLinks.querySelectorAll('a[href="/#oregon-small-claims-files"]').forEach((link) => link.remove());
    document.querySelectorAll("footer p").forEach((p) => {
      p.innerHTML = p.innerHTML.replace(/^\s*-\s*/u, "").replace(/\s*-\s*-\s*/g, " - ").trim();
    });

    if (!document.getElementById("group-nav-styles")) {
      const style = document.createElement("style");
      style.id = "group-nav-styles";
      style.textContent = `
        nav.top-links {
          align-items: center;
          row-gap: 10px;
        }
        nav.top-links .group-nav-right {
          margin-left: auto;
          display: inline-flex;
          align-items: center;
          gap: 14px;
          flex-wrap: wrap;
          justify-content: flex-end;
          max-width: 100%;
        }
        nav.top-links .group-seq-nav {
          display: inline-flex;
          align-items: center;
          gap: 8px;
          font-variant-numeric: tabular-nums;
          max-width: 100%;
          overflow-x: auto;
          -webkit-overflow-scrolling: touch;
          scrollbar-width: thin;
          justify-content: center;
        }
        nav.top-links .group-seq-nav > * {
          /* Stabilize layout so numbers/letters don't shift when navigating.
             Fixed min-width per slot + center text keeps the "current" visually
             in the middle on mobile as the window slides. */
          min-width: 2.3em;
          text-align: center;
          box-sizing: content-box;
        }
        nav.top-links .group-seq-nav a,
        nav.top-links .group-seq-current,
        nav.top-links .group-seq-ellipsis {
          white-space: nowrap;
          flex: 0 0 auto;
        }
        nav.top-links .group-seq-current {
          color: #555;
        }
        nav.top-links .group-seq-ellipsis {
          color: #888;
          padding: 0 1px;
        }
        nav.top-links .group-context-links {
          display: inline-flex;
          align-items: center;
          gap: 6px;
          white-space: nowrap;
          flex: 0 0 auto;
        }
        nav.top-links .group-context-sep {
          color: #555;
        }
        nav.top-links .group-seq-prev,
        nav.top-links .group-seq-next {
          font-weight: 700;
          white-space: nowrap;
          flex: 0 0 auto;
        }
        @media (max-width: 620px) {
          #legal-banner .legal-banner-inner {
            padding: 6px 14px 6px 14px;
            gap: 10px;
          }
          #legal-banner .legal-banner-inner span {
            font-size: 12px !important;
          }
          nav.top-links {
            gap: 8px 10px;
            position: sticky;
            top: 0;
            z-index: 30;
            background: #fff;
            margin-bottom: 12px;
            padding-bottom: 10px;
            box-shadow: 0 1px 0 #d7d7d7;
            /* Force clean column stacking on mobile so context and controls
               don't fight for space or wrap the original Open link into the
               group context line. */
            flex-direction: column;
            align-items: stretch;
          }
          nav.top-links .group-context-links {
            flex: none;
            font-size: 0.85rem;
            margin-bottom: 4px;
          }
          nav.top-links .group-nav-right {
            flex: none;
            width: 100%;
            justify-content: space-between;
            gap: 8px;
          }
          nav.top-links .group-seq-nav {
            gap: 6px;
            font-size: 0.9rem;
            max-width: 100%;
            flex: 1 1 auto;
            justify-content: center;
          }
          nav.top-links .group-seq-nav > * {
            /* Keep the current document number locked in the visual middle of
               the 5-slot strip on mobile. All slots get the same min-width so
               the highlight doesn't appear to "move around" as you tap next/prev. */
            min-width: 2.1em;
            text-align: center;
            box-sizing: content-box;
          }
          nav.top-links .group-seq-prev,
          nav.top-links .group-seq-next {
            min-height: 44px;
            display: inline-flex;
            align-items: center;
            padding: 0 4px;
            min-width: 3.5em; /* ensure side slots have consistent footprint */
          }
        }
      `;
      document.head.appendChild(style);
    }

    const getSeqWindow = (items, index) => {
      const isMobile = window.matchMedia("(max-width: 620px)").matches;
      const maxVisible = isMobile ? 5 : 9;
      const total = items.length;
      if (total <= maxVisible) return { start: 0, end: total };

      const side = Math.floor((maxVisible - 1) / 2);
      let start = Math.max(0, index - side);
      let end = Math.min(total, start + maxVisible);
      if (end - start < maxVisible) start = Math.max(0, end - maxVisible);

      // On mobile especially, try to keep the *current* item visually in the
      // middle of the rendered strip (the 3rd slot for 5 items) even near
      // the edges of the group. This stops the highlighted number from
      // "moving around" left/right as you tap next/prev.
      if (isMobile && total > maxVisible) {
        const targetPos = Math.floor(maxVisible / 2); // 2 for 5 items
        const curPos = index - start;
        if (curPos !== targetPos) {
          const delta = curPos - targetPos;
          start = Math.max(0, Math.min(total - maxVisible, start + delta));
          end = Math.min(total, start + maxVisible);
        }
      }

      return { start, end };
    };

    const caseLabel = currentGroup.caseAnchors
      ? currentItem.num.match(/^(7\.[A-C])/)?.[1]
      : null;
    const caseAnchor = caseLabel ? currentGroup.caseAnchors[caseLabel] : null;
    const seqItems = caseLabel
      ? currentGroup.items.filter((item) => item.num.startsWith(`${caseLabel}.`))
      : currentGroup.items;
    const seqIndex = seqItems.findIndex((item) => item.slug === slug);

    const contextLinks = document.createElement("span");
    contextLinks.className = "group-context-links";
    contextLinks.setAttribute("aria-label", "Archive navigation");

    const groupLink = document.createElement("a");
    groupLink.href = caseAnchor ? `/#${caseAnchor.id}` : `/#${currentGroup.id}`;
    groupLink.textContent = caseLabel ? `Group ${caseLabel}` : `Group ${currentGroup.num}`;
    groupLink.title = caseAnchor?.title || currentGroup.title;
    contextLinks.appendChild(groupLink);

    const sep = document.createElement("span");
    sep.className = "group-context-sep";
    sep.textContent = "/";
    sep.setAttribute("aria-hidden", "true");
    contextLinks.appendChild(sep);

    const homeLink = document.createElement("a");
    homeLink.href = "/";
    homeLink.textContent = "Home";
    homeLink.addEventListener("click", () => {
      sessionStorage.removeItem(scrollKey);
    });
    contextLinks.appendChild(homeLink);

    topLinks.insertBefore(contextLinks, topLinks.firstChild);

    // Remove the original document action link (the "Open PDF" or "Open image" that was
    // the only child of the header's .top-links in the static HTML).
    // It gets mixed into the group context line on mobile ("Group 6 / Home image") and
    // is redundant anyway — the sidebar .actions already has Open/Download, and the
    // seq nav is for switching documents.
    topLinks.querySelectorAll(':scope > a').forEach(a => a.remove());

    if (seqItems.length > 1) {
      const rightNav = document.createElement("div");
      rightNav.className = "group-nav-right";

      const isMobile = window.matchMedia("(max-width: 620px)").matches;

      // Build the sequence strip first (used in both desktop and mobile paths)
      const seqNav = document.createElement("span");
      seqNav.className = "group-seq-nav";
      seqNav.setAttribute("aria-label", "Documents in this group");

      const { start, end } = getSeqWindow(seqItems, seqIndex);
      if (start > 0) {
        const ellipsis = document.createElement("span");
        ellipsis.className = "group-seq-ellipsis";
        ellipsis.textContent = "…";
        ellipsis.setAttribute("aria-hidden", "true");
        seqNav.appendChild(ellipsis);
      }

      seqItems.slice(start, end).forEach((item, offset) => {
        const idx = start + offset;
        if (idx === seqIndex) {
          const current = document.createElement("span");
          current.className = "group-seq-current";
          current.textContent = item.num;
          current.setAttribute("aria-current", "page");
          seqNav.appendChild(current);
          return;
        }

        const link = document.createElement("a");
        link.href = `/${item.slug}/`;
        link.title = item.title;
        link.textContent = item.num;
        seqNav.appendChild(link);
      });

      if (end < seqItems.length) {
        const ellipsis = document.createElement("span");
        ellipsis.className = "group-seq-ellipsis";
        ellipsis.textContent = "…";
        ellipsis.setAttribute("aria-hidden", "true");
        seqNav.appendChild(ellipsis);
      }

      if (!isMobile) {
        // Desktop: original conditional behavior (no forced spacers)
        if (seqIndex > 0) {
          const prev = seqItems[seqIndex - 1];
          const prevLink = document.createElement("a");
          prevLink.className = "group-seq-prev";
          prevLink.href = `/${prev.slug}/`;
          prevLink.title = prev.title;
          prevLink.textContent = "‹ Prev";
          prevLink.setAttribute("aria-label", `Previous: ${prev.title}`);
          rightNav.appendChild(prevLink);
        }

        rightNav.appendChild(seqNav);

        if (seqIndex < seqItems.length - 1) {
          const next = seqItems[seqIndex + 1];
          const nextLink = document.createElement("a");
          nextLink.className = "group-seq-next";
          nextLink.href = `/${next.slug}/`;
          nextLink.title = next.title;
          nextLink.textContent = "Next ›";
          nextLink.setAttribute("aria-label", `Next: ${next.title}`);
          rightNav.appendChild(nextLink);
        }
      } else {
        // Mobile: *always* render three slots (left | seq | right).
        // When there is no prev/next we insert a hidden spacer with identical
        // text + class so the width is *exactly* the same. This prevents the
        // sequence strip (and the current number inside it) from jumping left/right
        // when Prev or Next appear or disappear.
        // The middle seq is always centered between two equal-width sides.

        // Left slot (Prev or hidden spacer with same footprint)
        if (seqIndex > 0) {
          const prev = seqItems[seqIndex - 1];
          const prevLink = document.createElement("a");
          prevLink.className = "group-seq-prev";
          prevLink.href = `/${prev.slug}/`;
          prevLink.title = prev.title;
          prevLink.textContent = "‹ Prev";
          prevLink.setAttribute("aria-label", `Previous: ${prev.title}`);
          rightNav.appendChild(prevLink);
        } else {
          const spacer = document.createElement("span");
          spacer.className = "group-seq-prev"; // reuse arrow styles (height, padding, etc.)
          spacer.textContent = "‹ Prev";
          spacer.setAttribute("aria-hidden", "true");
          spacer.style.visibility = "hidden";
          rightNav.appendChild(spacer);
        }

        rightNav.appendChild(seqNav);

        // Right slot (Next or hidden spacer)
        if (seqIndex < seqItems.length - 1) {
          const next = seqItems[seqIndex + 1];
          const nextLink = document.createElement("a");
          nextLink.className = "group-seq-next";
          nextLink.href = `/${next.slug}/`;
          nextLink.title = next.title;
          nextLink.textContent = "Next ›";
          nextLink.setAttribute("aria-label", `Next: ${next.title}`);
          rightNav.appendChild(nextLink);
        } else {
          const spacer = document.createElement("span");
          spacer.className = "group-seq-next";
          spacer.textContent = "Next ›";
          spacer.setAttribute("aria-hidden", "true");
          spacer.style.visibility = "hidden";
          rightNav.appendChild(spacer);
        }
      }

      topLinks.appendChild(rightNav);
    }
  })();
})();
