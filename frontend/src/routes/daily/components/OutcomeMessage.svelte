<script lang="ts">
    import { onMount } from "svelte";

    interface Props {
        primary: string;
        secondary: string;
        solution: string;
        pointsGained: number;
        gameStatus?: "won" | "lost";
    }

    let {
        primary,
        secondary,
        solution,
        pointsGained,
        gameStatus = "won",
    }: Props = $props();

    let visible = $state(false);
    let solutionVisible = $state(false);
    let pointsVisible = $state(false);

    onMount(() => {
        const timer1 = setTimeout(() => (visible = true), 100);
        const timer2 = setTimeout(() => (solutionVisible = true), 400);
        const timer3 = setTimeout(() => (pointsVisible = true), 700);

        return () => {
            clearTimeout(timer1);
            clearTimeout(timer2);
            clearTimeout(timer3);
        };
    });
</script>

<div
    class="flex flex-col lg:flex-row gap-4 lg:gap-8 py-4 lg:py-4 border-y border-cyan-900/40 my-3 lg:my-4 bg-slate-900/20 lg:bg-transparent px-4 lg:px-0 lg:items-center"
>
    <!-- SECTION 1 — LEFT (OUTCOME) -->
    <div
        class={`flex-1 flex flex-col gap-2 lg:gap-2 transition-all duration-300 ${
            visible ? "opacity-100 translate-y-0" : "opacity-0 translate-y-2"
        }`}
    >
        <!-- Primary status -->
        <div
            class="text-sm md:text-lg lg:text-xl text-cyan-300 font-mono tracking-[0.2em] font-bold uppercase"
        >
            {primary}
        </div>

        <!-- Secondary narrative -->
        <div
            class="text-[10px] md:text-sm text-cyan-500/60 font-mono tracking-[0.15em] uppercase"
        >
            {secondary}
        </div>

        <!-- Solution reveal -->
        <div
            class={`mt-1 lg:mt-3 transition-all duration-500 delay-300 ${
                solutionVisible
                    ? "opacity-100 translate-y-0"
                    : "opacity-0 translate-y-2"
            }`}
        >
            <div
                class="text-[10px] text-cyan-500/60 tracking-widest uppercase mb-1"
            >
                Solution
            </div>
            <div
                class="text-xl md:text-3xl text-cyan-400 font-mono tracking-[0.3em] font-bold"
            >
                {#each solution.split("") as letter, i}
                    <span
                        class="inline-block animate-[letterReveal_150ms_ease-out_forwards]"
                        style:animation-delay={`${i * 80}ms`}
                        style:opacity={0}
                    >
                        {letter}
                    </span>
                {/each}
            </div>
        </div>
    </div>

    <!-- SECTION 2 — CENTER (SESSION IMPACT) -->
    <div
        class={`flex-shrink-0 flex flex-col items-center justify-center text-center lg:px-6 transition-all duration-500 delay-500 ${
            pointsVisible ? "opacity-100 scale-100" : "opacity-0 scale-95"
        }`}
    >
        <div
            class="text-[10px] text-cyan-500/60 tracking-widest uppercase mb-1"
        >
            {gameStatus === "won" ? "Points Gained" : "Points Deducted"}
        </div>
        <div
            class={`text-xl font-mono font-bold animate-[pointsPulse_400ms_ease-out] ${
                gameStatus === "won" ? "text-cyan-300" : "text-red-400"
            }`}
        >
            {gameStatus === "won" ? "+" : "−"}{Math.abs(pointsGained)} PTS
        </div>
    </div>

    <!-- SECTION 3 — RIGHT (NEXT ACTION) -->
    <div
        class={`flex-shrink-0 flex items-center justify-center lg:justify-end transition-all duration-500 delay-700 ${
            pointsVisible
                ? "opacity-100 translate-x-0"
                : "opacity-0 translate-x-2"
        }`}
    >
        <button
            class="w-full lg:w-auto px-5 py-2 border-2 border-cyan-900/60 bg-slate-900/40 text-cyan-400 font-mono text-xs tracking-wider uppercase rounded hover:bg-slate-800/60 hover:border-cyan-700 transition-all hover:shadow-[0_0_8px_rgba(6,182,212,0.3)]"
        >
            Return to Modes
        </button>
    </div>
</div>
