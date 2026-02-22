<script lang="ts">
    import { onMount } from "svelte";

    interface Props {
        greens: number;
        yellows: number;
        attemptsUsed: number;
        gameStatus: "playing" | "won" | "lost";
        isMobile?: boolean;
    }

    let {
        greens,
        yellows,
        attemptsUsed,
        gameStatus,
        isMobile = false,
    }: Props = $props();

    let roughWork = $state("");
    let showCursor = $state(true);
    let confidenceText = $state("");
    let displayedRecovery = $state(0);

    let breachWindowsRemaining = $derived(6 - attemptsUsed);
    const maxSignals = 10;
    let systemConfidence = $derived(
        greens >= 3 ? "HIGH" : greens >= 1 ? "MEDIUM" : "LOW",
    );
    let dataRecovery = $derived(
        Math.min(Math.min(greens, 10) * 10 + Math.min(yellows, 10) * 5, 100),
    );

    // Cursor blink effect
    $effect(() => {
        if (gameStatus === "playing") {
            const interval = setInterval(() => {
                showCursor = !showCursor;
            }, 800);
            return () => clearInterval(interval);
        } else {
            showCursor = false;
        }
    });

    // Typed confidence effect
    $effect(() => {
        const targetText = systemConfidence;
        let currentIndex = 0;
        confidenceText = "";

        const typeInterval = setInterval(() => {
            if (currentIndex < targetText.length) {
                confidenceText = targetText.slice(0, currentIndex + 1);
                currentIndex++;
            } else {
                clearInterval(typeInterval);
            }
        }, 30);

        return () => clearInterval(typeInterval);
    });

    // Stepped recovery percentage
    $effect(() => {
        if (displayedRecovery < dataRecovery) {
            const step = Math.ceil((dataRecovery - displayedRecovery) / 3);
            const timeout = setTimeout(() => {
                displayedRecovery = Math.min(
                    displayedRecovery + step,
                    dataRecovery,
                );
            }, 150);
            return () => clearTimeout(timeout);
        } else if (displayedRecovery > dataRecovery) {
            displayedRecovery = dataRecovery;
        }
    });

    function handleRoughWorkChange(e: Event) {
        roughWork = (e.target as HTMLTextAreaElement).value;
    }
</script>

{#snippet signalBlocks(
    value: number,
    max: number,
    type: "verified" | "partial",
)}
    {@const color = type === "verified" ? "bg-green-500" : "bg-amber-500"}
    {@const glowColor =
        type === "verified"
            ? "shadow-[0_0_6px_rgba(34,197,94,0.5)]"
            : "shadow-[0_0_6px_rgba(251,191,36,0.5)]"}
    <div class="flex gap-1.5">
        {#each Array(max) as _, i}
            <div
                class={`w-6 h-6 rounded transition-all duration-500 ${
                    i < value
                        ? `${color} ${glowColor}`
                        : "bg-slate-900/60 border border-cyan-900/30"
                }`}
                style:transition-delay={`${i * 120}ms`}
            ></div>
        {/each}
    </div>
{/snippet}

<div class="w-full">
    <div class="flex items-center justify-between mb-6">
        <h2 class="text-sm tracking-widest text-cyan-400/80">
            [ DECRYPTION STATE ]
        </h2>
        <div class="text-xs text-cyan-500/60">
            Ø{100 + Math.min(greens, 10) * 10 + Math.min(yellows, 10) * 5}
        </div>
    </div>

    <!-- Verified Signals -->
    <div class="mb-5">
        <div class="flex items-center gap-2 mb-2">
            <div
                class="w-2 h-2 rounded-full bg-green-500 animate-pulse"
                style:animation-duration="2s"
            ></div>
            <span class="text-xs tracking-wider text-green-400"
                >VERIFIED SIGNALS</span
            >
        </div>
        {@render signalBlocks(greens, maxSignals, "verified")}
    </div>

    <!-- Partial Signals -->
    <div class="mb-5">
        <div class="flex items-center gap-2 mb-2">
            <div
                class="w-2 h-2 rounded-full bg-amber-500 animate-pulse"
                style:animation-duration="2s"
            ></div>
            <span class="text-xs tracking-wider text-amber-400"
                >PARTIAL SIGNALS</span
            >
        </div>
        {@render signalBlocks(yellows, maxSignals, "partial")}
    </div>

    <!-- System Confidence -->
    <div class="mb-5 pb-5 border-b border-cyan-900/30">
        <div class="flex items-center justify-between">
            <span class="text-xs text-cyan-500/60 tracking-wider"
                >SYSTEM CONFIDENCE</span
            >
            <span
                class={`text-sm font-mono font-bold tracking-wider ${
                    systemConfidence === "HIGH"
                        ? "text-green-400"
                        : systemConfidence === "MEDIUM"
                          ? "text-amber-400"
                          : "text-red-400"
                }`}
            >
                {confidenceText}
            </span>
        </div>
    </div>

    <!-- Data Recovery -->
    <div class="mb-5">
        <div class="flex items-center justify-between mb-2">
            <span class="text-xs text-cyan-500/60 tracking-wider"
                >DATA RECOVERY</span
            >
            <span class="text-sm font-mono font-bold text-cyan-400"
                >{displayedRecovery}%</span
            >
        </div>
        <div class="flex gap-1">
            {#each Array(14) as _, i}
                <div
                    class={`w-4 h-4 rounded transition-all duration-300 ${
                        i < Math.floor((displayedRecovery / 100) * 14)
                            ? "bg-cyan-600 shadow-[0_0_4px_rgba(8,145,178,0.4)]"
                            : "bg-slate-900/60 border border-cyan-900/30"
                    }`}
                    style:transition-delay={`${i * 80}ms`}
                ></div>
            {/each}
        </div>
    </div>

    <!-- Scratch Buffer -->
    <div class="mb-5">
        <div class="flex items-center justify-between mb-2">
            <span class="text-xs tracking-wider text-cyan-400/80"
                >SCRATCH BUFFER</span
            >
            {#if gameStatus !== "playing"}
                <span class="text-xs text-red-400/60">[ LOCKED ]</span>
            {/if}
        </div>
        <div class="relative">
            <textarea
                value={roughWork}
                oninput={handleRoughWorkChange}
                placeholder="> TYPE NOTES HERE..."
                class={`w-full ${isMobile ? "h-24" : "h-32"} bg-slate-950/60 border border-cyan-900/50 rounded text-xs text-cyan-300 font-mono p-2 resize-none focus:outline-none focus:border-cyan-700 placeholder:text-cyan-900/60 caret-cyan-500 transition-all duration-200 ${
                    gameStatus !== "playing" ? "opacity-60" : ""
                }`}
                spellcheck="false"
                disabled={gameStatus !== "playing"}
            ></textarea>
            {#if gameStatus === "playing" && showCursor && roughWork.length === 0}
                <div
                    class="absolute left-2 top-2 w-0.5 h-4 bg-cyan-500 animate-[cursorBlink_800ms_step-end_infinite]"
                ></div>
            {/if}
        </div>
    </div>

    <!-- Breach Windows Remaining -->
    <div>
        <div class="text-xs text-cyan-500/60 tracking-wider mb-2">
            BREACH WINDOWS REMAINING
        </div>
        <div class="flex gap-1.5">
            {#each Array(6) as _, i}
                <div
                    class={`w-6 h-6 rounded transition-all duration-300 ${
                        i < breachWindowsRemaining
                            ? "bg-slate-600 border border-cyan-700/50"
                            : "bg-transparent border border-red-900/30 opacity-30"
                    }`}
                    style:animation={i === breachWindowsRemaining &&
                    attemptsUsed > 0
                        ? "windowCollapse 400ms ease-out"
                        : undefined}
                ></div>
            {/each}
        </div>
    </div>
</div>
