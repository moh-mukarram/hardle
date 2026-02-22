<script lang="ts">
  import {
    Settings,
    Menu,
    X,
    Terminal,
    ChevronRight,
    Power,
    ChevronDown,
    ChevronUp,
    ArrowRight,
  } from "lucide-svelte";
  import { onMount, onDestroy } from "svelte";
  import { goto } from "$app/navigation";
  import { userStore } from "$lib/stores/user";

  let selectedMode: "normal" | "hard" | "extreme" = "normal";
  let isMobileMenuOpen = false;
  let areLogsOpen = false;
  let pointsDisplay = 10;

  // Slide to activate states
  let dragElement: HTMLElement;
  let trackElement: HTMLElement;
  let isDragging = false;
  let startX = 0;
  let currentX = 0;
  let maxSlidable = 0;
  let slidingBack = false;

  // Modal states
  let isSettingsOpen = false;
  let isTerminateOpen = false;

  // Settings states
  let volume = 75;
  let sfxEnabled = true;
  let vibrationEnabled = true;
  let hapticIntensity: "low" | "medium" | "high" = "medium";
  let reduceMotion = false;
  let highContrast = false;

  const logs = [
    {
      date: "04.23.24",
      status: "CLEARANCE SUCCESS",
      points: "+10",
      type: "success",
    },
    { date: "04.23.24", status: "BREACH FAILED", points: "-5", type: "fail" },
    {
      date: "04.22.24",
      status: "CLEARANCE SUCCESS",
      points: "+20",
      type: "success",
    },
    {
      date: "04.22.24",
      status: "CLEARANCE SUCCESS",
      points: "+10",
      type: "success",
    },
    { date: "04.22.24", status: "BREACH FAILED", points: "-10", type: "fail" },
  ];

  type ProtocolNode = {
    mode: "normal" | "hard" | "extreme";
    title: string;
    points: number;
    description: string;
    colorClass: string;
    borderColorClass: string;
  };

  const protocols: ProtocolNode[] = [
    {
      mode: "normal",
      title: "NORMAL PROTOCOL",
      points: 10,
      description:
        "Standard decryption process. Visual signal intelligence active.",
      colorClass: "text-cyan-300",
      borderColorClass: "border-cyan-500/60",
    },
    {
      mode: "hard",
      title: "HARD PROTOCOL",
      points: 18,
      description: "Verified signals only. Partial signals suppressed.",
      colorClass: "text-cyan-300",
      borderColorClass:
        "border-cyan-400 shadow-[0_0_10px_rgba(34,211,238,0.2)]",
    },
    {
      mode: "extreme",
      title: "EXTREME PROTOCOL",
      points: 25,
      description: "Zero signal intelligence. Blind decryption required.",
      colorClass: "text-amber-500",
      borderColorClass: "border-amber-500/60",
    },
  ];

  const mobileProtocols: ProtocolNode[] = [
    {
      mode: "normal",
      title: "NORMAL",
      points: 10,
      description: "Visual signal intel active.",
      colorClass: "text-cyan-300",
      borderColorClass: "border-cyan-500/60",
    },
    {
      mode: "hard",
      title: "HARD",
      points: 18,
      description: "Verified signals only.",
      colorClass: "text-cyan-300",
      borderColorClass: "border-cyan-400",
    },
    {
      mode: "extreme",
      title: "EXTREME",
      points: 25,
      description: "Zero signal intel.",
      colorClass: "text-amber-500",
      borderColorClass: "border-amber-500/60",
    },
  ];

  let flickerInterval: ReturnType<typeof setInterval>;

  $: {
    const targetPoints =
      selectedMode === "normal" ? 10 : selectedMode === "hard" ? 18 : 25;
    let flickerCount = 0;
    const maxFlickers = 6;

    if (flickerInterval) clearInterval(flickerInterval);

    flickerInterval = setInterval(() => {
      if (flickerCount < maxFlickers) {
        pointsDisplay = Math.floor(Math.random() * 99);
        flickerCount++;
      } else {
        pointsDisplay = targetPoints;
        clearInterval(flickerInterval);
      }
    }, 40);
  }

  onDestroy(() => {
    if (flickerInterval) clearInterval(flickerInterval);
  });
  function startDrag(e: PointerEvent) {
    if (slidingBack || !dragElement || !trackElement) return;
    isDragging = true;
    startX = e.clientX;
    const trackRect = trackElement.getBoundingClientRect();
    const handleRect = dragElement.getBoundingClientRect();
    // Use container width minus handle width and margins
    maxSlidable = trackRect.width - handleRect.width - 4;
    dragElement.setPointerCapture(e.pointerId);
  }

  function onDrag(e: PointerEvent) {
    if (!isDragging) return;
    e.preventDefault();
    const delta = e.clientX - startX;
    // Bound movement between 0 and maximum slidable width
    currentX = Math.max(0, Math.min(delta, maxSlidable));
  }

  function stopDrag(e: PointerEvent) {
    if (!isDragging) return;
    isDragging = false;
    dragElement.releasePointerCapture(e.pointerId);

    // 90% threshold for activation
    if (currentX >= maxSlidable * 0.9) {
      currentX = maxSlidable; // Snap to end
      goto("/game");
    } else {
      // Revert smoothly
      slidingBack = true;
      currentX = 0;
      setTimeout(() => {
        slidingBack = false;
      }, 300); // Wait for transition to finish
    }
  }
</script>

<div
  class="fixed inset-0 z-50 bg-[#050C14] bg-gradient-to-b from-[#050C14] to-[#0A1622] text-cyan-400 font-mono overflow-auto flex flex-col"
>
  <!-- Background Effects -->
  <div
    class="absolute inset-0 pointer-events-none opacity-[0.03] bg-[url('data:image/svg+xml;base64,PHN2ZyB4bWxucz0naHR0cDovL3d3dy53My5vcmcvMjAwMC9zdmcnIHdpZHRoPScyMDAlJyBoZWlnaHQ9JzIwMCUnPjxmaWx0ZXIgaWQ9J25vaXNlJz48ZmVUdXJidWxlbmNlIHR5cGU9J2ZyYWN0YWxOb2lzZScgYmFzZUZyZXF1ZW5jeT0nMC42NSBzdGl0Y2hUaWxlcz0nc3RpdGNoJy8+PC9maWx0ZXI+PHJlY3Qgd2lkdGg9JzEwMCUnIGhlaWdodD0nMTAwJScgZmlsdGVyPSd1cmwoI25vaXNlKScgb3BhY2l0eT0nMC40Jy8+PC9zdmc+')] mix-blend-overlay"
  ></div>
  <div
    class="hidden lg:block absolute inset-0 pointer-events-none bg-[linear-gradient(rgba(18,16,16,0)_50%,rgba(0,0,0,0.1)_50%),linear-gradient(90deg,rgba(255,0,0,0.03),rgba(0,255,0,0.01),rgba(0,0,255,0.03))] z-1 bg-[length:100%_2px,3px_100%]"
  ></div>

  <!-- MOBILE LAYOUT -->
  <div class="lg:hidden flex flex-col h-full w-full">
    <!-- TOP BAR -->
    <header
      class="relative z-20 flex items-center justify-between px-4 py-3 border-b border-cyan-900/30 bg-[#050C14]/90 backdrop-blur-md h-[50px] shrink-0"
    >
      <div class="flex items-center gap-3">
        <button
          on:click={() => (isMobileMenuOpen = !isMobileMenuOpen)}
          class="text-cyan-500 hover:text-cyan-300 transition-colors"
        >
          {#if isMobileMenuOpen}
            <X class="w-5 h-5" />
          {:else}
            <Menu class="w-5 h-5" />
          {/if}
        </button>
        <h1
          class="text-sm tracking-[0.2em] font-bold text-cyan-100 drop-shadow-[0_0_8px_rgba(34,211,238,0.3)]"
        >
          HARDLE
        </h1>
      </div>

      <button
        on:click={() => (isSettingsOpen = true)}
        class="text-cyan-600 hover:text-cyan-400 transition-colors"
      >
        <Settings class="w-4 h-4" />
      </button>
    </header>

    <!-- Mobile Menu Overlay -->
    {#if isMobileMenuOpen}
      <div
        class="absolute inset-0 top-[50px] z-40 bg-[#050C14]/98 backdrop-blur-xl border-t border-cyan-900/30 p-6 flex flex-col gap-4 animate-in slide-in-from-top-4 duration-300 ease-[cubic-bezier(0.16,1,0.3,1)]"
      >
        <button
          on:click={() => (isTerminateOpen = true)}
          class="flex items-center gap-3 px-4 py-3 border border-red-900/60 text-red-500/70 text-xs tracking-widest uppercase bg-red-900/5"
        >
          <Power class="w-4 h-4" />
          Terminate Session
        </button>
      </div>
    {/if}

    <div class="flex-1 flex flex-col p-4 overflow-hidden">
      <!-- HEADER -->
      <div class="space-y-0.5 mb-3 shrink-0">
        <div
          class="flex items-center gap-1.5 text-cyan-500/50 text-[10px] tracking-widest"
        >
          <ChevronRight class="w-3 h-3" />
          <span>DECRYPTION INIT</span>
        </div>
        <h2 class="text-xl text-white font-light tracking-widest uppercase">
          Select Mode
        </h2>
      </div>

      <!-- PLAYER SNAPSHOT (Mobile) -->
      <div
        class="relative p-4 mb-4 border-t border-b border-cyan-900/30 bg-cyan-900/5 shrink-0"
      >
        <div class="flex flex-col gap-1">
          <div
            class="text-xl text-white font-medium tracking-wide lowercase leading-none"
          >
            {$userStore.name}
          </div>
          <div
            class={`inline-block w-fit px-2 py-0.5 mt-1 mb-1 text-xs font-mono text-cyan-300 border border-cyan-500/40 bg-cyan-900/20 rounded-sm ${$userStore.rank === "root" ? "shadow-[0_0_10px_rgba(6,182,212,0.3)] border-cyan-400" : "shadow-[0_0_5px_rgba(6,182,212,0.1)]"}`}
          >
            [{$userStore.rank}]
          </div>
          <div class="text-sm font-mono text-cyan-500/60 tracking-wider">
            {$userStore.points} PTS
          </div>
        </div>
      </div>

      <!-- PROTOCOL CARDS (Stacked) -->
      <div class="flex flex-col gap-2 flex-1 min-h-0 overflow-y-auto pb-4">
        {#each mobileProtocols as node}
          <button
            on:click={() => (selectedMode = node.mode)}
            class="relative flex flex-col justify-center p-3 text-left transition-all duration-200 w-full border bg-[#081018]/40 h-[90px] shrink-0 {selectedMode ===
            node.mode
              ? 'border-cyan-400 bg-cyan-900/10 shadow-[0_0_10px_rgba(34,211,238,0.1)]'
              : 'border-cyan-900/20 hover:border-cyan-800'}"
          >
            <div class="flex justify-between items-center w-full mb-1">
              <h3
                class="text-sm font-bold tracking-widest uppercase {selectedMode ===
                node.mode
                  ? node.colorClass
                  : 'text-cyan-700'}"
              >
                {node.title}
              </h3>
              <div
                class="text-lg font-light {selectedMode === node.mode
                  ? node.colorClass
                  : 'text-cyan-800/60'}"
              >
                +{node.points}
              </div>
            </div>
            <p
              class="text-[10px] uppercase tracking-wider text-cyan-400/50 mb-2 truncate"
            >
              {node.description}
            </p>
            <div class="flex items-center gap-2">
              <span
                class="text-[8px] uppercase tracking-widest text-cyan-900/60"
                >Signal</span
              >
              <div class="flex gap-0.5">
                {#if node.mode === "normal"}
                  <div class="w-1.5 h-1.5 bg-green-500"></div>
                  <div class="w-1.5 h-1.5 bg-amber-500"></div>
                  <div class="w-1.5 h-1.5 bg-slate-700/50"></div>
                  <div class="w-1.5 h-1.5 bg-slate-700/50"></div>
                {:else if node.mode === "hard"}
                  <div class="w-1.5 h-1.5 bg-green-500"></div>
                  <div class="w-1.5 h-1.5 bg-slate-700/50"></div>
                  <div class="w-1.5 h-1.5 bg-slate-700/50"></div>
                  <div class="w-1.5 h-1.5 bg-slate-700/50"></div>
                {:else}
                  <div class="w-1.5 h-1.5 bg-slate-800"></div>
                  <div class="w-1.5 h-1.5 bg-slate-800"></div>
                  <div class="w-1.5 h-1.5 bg-slate-800"></div>
                  <div class="w-1.5 h-1.5 bg-slate-800"></div>
                {/if}
              </div>
            </div>
          </button>
        {/each}
      </div>

      <!-- COLLAPSIBLE LOGS -->
      <div class="shrink-0 border-t border-cyan-900/30 mt-2">
        <button
          on:click={() => (areLogsOpen = !areLogsOpen)}
          class="w-full flex items-center justify-between py-3 text-[10px] tracking-widest text-cyan-500/80 uppercase active:bg-cyan-900/10 transition-colors"
        >
          <span>[ LAST 5 DECRYPTION LOGS ]</span>
          {#if areLogsOpen}
            <ChevronDown class="w-3 h-3" />
          {:else}
            <ChevronUp class="w-3 h-3" />
          {/if}
        </button>
        <div
          class="overflow-hidden transition-all duration-300 ease-[cubic-bezier(0.16,1,0.3,1)] bg-[#04080c] {areLogsOpen
            ? 'max-h-[150px] border-b border-cyan-900/30'
            : 'max-h-0'}"
        >
          <div class="p-3 space-y-2">
            {#each logs as log}
              <div
                class="flex items-center justify-between text-[10px] font-mono"
              >
                <span class="text-cyan-800">{log.date}</span>
                <span
                  class={log.type === "success"
                    ? "text-green-500/80"
                    : "text-amber-600/80"}>{log.status}</span
                >
                <span
                  class="{log.type === 'success'
                    ? 'text-green-400'
                    : 'text-amber-500'} w-8 text-right">{log.points}</span
                >
              </div>
            {/each}
          </div>
        </div>
      </div>
    </div>

    <!-- MOBILE SLIDE CTA -->
    <div class="p-4 pb-8 bg-[#050C14] shrink-0 border-t border-cyan-900/20">
      <div
        bind:this={trackElement}
        class="relative h-[80px] rounded-xl border-2 border-cyan-500 bg-[#081018] overflow-hidden select-none shadow-[0_0_20px_rgba(6,182,212,0.15)] flex items-center group"
      >
        <!-- Background fill based on drag progress -->
        <div
          class="absolute inset-y-0 left-0 bg-cyan-900/40 {slidingBack
            ? 'transition-all duration-300'
            : ''}"
          style="width: {(currentX / Math.max(1, maxSlidable)) * 100}%"
        ></div>

        <div
          class="absolute inset-0 flex items-center justify-center pl-16 md:pl-20 pointer-events-none"
        >
          <span
            class="text-[11px] tracking-[0.15em] font-bold text-cyan-400 uppercase transition-opacity {currentX >
            50
              ? 'opacity-0'
              : 'opacity-100'}"
          >
            Slide to Initiate Decryption →
          </span>
        </div>
        <div
          bind:this={dragElement}
          on:pointerdown={startDrag}
          on:pointermove={onDrag}
          on:pointerup={stopDrag}
          on:pointercancel={stopDrag}
          class="relative bg-cyan-500 rounded-lg flex items-center justify-center shadow-[0_0_15px_rgba(6,182,212,0.4)] ml-1 cursor-grab active:cursor-grabbing {slidingBack
            ? 'transition-transform duration-300'
            : ''}"
          style="width: 80px; height: 70px; transform: translateX({currentX}px); touch-action: none;"
        >
          <ArrowRight class="w-6 h-6 text-[#050C14] stroke-[3px]" />
        </div>
      </div>
    </div>
  </div>

  <!-- DESKTOP LAYOUT -->
  <div class="hidden lg:flex flex-col h-full w-full">
    <!-- Top Navigation Bar -->
    <header
      class="relative z-20 flex items-center justify-between px-6 py-4 border-b border-cyan-900/30 bg-[#050C14]/90 backdrop-blur-md"
    >
      <div class="flex items-center gap-4">
        <h1
          class="text-xl tracking-[0.2em] font-bold text-cyan-100 drop-shadow-[0_0_8px_rgba(34,211,238,0.3)]"
        >
          HARDLE
        </h1>
      </div>

      <div class="flex items-center gap-4">
        <button
          on:click={() => (isSettingsOpen = true)}
          class="flex items-center gap-2 px-4 py-1.5 border border-cyan-800 text-cyan-500 text-[10px] tracking-widest hover:bg-cyan-900/20 hover:border-cyan-600 transition-colors uppercase"
        >
          <Settings class="w-3 h-3" />
          Settings
        </button>
        <button
          on:click={() => (isTerminateOpen = true)}
          class="flex items-center gap-2 px-4 py-1.5 border border-red-900/60 text-red-500/70 text-[10px] tracking-widest hover:bg-red-900/10 hover:text-red-400 hover:border-red-700/50 transition-colors uppercase"
        >
          <Power class="w-3 h-3" />
          Terminate
        </button>
      </div>
    </header>

    <!-- Main Content Grid -->
    <main
      class="relative z-10 flex-1 flex p-10 gap-10 max-w-[1600px] mx-auto w-full"
    >
      <!-- Left Column - Core Interface -->
      <div class="flex-1 flex flex-col gap-10">
        <div class="space-y-1 mt-2">
          <div
            class="flex items-center gap-2 text-cyan-500/50 text-xs tracking-widest"
          >
            <ChevronRight class="w-3 h-3" />
            <span>DECRYPTION PROTOCOL INITIALIZATION</span>
          </div>
          <h2 class="text-3xl text-white font-light tracking-widest uppercase">
            Select Breach Mode
          </h2>
        </div>

        <!-- Player Snapshot (Desktop) -->
        <div
          class="relative p-5 border-l border-cyan-500/20 bg-gradient-to-r from-cyan-900/10 to-transparent"
        >
          <div class="flex flex-row items-center gap-6">
            <div class="flex items-center gap-4">
              <div class="space-y-1">
                <div
                  class="text-xl text-white tracking-[0.15em] uppercase font-medium"
                >
                  {$userStore.name}
                </div>
                <div
                  class="flex flex-wrap items-center gap-x-4 gap-y-1 text-sm font-medium"
                >
                  <span class="text-cyan-400 tracking-wider font-mono"
                    >[{$userStore.rank}]</span
                  >
                  <span class="text-cyan-800">|</span>
                  <span class="text-white/80 tracking-wider"
                    >{$userStore.points} PTS</span
                  >
                </div>
              </div>
            </div>

            <div class="ml-auto">
              <div
                class="text-[10px] text-cyan-500/50 flex items-center gap-2 uppercase tracking-widest"
              >
                <span
                  class="w-1.5 h-1.5 bg-cyan-500/40 rounded-full animate-pulse"
                ></span>
                Reset in 18 days
              </div>
            </div>
          </div>
        </div>

        <!-- Protocol Selection Grid -->
        <div class="grid grid-cols-3 gap-5">
          {#each protocols as node}
            <button
              on:click={() => (selectedMode = node.mode)}
              class="relative flex flex-col p-6 text-left transition-all duration-200 w-full h-full border bg-[#081018]/40 {selectedMode ===
              node.mode
                ? `${node.borderColorClass} bg-cyan-900/10 shadow-[0_0_15px_rgba(8,145,178,0.15)]`
                : 'border-cyan-900/20 hover:border-cyan-800 hover:bg-cyan-900/5'}"
            >
              <div class="flex justify-between items-start mb-4 w-full">
                <h3
                  class="text-lg font-bold tracking-widest {selectedMode ===
                  node.mode
                    ? node.colorClass
                    : 'text-cyan-700'}"
                >
                  {node.title}
                </h3>
                {#if selectedMode === node.mode}
                  <div
                    class="w-1.5 h-1.5 {node.colorClass === 'text-amber-500'
                      ? 'bg-amber-500'
                      : 'bg-cyan-400'} shadow-[0_0_8px_currentColor]"
                  ></div>
                {/if}
              </div>
              <p
                class="text-[10px] uppercase tracking-wider text-cyan-400/60 mb-6 h-12"
              >
                {node.description}
              </p>
              <div
                class="mt-auto w-full pt-4 border-t border-cyan-900/20 flex items-center justify-between"
              >
                <div class="flex flex-col gap-1.5">
                  <span
                    class="text-[9px] uppercase tracking-widest text-cyan-800"
                    >Signal Intel</span
                  >
                  <div class="flex gap-1">
                    {#if node.mode === "normal"}
                      <div
                        class="w-2 h-2 bg-green-500 rounded-[1px] shadow-[0_0_5px_rgba(34,197,94,0.5)]"
                      ></div>
                      <div
                        class="w-2 h-2 bg-amber-500 rounded-[1px] shadow-[0_0_5px_rgba(245,158,11,0.5)]"
                      ></div>
                      <div class="w-2 h-2 bg-slate-700/50 rounded-[1px]"></div>
                      <div class="w-2 h-2 bg-slate-700/50 rounded-[1px]"></div>
                      <div class="w-2 h-2 bg-slate-700/50 rounded-[1px]"></div>
                    {:else if node.mode === "hard"}
                      <div
                        class="w-2 h-2 bg-green-500 rounded-[1px] shadow-[0_0_5px_rgba(34,197,94,0.5)]"
                      ></div>
                      <div class="w-2 h-2 bg-slate-700/50 rounded-[1px]"></div>
                      <div class="w-2 h-2 bg-slate-700/50 rounded-[1px]"></div>
                      <div class="w-2 h-2 bg-slate-700/50 rounded-[1px]"></div>
                      <div class="w-2 h-2 bg-slate-700/50 rounded-[1px]"></div>
                    {:else}
                      <div class="w-2 h-2 bg-slate-800 rounded-[1px]"></div>
                      <div class="w-2 h-2 bg-slate-800 rounded-[1px]"></div>
                      <div class="w-2 h-2 bg-slate-800 rounded-[1px]"></div>
                      <div class="w-2 h-2 bg-slate-800 rounded-[1px]"></div>
                      <div class="w-2 h-2 bg-slate-800 rounded-[1px]"></div>
                    {/if}
                  </div>
                </div>
                <div
                  class="text-2xl font-light {selectedMode === node.mode
                    ? node.colorClass
                    : 'text-cyan-800'}"
                >
                  +{selectedMode === node.mode ? pointsDisplay : node.points}
                </div>
              </div>
            </button>
          {/each}
        </div>
      </div>

      <!-- Right Column - Intelligence Panel -->
      <div
        class="w-[380px] border-l border-cyan-900/30 pl-10 flex flex-col justify-between py-2"
      >
        <div class="space-y-8">
          <div class="border border-cyan-900/30 p-1">
            <div
              class="bg-cyan-900/10 px-3 py-2 flex items-center gap-2 text-cyan-500 text-[10px] uppercase tracking-[0.2em]"
            >
              <Terminal class="w-3 h-3" />
              <span>Terminal Access Log</span>
            </div>
          </div>

          <div>
            <h4
              class="text-[10px] text-cyan-600 uppercase tracking-widest mb-6 border-b border-cyan-900/30 pb-2"
            >
              Last 5 Decryption Logs
            </h4>
            <div class="space-y-4 font-mono text-xs">
              {#each logs as log}
                <div
                  class="grid grid-cols-[auto_1fr_auto] gap-4 items-center group cursor-default hover:bg-cyan-900/5 p-1 rounded transition-colors"
                >
                  <span
                    class="text-cyan-800 group-hover:text-cyan-600 transition-colors"
                    >{log.date}</span
                  >
                  <span
                    class="{log.type === 'success'
                      ? 'text-green-500'
                      : 'text-amber-500'} tracking-tight">{log.status}</span
                  >
                  <span
                    class="{log.type === 'success'
                      ? 'text-green-400'
                      : 'text-amber-500'} text-right font-medium"
                    >{log.points}</span
                  >
                </div>
              {/each}
            </div>
          </div>
        </div>

        <div class="mt-auto border-t border-cyan-900/20 pt-6">
          <div class="flex justify-between items-end mb-2">
            <span class="text-[10px] text-cyan-700 tracking-widest uppercase"
              >System Status</span
            >
            <span class="text-[10px] text-cyan-600 tracking-widest uppercase"
              >Load: 12%</span
            >
          </div>
          <div class="flex gap-1 h-8">
            {#each Array(24) as _, i}
              <div
                class="flex-1 {i < 18
                  ? 'bg-cyan-900/30'
                  : 'bg-cyan-900/10'} animate-pulse"
                style="animation-delay: {i * 0.05}s"
              ></div>
            {/each}
          </div>
        </div>
      </div>
    </main>

    <!-- Footer / CTA (Desktop) -->
    <footer
      class="relative z-10 p-10 flex justify-end bg-transparent border-t lg:border-t-0 border-cyan-900/30"
    >
      <button
        on:click={() => goto("/game")}
        class="relative w-auto px-16 py-5 text-lg tracking-[0.2em] font-medium uppercase transition-all duration-300 border group {selectedMode ===
        'extreme'
          ? 'border-amber-600/60 text-amber-100 hover:border-amber-500 hover:text-white'
          : selectedMode === 'hard'
            ? 'border-cyan-400/60 text-cyan-100 hover:border-cyan-300 hover:text-white'
            : 'border-cyan-600/40 text-cyan-200 hover:border-cyan-400 hover:text-white'}"
      >
        <span class="relative z-10 flex items-center justify-center gap-3">
          INITIATE DECRYPTION
          <ChevronRight
            class="w-4 h-4 group-hover:translate-x-1 transition-transform"
          />
        </span>
        <div
          class="absolute inset-0 bg-black/0 group-active:bg-black/20 transition-colors"
        ></div>
      </button>
    </footer>
  </div>

  <!-- MODALS -->
  {#if isSettingsOpen}
    <div class="fixed inset-0 z-[100] flex items-center justify-center p-4">
      <div
        class="absolute inset-0 bg-black/70 backdrop-blur-[2px] animate-in fade-in duration-150"
        aria-label="close"
        on:click={() => (isSettingsOpen = false)}
        role="button"
        tabindex="0"
      ></div>
      <div
        class="relative w-full max-w-[480px] bg-[#071018] border border-cyan-500/30 shadow-[0_0_40px_rgba(6,182,212,0.1)] outline-none"
      >
        <div
          class="flex items-center justify-between px-6 py-4 border-b border-cyan-900/30 bg-[#0A1622]"
        >
          <h3
            class="text-sm font-bold tracking-[0.2em] text-cyan-100 uppercase"
          >
            &gt; SYSTEM SETTINGS
          </h3>
          <button
            on:click={() => (isSettingsOpen = false)}
            class="text-cyan-500 hover:text-cyan-300 transition-colors"
          >
            <X class="w-4 h-4" />
          </button>
        </div>
        <div
          class="p-6 space-y-8 max-h-[70vh] overflow-y-auto"
          style="scrollbar-width: thin; scrollbar-color: #0891b2 transparent;"
        >
          <section class="space-y-4">
            <h4
              class="text-[10px] font-bold text-cyan-600 uppercase tracking-widest border-b border-cyan-900/30 pb-2"
            >
              Audio
            </h4>
            <div class="space-y-4 px-2">
              <div class="space-y-2">
                <div
                  class="flex justify-between text-xs text-cyan-400 uppercase tracking-wider"
                >
                  <span>Master Volume</span>
                  <span>{volume}%</span>
                </div>
                <input
                  type="range"
                  min="0"
                  max="100"
                  bind:value={volume}
                  class="w-full h-1 bg-cyan-900/40 rounded-none appearance-none cursor-pointer [&::-webkit-slider-thumb]:appearance-none [&::-webkit-slider-thumb]:w-3 [&::-webkit-slider-thumb]:h-3 [&::-webkit-slider-thumb]:bg-cyan-500 [&::-webkit-slider-thumb]:border-0"
                />
              </div>
              <div class="flex items-center justify-between">
                <span class="text-xs text-cyan-400 uppercase tracking-wider"
                  >Sound Effects</span
                >
                <button
                  on:click={() => (sfxEnabled = !sfxEnabled)}
                  class="w-8 h-4 rounded-full relative transition-colors {sfxEnabled
                    ? 'bg-cyan-500/30'
                    : 'bg-slate-800'}"
                >
                  <div
                    class="absolute top-0.5 w-3 h-3 bg-cyan-400 rounded-full transition-all {sfxEnabled
                      ? 'left-4.5'
                      : 'left-0.5'}"
                  ></div>
                </button>
              </div>
            </div>
          </section>
          <section class="space-y-4">
            <h4
              class="text-[10px] font-bold text-cyan-600 uppercase tracking-widest border-b border-cyan-900/30 pb-2"
            >
              Haptics
            </h4>
            <div class="space-y-4 px-2">
              <div class="flex items-center justify-between">
                <span class="text-xs text-cyan-400 uppercase tracking-wider"
                  >Vibration</span
                >
                <button
                  on:click={() => (vibrationEnabled = !vibrationEnabled)}
                  class="w-8 h-4 rounded-full relative transition-colors {vibrationEnabled
                    ? 'bg-cyan-500/30'
                    : 'bg-slate-800'}"
                >
                  <div
                    class="absolute top-0.5 w-3 h-3 bg-cyan-400 rounded-full transition-all {vibrationEnabled
                      ? 'left-4.5'
                      : 'left-0.5'}"
                  ></div>
                </button>
              </div>
              <div
                class="space-y-2 transition-opacity {!vibrationEnabled
                  ? 'opacity-50 pointer-events-none'
                  : 'opacity-100'}"
              >
                <span
                  class="text-xs text-cyan-400 uppercase tracking-wider block mb-2"
                  >Intensity</span
                >
                <div
                  class="flex border border-cyan-900/30 bg-cyan-900/10 p-0.5"
                >
                  {#each ["low", "medium", "high"] as level}
                    <button
                      on:click={() => (hapticIntensity = level)}
                      class="flex-1 py-1.5 text-[10px] uppercase tracking-wider transition-all {hapticIntensity ===
                      level
                        ? 'bg-cyan-500/20 text-cyan-200 shadow-[0_0_10px_rgba(6,182,212,0.1)]'
                        : 'text-cyan-600 hover:text-cyan-400'}"
                    >
                      {level}
                    </button>
                  {/each}
                </div>
              </div>
            </div>
          </section>
          <section class="space-y-4">
            <h4
              class="text-[10px] font-bold text-cyan-600 uppercase tracking-widest border-b border-cyan-900/30 pb-2"
            >
              General
            </h4>
            <div class="space-y-4 px-2">
              <div class="flex items-center justify-between">
                <span class="text-xs text-cyan-400 uppercase tracking-wider"
                  >Reduce Motion</span
                >
                <button
                  on:click={() => (reduceMotion = !reduceMotion)}
                  class="w-8 h-4 rounded-full relative transition-colors {reduceMotion
                    ? 'bg-cyan-500/30'
                    : 'bg-slate-800'}"
                >
                  <div
                    class="absolute top-0.5 w-3 h-3 bg-cyan-400 rounded-full transition-all {reduceMotion
                      ? 'left-4.5'
                      : 'left-0.5'}"
                  ></div>
                </button>
              </div>
              <div class="flex items-center justify-between">
                <span class="text-xs text-cyan-400 uppercase tracking-wider"
                  >High Contrast</span
                >
                <button
                  on:click={() => (highContrast = !highContrast)}
                  class="w-8 h-4 rounded-full relative transition-colors {highContrast
                    ? 'bg-cyan-500/30'
                    : 'bg-slate-800'}"
                >
                  <div
                    class="absolute top-0.5 w-3 h-3 bg-cyan-400 rounded-full transition-all {highContrast
                      ? 'left-4.5'
                      : 'left-0.5'}"
                  ></div>
                </button>
              </div>
            </div>
          </section>
          <section class="pt-2">
            <div
              class="bg-cyan-900/5 border border-cyan-900/20 p-4 space-y-3 text-center"
            >
              <div class="space-y-0.5">
                <div class="text-xs font-bold text-cyan-100 tracking-widest">
                  HARDLE v1.0
                </div>
                <div
                  class="text-[10px] text-cyan-500/60 uppercase tracking-wider"
                >
                  Competitive Word Decryption System
                </div>
              </div>
              <div class="text-[9px] text-cyan-800 font-mono">
                Build ID: 0608N-116
              </div>
              <button
                class="text-[10px] text-cyan-400 border border-cyan-900/40 px-3 py-1 uppercase tracking-widest hover:bg-cyan-900/20 transition-colors"
                >View License</button
              >
            </div>
          </section>
        </div>
        <div
          class="px-6 py-3 bg-[#050C14] border-t border-cyan-900/30 flex justify-end"
        >
          <span class="text-[9px] text-cyan-700/50 uppercase tracking-widest"
            >Settings auto-save active</span
          >
        </div>
      </div>
    </div>
  {/if}

  {#if isTerminateOpen}
    <div class="fixed inset-0 z-[100] flex items-center justify-center p-4">
      <div
        class="absolute inset-0 bg-black/70 backdrop-blur-[2px] animate-in fade-in duration-150"
        aria-label="close"
        on:click={() => (isTerminateOpen = false)}
        role="button"
        tabindex="0"
      ></div>
      <div
        class="relative w-full max-w-[420px] bg-[#071018] border border-red-900/50 shadow-[0_0_40px_rgba(220,38,38,0.1)] outline-none"
      >
        <div class="px-6 py-4 border-b border-red-900/20 bg-[#0A1622]">
          <h3 class="text-sm font-bold tracking-[0.2em] text-red-500 uppercase">
            &gt; TERMINATE SESSION
          </h3>
        </div>
        <div class="p-8 text-center space-y-4">
          <p class="text-cyan-100 text-sm tracking-wide">
            Are you sure you want to sign out?
          </p>
          <p class="text-cyan-600/60 text-xs tracking-wide">
            You will be redirected to the login interface.
          </p>
        </div>
        <div class="p-6 pt-2 flex gap-4">
          <button
            on:click={() => (isTerminateOpen = false)}
            class="flex-1 py-3 border border-cyan-800 text-cyan-500 text-xs font-bold tracking-[0.15em] hover:bg-cyan-900/10 hover:border-cyan-600 transition-colors uppercase"
            >Cancel</button
          >
          <button
            class="flex-1 py-3 bg-red-900/80 text-white text-xs font-bold tracking-[0.15em] hover:bg-red-800 transition-colors uppercase shadow-[0_0_15px_rgba(153,27,27,0.4)]"
            >Terminate</button
          >
        </div>
      </div>
    </div>
  {/if}
</div>
