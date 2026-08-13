(() => {
  const header = document.querySelector("[data-header]");
  const toggle = document.querySelector("[data-nav-toggle]");
  const nav = document.querySelector("[data-nav]");

  if (header) {
    let lastY = window.scrollY;
    const onScroll = () => {
      const y = Math.max(0, window.scrollY);
      header.classList.toggle("is-scrolled", y > 8);

      const delta = y - lastY;
      const navOpen = header.classList.contains("nav-open");

      if (navOpen || y < 88) {
        header.classList.remove("is-hidden");
      } else if (delta > 6) {
        header.classList.add("is-hidden");
      } else if (delta < -6) {
        header.classList.remove("is-hidden");
      }

      lastY = y;
    };
    onScroll();
    window.addEventListener("scroll", onScroll, { passive: true });
  }

  if (toggle && nav && header) {
    const setOpen = (open) => {
      header.classList.toggle("nav-open", open);
      toggle.setAttribute("aria-expanded", open ? "true" : "false");
      if (open) {
        header.classList.remove("is-hidden");
      }
    };

    toggle.addEventListener("click", () => {
      setOpen(!header.classList.contains("nav-open"));
    });

    nav.querySelectorAll("a").forEach((link) => {
      link.addEventListener("click", () => setOpen(false));
    });

    document.addEventListener("keydown", (event) => {
      if (event.key === "Escape") {
        setOpen(false);
      }
    });
  }

  const initLocationFilters = (form) => {
    const stateSelect = form.querySelector("[data-state-select]");
    const citySelect = form.querySelector("[data-city-select]");
    if (!stateSelect || !citySelect) {
      return;
    }

    let stateCities = {};
    try {
      stateCities = JSON.parse(form.dataset.stateCities || "{}");
    } catch (_error) {
      stateCities = {};
    }

    const allCities = Object.values(stateCities).flat();
    const selectedCity =
      citySelect.dataset.selectedCity || citySelect.value || "";

    const fillCities = (cities, preferredCity) => {
      const current = preferredCity || "";
      citySelect.innerHTML = "";
      const allOption = document.createElement("option");
      allOption.value = "";
      allOption.textContent = "All cities";
      citySelect.appendChild(allOption);

      cities.forEach((city) => {
        const option = document.createElement("option");
        option.value = city;
        option.textContent = city;
        if (city === current) {
          option.selected = true;
        }
        citySelect.appendChild(option);
      });
    };

    const syncCities = () => {
      const state = stateSelect.value;
      const cities = state ? stateCities[state] || [] : allCities;
      fillCities(cities, citySelect.value || selectedCity);
    };

    stateSelect.addEventListener("change", () => {
      fillCities(stateSelect.value ? stateCities[stateSelect.value] || [] : allCities, "");
    });

    syncCities();
  };

  document.querySelectorAll("[data-location-filters]").forEach(initLocationFilters);

  const enhanceSelect = (select) => {
    if (select.closest(".custom-select")) {
      return;
    }

    const wrap = document.createElement("div");
    wrap.className = "custom-select";
    select.parentNode.insertBefore(wrap, select);
    wrap.appendChild(select);
    select.classList.add("custom-select-native");
    select.tabIndex = -1;

    const trigger = document.createElement("button");
    trigger.type = "button";
    trigger.className = "custom-select-trigger";
    trigger.setAttribute("aria-haspopup", "listbox");
    trigger.setAttribute("aria-expanded", "false");
    if (select.getAttribute("aria-label")) {
      trigger.setAttribute("aria-label", select.getAttribute("aria-label"));
    }

    const valueEl = document.createElement("span");
    valueEl.className = "custom-select-value";
    trigger.appendChild(valueEl);

    const panel = document.createElement("div");
    panel.className = "custom-select-panel";
    const searchable = select.name !== "experience";

    let searchInput = null;
    if (searchable) {
      const searchWrap = document.createElement("div");
      searchWrap.className = "custom-select-search";
      searchInput = document.createElement("input");
      searchInput.type = "text";
      searchInput.className = "custom-select-search-input";
      searchInput.placeholder = "Search";
      searchInput.setAttribute("aria-label", "Search options");
      searchInput.autocomplete = "off";
      searchWrap.appendChild(searchInput);
      panel.appendChild(searchWrap);
    }

    const menu = document.createElement("ul");
    menu.className = "custom-select-menu";
    menu.setAttribute("role", "listbox");

    const emptyEl = document.createElement("p");
    emptyEl.className = "custom-select-empty";
    emptyEl.textContent = "No matches";
    emptyEl.hidden = true;

    panel.appendChild(menu);
    if (searchable) {
      panel.appendChild(emptyEl);
    }

    wrap.appendChild(trigger);
    wrap.appendChild(panel);

    const close = () => {
      wrap.classList.remove("is-open");
      trigger.setAttribute("aria-expanded", "false");
      if (searchInput) {
        searchInput.value = "";
        filterOptions("");
      }
    };

    const filterOptions = (query) => {
      const needle = query.trim().toLowerCase();
      let visible = 0;
      menu.querySelectorAll(".custom-select-option").forEach((item) => {
        const match = item.textContent.toLowerCase().includes(needle);
        item.hidden = !match;
        if (match) {
          visible += 1;
        }
      });
      emptyEl.hidden = visible > 0;
    };

    const open = () => {
      document.querySelectorAll(".custom-select.is-open").forEach((item) => {
        if (item !== wrap) {
          item.classList.remove("is-open");
          const otherTrigger = item.querySelector(".custom-select-trigger");
          if (otherTrigger) {
            otherTrigger.setAttribute("aria-expanded", "false");
          }
        }
      });
      wrap.classList.add("is-open");
      trigger.setAttribute("aria-expanded", "true");
      if (searchInput) {
        searchInput.value = "";
        filterOptions("");
      }
      window.requestAnimationFrame(() => {
        if (searchInput) {
          searchInput.focus();
        }
        const selected = menu.querySelector(".is-selected");
        if (selected) {
          selected.scrollIntoView({ block: "nearest" });
        }
      });
    };

    const chooseOption = (option) => {
      select.value = option.value;
      select.dispatchEvent(new Event("change", { bubbles: true }));
      syncFromSelect();
      close();
      trigger.focus();
    };

    const syncFromSelect = () => {
      const selected = select.options[select.selectedIndex];
      valueEl.textContent = selected ? selected.textContent : "";
      menu.innerHTML = "";

      Array.from(select.options).forEach((option) => {
        const item = document.createElement("li");
        item.className = "custom-select-option";
        item.setAttribute("role", "option");
        item.dataset.value = option.value;
        item.textContent = option.textContent;
        if (option.selected) {
          item.classList.add("is-selected");
          item.setAttribute("aria-selected", "true");
        }
        item.addEventListener("click", () => chooseOption(option));
        menu.appendChild(item);
      });

      if (searchInput) {
        filterOptions(searchInput.value);
      }
    };

    trigger.addEventListener("click", () => {
      if (wrap.classList.contains("is-open")) {
        close();
      } else {
        open();
      }
    });

    trigger.addEventListener("keydown", (event) => {
      if (event.key === "ArrowDown" || event.key === "Enter" || event.key === " ") {
        event.preventDefault();
        if (!wrap.classList.contains("is-open")) {
          open();
        }
      }
    });

    if (searchInput) {
      searchInput.addEventListener("input", () => {
        filterOptions(searchInput.value);
      });

      searchInput.addEventListener("keydown", (event) => {
        if (event.key === "Enter") {
          event.preventDefault();
          const firstVisible = menu.querySelector(".custom-select-option:not([hidden])");
          if (firstVisible) {
            const match = Array.from(select.options).find(
              (option) => option.value === firstVisible.dataset.value
            );
            if (match) {
              chooseOption(match);
            }
          }
        }
      });
    }

    select.addEventListener("change", syncFromSelect);

    const observer = new MutationObserver(syncFromSelect);
    observer.observe(select, { childList: true });

    syncFromSelect();
  };

  document.querySelectorAll(".field select").forEach(enhanceSelect);

  const animateCount = (el, delay = 0) => {
    const target = Number(el.dataset.count || 0);
    const suffix = el.dataset.suffix || "";
    const duration = 1400;
    const easeOut = (t) => 1 - Math.pow(1 - t, 3);

    const run = () => {
      const start = performance.now();
      const tick = (now) => {
        const progress = Math.min((now - start) / duration, 1);
        const value = Math.round(easeOut(progress) * target);
        el.textContent = `${value}${suffix}`;
        if (progress < 1) {
          window.requestAnimationFrame(tick);
        }
      };
      el.textContent = `0${suffix}`;
      window.requestAnimationFrame(tick);
    };

    if (delay) {
      window.setTimeout(run, delay);
    } else {
      run();
    }
  };

  const counters = document.querySelectorAll("[data-count]");
  if (counters.length) {
    if (window.matchMedia("(prefers-reduced-motion: reduce)").matches) {
      counters.forEach((el) => {
        el.textContent = `${el.dataset.count}${el.dataset.suffix || ""}`;
      });
    } else {
      const countObserver = new IntersectionObserver(
        (entries) => {
          entries.forEach((entry) => {
            if (!entry.isIntersecting) {
              return;
            }
            animateCount(entry.target, Number(entry.target.dataset.countDelay || 0));
            countObserver.unobserve(entry.target);
          });
        },
        { threshold: 0.45 }
      );
      counters.forEach((el) => countObserver.observe(el));
    }
  }

  document.addEventListener("click", (event) => {
    document.querySelectorAll(".custom-select.is-open").forEach((item) => {
      if (!item.contains(event.target)) {
        item.classList.remove("is-open");
        const trigger = item.querySelector(".custom-select-trigger");
        if (trigger) {
          trigger.setAttribute("aria-expanded", "false");
        }
      }
    });
  });

  document.addEventListener("keydown", (event) => {
    if (event.key === "Escape") {
      document.querySelectorAll(".custom-select.is-open").forEach((item) => {
        item.classList.remove("is-open");
        const trigger = item.querySelector(".custom-select-trigger");
        if (trigger) {
          trigger.setAttribute("aria-expanded", "false");
        }
      });
    }
  });

  const searchTabs = document.querySelectorAll("[data-search-tab]");
  if (searchTabs.length) {
    const searchForm = document.querySelector(".hero-search");
    searchTabs.forEach((tab) => {
      tab.addEventListener("click", () => {
        searchTabs.forEach((item) => {
          const active = item === tab;
          item.classList.toggle("is-active", active);
          item.setAttribute("aria-selected", active ? "true" : "false");
        });

        if (tab.dataset.searchTab === "browse" && searchForm) {
          searchForm.querySelectorAll("select").forEach((select) => {
            select.value = "";
          });
        }
      });
    });
  }

  const initLawyerCarousel = (root) => {
    const viewport = root.querySelector("[data-carousel-viewport]");
    const track = root.querySelector("[data-carousel-track]");
    const section = root.closest("section") || root;
    const prev = section.querySelector("[data-carousel-prev]");
    const next = section.querySelector("[data-carousel-next]");
    if (!viewport || !track) {
      return;
    }

    const originals = Array.from(track.children);
    const total = originals.length;
    const reduceMotion = window.matchMedia("(prefers-reduced-motion: reduce)").matches;
    const intervalMs = 3000;
    const cloneCount = Math.min(4, total);

    const visibleCount = () => {
      if (window.matchMedia("(max-width: 640px)").matches) {
        return 1;
      }
      if (window.matchMedia("(max-width: 1024px)").matches) {
        return 2;
      }
      return 4;
    };

    if (total <= 1) {
      if (prev) prev.hidden = true;
      if (next) next.hidden = true;
      return;
    }

    originals.slice(-cloneCount).forEach((slide) => {
      track.insertBefore(slide.cloneNode(true), track.firstChild);
    });
    originals.slice(0, cloneCount).forEach((slide) => {
      track.appendChild(slide.cloneNode(true));
    });

    let index = cloneCount;
    let animating = false;
    let timer = null;
    let hovering = false;

    const gap = () => {
      const value = Number.parseFloat(window.getComputedStyle(track).gap);
      return Number.isNaN(value) ? 0 : value;
    };

    const syncSlideSize = () => {
      const visible = visibleCount();
      const gutter = gap();
      const width = (viewport.clientWidth - gutter * (visible - 1)) / visible;
      Array.from(track.children).forEach((slide) => {
        slide.style.flexBasis = `${width}px`;
      });
    };

    const slideStep = () => {
      const slide = track.children[0];
      if (!slide) {
        return 0;
      }
      return slide.getBoundingClientRect().width + gap();
    };

    const setOffset = (nextIndex, animate) => {
      index = nextIndex;
      track.style.transition = animate && !reduceMotion
        ? "transform 0.55s cubic-bezier(0.22, 1, 0.36, 1)"
        : "none";
      track.style.transform = `translate3d(-${index * slideStep()}px, 0, 0)`;
    };

    const jumpTo = (nextIndex) => {
      setOffset(nextIndex, false);
      void track.offsetWidth;
    };

    const wrapIfNeeded = () => {
      if (index >= cloneCount + total) {
        jumpTo(cloneCount);
      } else if (index <= 0) {
        jumpTo(total);
      }
    };

    const go = (delta) => {
      if (animating) {
        return;
      }
      animating = true;
      setOffset(index + delta, true);
      if (reduceMotion) {
        animating = false;
        wrapIfNeeded();
        return;
      }
      window.setTimeout(() => {
        animating = false;
      }, 600);
    };

    const stop = () => {
      if (timer) {
        window.clearInterval(timer);
        timer = null;
      }
    };

    const play = () => {
      stop();
      if (reduceMotion || hovering || document.hidden) {
        return;
      }
      timer = window.setInterval(() => go(1), intervalMs);
    };

    track.addEventListener("transitionend", (event) => {
      if (event.target !== track || event.propertyName !== "transform") {
        return;
      }
      animating = false;
      wrapIfNeeded();
    });

    if (next) {
      next.addEventListener("click", () => {
        go(1);
        play();
      });
    }
    if (prev) {
      prev.addEventListener("click", () => {
        go(-1);
        play();
      });
    }

    viewport.addEventListener("mouseenter", () => {
      hovering = true;
      stop();
    });
    viewport.addEventListener("mouseleave", () => {
      hovering = false;
      play();
    });

    document.addEventListener("visibilitychange", () => {
      if (document.hidden) {
        stop();
      } else {
        play();
      }
    });

    window.addEventListener("resize", () => {
      syncSlideSize();
      jumpTo(index);
    });

    syncSlideSize();
    jumpTo(cloneCount);
    play();
    go(1);
  };

  document.querySelectorAll("[data-lawyer-carousel]").forEach(initLawyerCarousel);

  const reveals = document.querySelectorAll(".reveal");
  if (!reveals.length) {
    return;
  }

  if (window.matchMedia("(prefers-reduced-motion: reduce)").matches) {
    reveals.forEach((el) => el.classList.add("is-visible"));
    return;
  }

  const observer = new IntersectionObserver(
    (entries) => {
      entries.forEach((entry) => {
        if (entry.isIntersecting) {
          entry.target.classList.add("is-visible");
          observer.unobserve(entry.target);
        }
      });
    },
    { threshold: 0.14, rootMargin: "0px 0px -8% 0px" }
  );

  reveals.forEach((el) => observer.observe(el));
})();
