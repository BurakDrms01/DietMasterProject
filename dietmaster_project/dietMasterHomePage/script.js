document.addEventListener("DOMContentLoaded", () => {
  // Sayfa yenilendiğinde en başa sar
  if (history.scrollRestoration) {
    history.scrollRestoration = "manual";
  }
  window.scrollTo(0, 0);

  // --- 1. Mobil Menü Toggle ---
  const btn = document.getElementById("mobile-menu-btn");
  const menu = document.getElementById("mobile-menu");

  btn.addEventListener("click", () => {
    menu.classList.toggle("hidden");
  });

  // --- 2. Navbar Scroll Efekti ---
  const navbar = document.getElementById("navbar");

  window.addEventListener("scroll", () => {
    if (window.scrollY > 50) {
      navbar.classList.add("scrolled");
    } else {
      navbar.classList.remove("scrolled");
    }
  });

  // --- 3. FAQ Accordion Mantığı ---
  const faqButtons = document.querySelectorAll(".faq-btn");

  faqButtons.forEach((button) => {
    button.addEventListener("click", () => {
      const item = button.closest(".faq-item");
      const content = button.nextElementSibling;
      const icon = button.querySelector("i");

      // Diğerlerini kapat
      document.querySelectorAll(".faq-item").forEach((otherItem) => {
        if (otherItem !== item) {
          const otherContent = otherItem.querySelector(".faq-content");
          const otherIcon = otherItem.querySelector("i");

          otherContent.classList.add("hidden");
          otherIcon.classList.remove("fa-minus");
          otherIcon.classList.add("fa-plus");

          // Reset styles
          otherItem.classList.remove(
            "bg-white",
            "border-2",
            "border-indigo-600",
            "shadow-lg"
          );
          otherItem.classList.add(
            "bg-gray-50",
            "border-transparent",
            "hover:bg-gray-100"
          );
        }
      });

      // Tıklananı aç/kapa
      content.classList.toggle("hidden");

      if (!content.classList.contains("hidden")) {
        // Açık Durum
        icon.classList.remove("fa-plus");
        icon.classList.add("fa-minus");

        item.classList.remove(
          "bg-gray-50",
          "border-transparent",
          "hover:bg-gray-100"
        );
        item.classList.add(
          "bg-white",
          "border-2",
          "border-indigo-600",
          "shadow-lg"
        );
      } else {
        // Kapalı Durum
        icon.classList.remove("fa-minus");
        icon.classList.add("fa-plus");

        item.classList.remove(
          "bg-white",
          "border-2",
          "border-indigo-600",
          "shadow-lg"
        );
        item.classList.add(
          "bg-gray-50",
          "border-transparent",
          "hover:bg-gray-100"
        );
      }
    });
  });

  // --- 3.5 FAQ Category Filtering ---
  const categoryButtons = document.querySelectorAll(".category-btn");
  const faqItems = document.querySelectorAll(".faq-item");

  categoryButtons.forEach((btn) => {
    btn.addEventListener("click", () => {
      // 1. Update Button Styles
      categoryButtons.forEach((b) => {
        b.classList.remove(
          "bg-indigo-50",
          "text-indigo-700",
          "font-bold",
          "border-indigo-600"
        );
        b.classList.add(
          "text-gray-600",
          "hover:bg-gray-50",
          "hover:text-gray-900",
          "border-transparent"
        );
      });

      btn.classList.remove(
        "text-gray-600",
        "hover:bg-gray-50",
        "hover:text-gray-900",
        "border-transparent"
      );
      btn.classList.add(
        "bg-indigo-50",
        "text-indigo-700",
        "font-bold",
        "border-indigo-600"
      );

      // 2. Filter Items
      const category = btn.getAttribute("data-category");

      faqItems.forEach((item) => {
        if (item.getAttribute("data-category") === category) {
          item.classList.remove("hidden");
        } else {
          item.classList.add("hidden");
        }
      });
    });
  });

  // --- 4. Smooth Scroll for Anchor Links ---
  document.querySelectorAll('a[href^="#"]').forEach((anchor) => {
    anchor.addEventListener("click", function (e) {
      e.preventDefault();
      const targetId = this.getAttribute("href").substring(1);
      const targetElement = document.getElementById(targetId);

      if (targetElement) {
        // CSS scroll-padding-top ile uyumlu çalışır
        targetElement.scrollIntoView({
          behavior: "smooth",
          block: "start",
        });
      }
    });
  });

  // --- 5. Before/After Slider Logic ---
  const track = document.getElementById("slider-track");
  const prevBtn = document.getElementById("prev-slide");
  const nextBtn = document.getElementById("next-slide");
  const dots = document.getElementById("slider-dots").children;

  if (track && prevBtn && nextBtn) {
    let currentIndex = 0;
    const slideCount = track.children.length;

    function updateSlider() {
      track.style.transform = `translateX(-${currentIndex * 100}%)`;

      // Update dots
      Array.from(dots).forEach((dot, index) => {
        if (index === currentIndex) {
          dot.classList.remove("bg-gray-300");
          dot.classList.add("bg-indigo-600");
        } else {
          dot.classList.add("bg-gray-300");
          dot.classList.remove("bg-indigo-600");
        }
      });
    }

    function nextSlide() {
      currentIndex = (currentIndex + 1) % slideCount;
      updateSlider();
    }

    function prevSlide() {
      currentIndex = (currentIndex - 1 + slideCount) % slideCount;
      updateSlider();
    }

    nextBtn.addEventListener("click", () => {
      nextSlide();
      resetInterval();
    });

    prevBtn.addEventListener("click", () => {
      prevSlide();
      resetInterval();
    });

    // Auto play
    let slideInterval = setInterval(nextSlide, 5000);

    function resetInterval() {
      clearInterval(slideInterval);
      slideInterval = setInterval(nextSlide, 5000);
    }

    // Pause on hover
    const sliderContainer = document.querySelector(
      "#degisimler .overflow-hidden"
    );
    if (sliderContainer) {
      sliderContainer.addEventListener("mouseenter", () => {
        clearInterval(slideInterval);
      });
      sliderContainer.addEventListener("mouseleave", () => {
        resetInterval();
      });
    }

    // Dot navigation
    Array.from(dots).forEach((dot, index) => {
      dot.addEventListener("click", () => {
        currentIndex = index;
        updateSlider();
        resetInterval();
      });
    });
  }

  // --- 6. Statistics Counter Animation ---
  const statsSection = document.getElementById("stats-section");
  const counters = document.querySelectorAll(".counter");
  const statItems = document.querySelectorAll(".stat-item");
  let started = false; // Function should run only once

  if (statsSection && counters.length > 0) {
    const observer = new IntersectionObserver(
      (entries) => {
        entries.forEach((entry) => {
          if (entry.isIntersecting && !started) {
            started = true;

            // 1. Fade In Animation
            statItems.forEach((item) => {
              item.classList.remove("opacity-0", "translate-y-4");
            });

            // 2. Number Counting Animation
            counters.forEach((counter) => {
              const target = +counter.getAttribute("data-target");
              const duration = 2000; // 2 seconds
              const increment = target / (duration / 16); // 60fps

              let current = 0;
              const updateCounter = () => {
                current += increment;
                if (current < target) {
                  counter.innerText = Math.ceil(current);
                  requestAnimationFrame(updateCounter);
                } else {
                  counter.innerText = target;
                }
              };
              updateCounter();
            });
          }
        });
      },
      { threshold: 0.5 } // Trigger when 50% of the section is visible
    );

    observer.observe(statsSection);
  }

  // --- 7. Hero Card Animation ---
  const heroCard = document.getElementById("hero-stat-card");
  if (heroCard) {
    const numberEl = document.getElementById("hero-stat-number");
    const linePath = document.getElementById("hero-graph-line");
    const areaPath = document.getElementById("hero-graph-area");
    const dot = document.getElementById("hero-graph-dot");
    const badge = document.getElementById("hero-success-badge");

    // Initial State Setup
    const pathLength = linePath.getTotalLength();
    linePath.style.strokeDasharray = pathLength;
    linePath.style.strokeDashoffset = pathLength;

    // Wait a bit for the page to load/bounce animation to settle slightly
    setTimeout(() => {
      // 1. Animate Number (0.0 to -4.2)
      let startTimestamp = null;
      const duration = 2000; // 2 seconds
      const startValue = 0.0;
      const endValue = -4.2;

      function step(timestamp) {
        if (!startTimestamp) startTimestamp = timestamp;
        const progress = Math.min((timestamp - startTimestamp) / duration, 1);

        // Easing function for smoother effect (easeOutQuart)
        const easeProgress = 1 - Math.pow(1 - progress, 4);

        const currentValue = (
          startValue +
          (endValue - startValue) * easeProgress
        ).toFixed(1);
        numberEl.textContent = currentValue;

        if (progress < 1) {
          window.requestAnimationFrame(step);
        }
      }
      window.requestAnimationFrame(step);

      // 2. Animate Graph Line Drawing
      // We use a transition for the stroke-dashoffset
      linePath.style.transition = "stroke-dashoffset 2s ease-out";
      linePath.style.strokeDashoffset = "0";

      // 3. Fade in Area and Dot
      setTimeout(() => {
        areaPath.classList.remove("opacity-0");
        areaPath.classList.add("opacity-100");
        dot.classList.remove("opacity-0");
        dot.classList.add("opacity-100");
      }, 1500); // Start fading in towards the end of the line draw

      // 4. Show Success Badge
      setTimeout(() => {
        badge.classList.remove("opacity-0", "translate-y-2");
      }, 2000); // Show after graph finishes
    }, 500); // 500ms initial delay
  }
});
