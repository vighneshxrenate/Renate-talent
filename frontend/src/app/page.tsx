"use client";

import Image from "next/image";
import { useCallback, useEffect, useRef, useState } from "react";
import SubmissionForm from "@/components/SubmissionForm";


// ── Parallax mouse hook ───────────────────────────────────────────────────────
function useMouseParallax(factor = 0.02) {
  const [offset, setOffset] = useState({ x: 0, y: 0 });
  useEffect(() => {
    const handle = (e: MouseEvent) => {
      const cx = window.innerWidth / 2;
      const cy = window.innerHeight / 2;
      setOffset({ x: (e.clientX - cx) * factor, y: (e.clientY - cy) * factor });
    };
    window.addEventListener("mousemove", handle, { passive: true });
    return () => window.removeEventListener("mousemove", handle);
  }, [factor]);
  return offset;
}

// ── Typing text hook ──────────────────────────────────────────────────────────
function useTypingText(texts: string[], speed = 80, pause = 2000) {
  const [displayText, setDisplayText] = useState("");
  const [textIndex, setTextIndex] = useState(0);
  const [charIndex, setCharIndex] = useState(0);
  const [isDeleting, setIsDeleting] = useState(false);

  useEffect(() => {
    const current = texts[textIndex];
    let timeout: ReturnType<typeof setTimeout>;
    if (!isDeleting && charIndex < current.length) {
      timeout = setTimeout(() => setCharIndex((c) => c + 1), speed);
    } else if (!isDeleting && charIndex === current.length) {
      timeout = setTimeout(() => setIsDeleting(true), pause);
    } else if (isDeleting && charIndex > 0) {
      timeout = setTimeout(() => setCharIndex((c) => c - 1), speed / 2);
    } else if (isDeleting && charIndex === 0) {
      setIsDeleting(false);
      setTextIndex((i) => (i + 1) % texts.length);
    }
    setDisplayText(current.substring(0, charIndex));
    return () => clearTimeout(timeout);
  }, [charIndex, isDeleting, textIndex, texts, speed, pause]);

  return displayText;
}

// ── Sparkle burst ─────────────────────────────────────────────────────────────
interface SparkleParticle {
  id: number; x: number; y: number;
  size: number; delay: number; color: string; duration: number;
}

function SparkleBurst({ trigger }: { trigger: number }) {
  const [particles, setParticles] = useState<SparkleParticle[]>([]);

  useEffect(() => {
    if (!trigger) return;
    const colors = ["#7c3aed", "#8b5cf6", "#a78bfa", "#c4b5fd", "#ddd6fe", "#6d28d9"];
    const ps: SparkleParticle[] = Array.from({ length: 28 }, (_, i) => {
      const angle = (i / 28) * Math.PI * 2 + (Math.random() - 0.5) * 0.5;
      const dist = 90 + Math.random() * 180;
      return {
        id: i,
        x: Math.cos(angle) * dist,
        y: Math.sin(angle) * dist,
        size: 4 + Math.random() * 9,
        delay: Math.random() * 0.28,
        color: colors[Math.floor(Math.random() * colors.length)],
        duration: 0.65 + Math.random() * 0.55,
      };
    });
    setParticles(ps);
    const t = setTimeout(() => setParticles([]), 1600);
    return () => clearTimeout(t);
  }, [trigger]);

  if (!particles.length) return null;

  return (
    <div
      style={{
        position: "fixed", left: "50%", top: "50%",
        pointerEvents: "none", zIndex: 500,
        transform: "translate(-50%, -50%)",
      }}
    >
      {particles.map((p) => (
        <div
          key={p.id}
          style={{
            position: "absolute",
            left: -p.size / 2, top: -p.size / 2,
            width: p.size, height: p.size,
            borderRadius: "50%",
            background: `radial-gradient(circle, ${p.color}, ${p.color}88)`,
            boxShadow: `0 0 ${p.size * 2}px ${p.color}`,
            animation: `sparkle-burst-out ${p.duration}s ease-out ${p.delay}s both`,
            ["--tx" as string]: `${p.x}px`,
            ["--ty" as string]: `${p.y}px`,
          } as React.CSSProperties}
        />
      ))}
    </div>
  );
}

// ── Modal ─────────────────────────────────────────────────────────────────────
function FormModal({
  mounted, visible, onClose, sparkleCount,
}: {
  mounted: boolean; visible: boolean; onClose: () => void; sparkleCount: number;
}) {
  if (!mounted) return null;

  return (
    <>
      <SparkleBurst trigger={sparkleCount} />
      <div
        className={`modal-overlay${visible ? " open" : ""}`}
        onClick={onClose}
        role="dialog"
        aria-modal="true"
        aria-label="Submit your resume"
      >
        <div className="modal-panel" onClick={(e) => e.stopPropagation()}>
          {/* Animated shimmer bar */}
          <div className="shimmer-bar" />

          {/* Close button */}
          <button
            onClick={onClose}
            aria-label="Close"
            style={{
              position: "absolute", top: "1rem", right: "1rem", zIndex: 10,
              width: 36, height: 36, borderRadius: "50%",
              background: "#f5f3ff", border: "none", cursor: "pointer",
              display: "flex", alignItems: "center", justifyContent: "center",
              fontSize: "1.125rem", color: "#6b7280",
              transition: "background 0.2s ease, color 0.2s ease, transform 0.3s cubic-bezier(.34,1.56,.64,1)",
            }}
            onMouseEnter={(e) => {
              const btn = e.currentTarget as HTMLButtonElement;
              btn.style.background = "#ede9fe";
              btn.style.color = "#7c3aed";
              btn.style.transform = "rotate(90deg) scale(1.15)";
            }}
            onMouseLeave={(e) => {
              const btn = e.currentTarget as HTMLButtonElement;
              btn.style.background = "#f5f3ff";
              btn.style.color = "#6b7280";
              btn.style.transform = "rotate(0deg) scale(1)";
            }}
          >
            ✕
          </button>

          {/* Decorative gradient ring behind header */}
          <div
            style={{
              position: "absolute", top: -60, left: "50%", transform: "translateX(-50%)",
              width: 240, height: 240, borderRadius: "50%",
              background: "radial-gradient(circle, rgba(124,58,237,0.12) 0%, rgba(167,139,250,0.06) 50%, transparent 70%)",
              filter: "blur(20px)", pointerEvents: "none",
            }}
          />

          {/* Header */}
          <div style={{ padding: "2.5rem 2rem 0", textAlign: "center", position: "relative" }}>
            {/* Icon orb */}
            <div
              style={{
                width: 60, height: 60, borderRadius: "50%",
                background: "linear-gradient(135deg, #7c3aed 0%, #a78bfa 100%)",
                margin: "0 auto 1rem",
                display: "flex", alignItems: "center", justifyContent: "center",
                fontSize: "1.625rem",
                boxShadow: "0 8px 32px rgba(124,58,237,0.4), 0 0 0 8px rgba(124,58,237,0.08)",
                animation: visible ? "modal-icon-pop 0.55s cubic-bezier(.34,1.56,.64,1) 0.32s both" : "none",
              }}
            >
              ✦
            </div>

            <span
              className="font-display"
              style={{
                color: "#7c3aed", fontSize: "0.75rem", fontWeight: 600,
                letterSpacing: "0.14em", textTransform: "uppercase",
                display: "block",
                animation: visible ? "fade-up 0.4s ease 0.42s both" : "none",
              }}
            >
              Get Started
            </span>

            <h2
              className="font-display"
              style={{
                fontSize: "clamp(1.5rem, 3vw, 2.25rem)", fontWeight: 800,
                letterSpacing: "-0.02em", marginTop: "0.5rem", marginBottom: "0.375rem",
                color: "#0f0a1e",
                animation: visible ? "fade-up 0.4s ease 0.48s both" : "none",
              }}
            >
              Submit Your{" "}
              <span className="text-gradient-violet">Resume</span>
            </h2>

            <p
              style={{
                color: "#6b7280", fontSize: "0.9375rem", lineHeight: 1.6, marginBottom: "1.5rem",
                animation: visible ? "fade-up 0.4s ease 0.54s both" : "none",
              }}
            >
              Let Renate AI match you with the right employers.
            </p>
          </div>

          {/* Gradient divider */}
          <div
            style={{
              height: 1,
              background: "linear-gradient(90deg, transparent, rgba(124,58,237,0.2), transparent)",
              margin: "0 2rem",
            }}
          />

          <div
            className="p-6 sm:p-8"
            style={{ animation: visible ? "fade-up 0.5s ease 0.58s both" : "none" }}
          >
            <SubmissionForm />
          </div>
        </div>
      </div>
    </>
  );
}

// ── Navbar ────────────────────────────────────────────────────────────────────
function Navbar() {
  const [scrolled, setScrolled] = useState(false);
  const [scrollProgress, setScrollProgress] = useState(0);

  useEffect(() => {
    const onScroll = () => {
      setScrolled(window.scrollY > 24);
      const totalHeight = document.body.scrollHeight - window.innerHeight;
      setScrollProgress(totalHeight > 0 ? (window.scrollY / totalHeight) * 100 : 0);
    };
    window.addEventListener("scroll", onScroll, { passive: true });
    return () => window.removeEventListener("scroll", onScroll);
  }, []);

  return (
    <nav
      style={{
        position: "fixed", top: 0, left: 0, right: 0, zIndex: 100,
        padding: scrolled ? "0.75rem 1.5rem" : "1rem 1.5rem",
        transition: "all 0.35s ease",
        ...(scrolled
          ? {
              background: "rgba(255,255,255,0.92)",
              backdropFilter: "blur(20px) saturate(180%)",
              WebkitBackdropFilter: "blur(20px) saturate(180%)",
              borderBottom: "1px solid rgba(124,58,237,0.12)",
              boxShadow: "0 4px 24px rgba(124,58,237,0.08)",
            }
          : {
              background: "transparent",
              borderBottom: "1px solid transparent",
            }),
      }}
    >
      {/* Scroll progress bar */}
      <div
        style={{
          position: "absolute", top: 0, left: 0, height: 2,
          width: `${scrollProgress}%`,
          background: "linear-gradient(90deg, #7c3aed, #a78bfa, #c4b5fd)",
          transition: "width 0.1s linear",
        }}
      />

      <div
        style={{
          maxWidth: "72rem", margin: "0 auto",
          display: "flex", alignItems: "center",
        }}
      >
        {/* Logo */}
        <div
          style={{
            flexShrink: 0, borderRadius: 8,
            transition: "transform 0.3s ease",
          }}
          onMouseEnter={(e) => (e.currentTarget.style.transform = "scale(1.05)")}
          onMouseLeave={(e) => (e.currentTarget.style.transform = "scale(1)")}
        >
          <Image src="/logo.jpeg" alt="Renate AI" width={160} height={48} className="object-contain" style={{ objectPosition: "left" }} priority />
        </div>
      </div>
    </nav>
  );
}

// ── Floating Particles ────────────────────────────────────────────────────────
function FloatingParticles() {
  const particles = Array.from({ length: 20 }, (_, i) => ({
    id: i,
    left: `${(i * 5.3 + 2) % 100}%`,
    top: `${(i * 7.1 + 3) % 100}%`,
    size: 4 + (i % 4) * 2,
    delay: (i * 0.41) % 6,
    duration: 6 + (i % 4) * 2,
    opacity: 0.15 + (i % 3) * 0.08,
  }));

  return (
    <>
      {particles.map((p) => (
        <div
          key={p.id}
          style={{
            position: "absolute",
            left: p.left, top: p.top,
            width: p.size, height: p.size,
            borderRadius: "50%",
            background: `radial-gradient(circle, rgba(124,58,237,${p.opacity}), rgba(139,92,246,${p.opacity * 0.5}))`,
            animation: `particle-float ${p.duration}s ease-in-out infinite`,
            animationDelay: `${p.delay}s`,
            pointerEvents: "none",
          }}
        />
      ))}
    </>
  );
}

// ── Hero ──────────────────────────────────────────────────────────────────────
function Hero({ onOpen }: { onOpen: () => void }) {
  const mouse = useMouseParallax(0.015);
  const typingText = useTypingText(
    ["a Job?", "an Internship?", "Career Growth?", "Your Dream Role?"],
    90,
    2200
  );

  return (
    <section
      style={{
        position: "relative", minHeight: "100vh",
        display: "flex", flexDirection: "column",
        alignItems: "center", justifyContent: "center",
        overflow: "hidden", background: "#ffffff",
      }}
    >
      {/* Dot grid */}
      <div className="bg-dots" style={{ position: "absolute", inset: 0, pointerEvents: "none", opacity: 0.7 }} />

      <FloatingParticles />

      {/* Morphing blobs with mouse parallax */}
      <div
        className="animate-morph-blob"
        style={{
          position: "absolute", top: "8%", left: "3%",
          width: 420, height: 420,
          background: "radial-gradient(circle, rgba(124,58,237,0.14) 0%, transparent 70%)",
          filter: "blur(56px)", pointerEvents: "none",
          transform: `translate(${mouse.x * 1.5}px, ${mouse.y * 1.5}px)`,
          transition: "transform 0.3s ease-out",
        }}
      />
      <div
        className="animate-morph-blob"
        style={{
          position: "absolute", top: "12%", right: "2%",
          width: 500, height: 500,
          background: "radial-gradient(circle, rgba(139,92,246,0.10) 0%, transparent 70%)",
          filter: "blur(64px)", pointerEvents: "none",
          animationDelay: "4s", animationDirection: "reverse",
          transform: `translate(${mouse.x * -1.2}px, ${mouse.y * -1.2}px)`,
          transition: "transform 0.3s ease-out",
        }}
      />
      <div
        className="animate-float-a"
        style={{
          position: "absolute", bottom: "15%", left: "25%",
          width: 560, height: 280,
          background: "radial-gradient(ellipse, rgba(109,40,217,0.07) 0%, transparent 70%)",
          filter: "blur(72px)", pointerEvents: "none", animationDelay: "4s",
          transform: `translate(${mouse.x * 0.8}px, ${mouse.y * 0.8}px)`,
          transition: "transform 0.3s ease-out",
        }}
      />
      {/* Extra violet-light orb */}
      <div
        className="animate-float-b"
        style={{
          position: "absolute", top: "55%", left: "60%",
          width: 320, height: 320,
          background: "radial-gradient(circle, rgba(196,181,253,0.12) 0%, transparent 70%)",
          filter: "blur(48px)", pointerEvents: "none", animationDelay: "2s",
          transform: `translate(${mouse.x * 0.6}px, ${mouse.y * 0.6}px)`,
          transition: "transform 0.3s ease-out",
        }}
      />

      {/* Content */}
      <div
        style={{
          position: "relative", zIndex: 10, textAlign: "center",
          padding: "0 1.5rem", maxWidth: "64rem", margin: "0 auto", paddingTop: "7rem",
        }}
      >
        {/* Badge */}
        <div
          className="animate-fade-up"
          style={{
            display: "inline-flex", alignItems: "center", gap: "0.5rem",
            background: "rgba(245,243,255,0.85)", border: "1px solid rgba(124,58,237,0.25)",
            borderRadius: "9999px", padding: "0.375rem 1rem", marginBottom: "2rem",
            backdropFilter: "blur(10px)",
          }}
        >
          <span
            className="animate-pulse-glow"
            style={{
              width: 8, height: 8, borderRadius: "50%",
              background: "#7c3aed", display: "inline-block",
            }}
          />
          <span className="font-display" style={{ color: "#7c3aed", fontSize: "0.8125rem", fontWeight: 600 }}>
            AI-Powered Talent Matching Platform
          </span>
        </div>

        {/* Headline */}
        <h1
          className="font-display animate-fade-up delay-100"
          style={{
            fontSize: "clamp(2.75rem, 7vw, 5.5rem)", fontWeight: 800,
            lineHeight: 1.06, letterSpacing: "-0.03em", marginBottom: "1.5rem",
            color: "#0f0a1e",
          }}
        >
          <span className="text-gradient-violet">Looking for</span>
          <br />
          <span className="typing-cursor" style={{ color: "#0f0a1e" }}>{typingText || "\u00A0"}</span>
          <br />
          <span className="text-gradient-shimmer-violet">Renate</span>
          <br />
          <span style={{ color: "#0f0a1e" }}>Will Help You.</span>
        </h1>

        {/* Subheadline */}
        <p
          className="animate-fade-up delay-200"
          style={{
            fontSize: "clamp(1rem, 2.5vw, 1.25rem)",
            color: "#64748b", maxWidth: 560, margin: "0 auto 2.5rem",
            lineHeight: 1.75, fontWeight: 400,
          }}
        >
          Renate AI intelligently matches your resume with the right employers
          across 36 industries.
        </p>

        {/* CTAs */}
        <div
          className="animate-fade-up delay-300 hero-cta-group"
          style={{
            display: "flex", flexWrap: "wrap", gap: "1rem",
            justifyContent: "center", alignItems: "center",
          }}
        >
          <button
            className="btn-primary"
            onClick={onOpen}
            style={{ fontSize: "1rem", padding: "1rem 2.5rem" }}
          >
            Submit Your Resume
          </button>
        </div>

        {/* Trust indicators */}
        <div
          className="animate-fade-up delay-400 hero-trust-grid"
          style={{
            display: "flex", alignItems: "center", justifyContent: "center",
            gap: "1.5rem", marginTop: "3rem", flexWrap: "wrap",
          }}
        >
          {["50k+ Professionals Placed", "36 Industries", "Free for Students"].map((item, i) => (
            <div
              key={item}
              style={{
                display: "flex", alignItems: "center", gap: "0.375rem",
                color: "#94a3b8", fontSize: "0.875rem",
                animation: `fade-up 0.5s cubic-bezier(.22,1,.36,1) ${0.6 + i * 0.1}s both`,
              }}
            >
              <svg width="14" height="14" viewBox="0 0 14 14" fill="none">
                <path d="M2 7L5.5 10.5L12 3.5" stroke="#8b5cf6" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" />
              </svg>
              {item}
            </div>
          ))}
        </div>
      </div>

      {/* Scroll indicator */}
      <div
        className="animate-fade-up delay-500 animate-bounce-soft"
        style={{
          position: "absolute", bottom: "2.5rem",
          display: "flex", flexDirection: "column", alignItems: "center", gap: "0.375rem",
          color: "#94a3b8", pointerEvents: "none",
        }}
      >
        <span
          className="font-display"
          style={{ fontSize: "0.6875rem", letterSpacing: "0.12em", textTransform: "uppercase" }}
        >
          Scroll
        </span>
        <svg width="18" height="18" viewBox="0 0 18 18" fill="none">
          <path d="M4 6.5L9 11.5L14 6.5" stroke="#94a3b8" strokeWidth="1.5" strokeLinecap="round" strokeLinejoin="round" />
        </svg>
      </div>

      {/* Bottom fade */}
      <div
        style={{
          position: "absolute", bottom: 0, left: 0, right: 0, height: 120,
          background: "linear-gradient(to bottom, transparent, rgba(245,243,255,0.2))",
          pointerEvents: "none",
        }}
      />
    </section>
  );
}


// ── Page ──────────────────────────────────────────────────────────────────────
export default function Home() {
  const [modalMounted, setModalMounted] = useState(false);
  const [modalVisible, setModalVisible] = useState(false);
  const [sparkleCount, setSparkleCount] = useState(0);
  const closeTimer = useRef<ReturnType<typeof setTimeout> | null>(null);

  const openModal = useCallback(() => {
    if (closeTimer.current) clearTimeout(closeTimer.current);
    setModalMounted(true);
    requestAnimationFrame(() => {
      requestAnimationFrame(() => {
        setModalVisible(true);
        setSparkleCount((n) => n + 1);
        document.body.classList.add("modal-open");
      });
    });
  }, []);

  const closeModal = useCallback(() => {
    setModalVisible(false);
    document.body.classList.remove("modal-open");
    closeTimer.current = setTimeout(() => setModalMounted(false), 380);
  }, []);

  useEffect(() => {
    const onKey = (e: KeyboardEvent) => {
      if (e.key === "Escape" && modalVisible) closeModal();
    };
    document.addEventListener("keydown", onKey);
    return () => document.removeEventListener("keydown", onKey);
  }, [modalVisible, closeModal]);

  useEffect(() => {
    const selectors = ".reveal, .reveal-left, .reveal-right, .reveal-scale";
    const els = document.querySelectorAll(selectors);
    if (!els.length) return;
    const io = new IntersectionObserver(
      (entries) => {
        entries.forEach((entry) => {
          if (entry.isIntersecting) {
            entry.target.classList.add("visible");
            io.unobserve(entry.target);
          }
        });
      },
      { threshold: 0.12 }
    );
    els.forEach((el) => io.observe(el));
    return () => io.disconnect();
  }, []);

  useEffect(() => {
    return () => {
      if (closeTimer.current) clearTimeout(closeTimer.current);
      document.body.classList.remove("modal-open");
    };
  }, []);

  return (
    <>
      <main style={{ background: "#ffffff" }}>
        <Navbar />
        <Hero onOpen={openModal} />
      </main>

      <FormModal
        mounted={modalMounted}
        visible={modalVisible}
        onClose={closeModal}
        sparkleCount={sparkleCount}
      />
    </>
  );
}
