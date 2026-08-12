(() => {
  const header = document.querySelector("[data-header]");
  const toggle = document.querySelector("[data-nav-toggle]");
  const nav = document.querySelector("[data-nav]");

  if (header) {
    const onScroll = () => {
      header.classList.toggle("is-scrolled", window.scrollY > 8);
    };
    onScroll();
    window.addEventListener("scroll", onScroll, { passive: true });
  }

  if (toggle && nav && header) {
    const setOpen = (open) => {
      header.classList.toggle("nav-open", open);
      toggle.setAttribute("aria-expanded", open ? "true" : "false");
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
