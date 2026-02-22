<script lang="ts">
    import { onMount } from "svelte";

    interface Props {
        currentTotalPoints: number;
        pointsGained: number;
        gameStatus: "won" | "lost";
    }

    interface Rank {
        name: string;
        minPoints: number;
    }

    let { currentTotalPoints, pointsGained, gameStatus }: Props = $props();

    const RANKS: Rank[] = [
        { name: "UNVERIFIED", minPoints: 0 },
        { name: "CLEARANCE I", minPoints: 100 },
        { name: "CLEARANCE II", minPoints: 300 },
        { name: "CLEARANCE III", minPoints: 600 },
        { name: "SECURE ACCESS", minPoints: 1000 },
        { name: "ELEVATED ACCESS", minPoints: 1500 },
        { name: "RESTRICTED ACCESS", minPoints: 2100 },
        { name: "SYSTEM OPERATOR", minPoints: 2800 },
        { name: "CORE OPERATOR", minPoints: 3600 },
        { name: "ROOT ACCESS", minPoints: 4500 },
    ];

    let visible = $state(false);
    let rankChangeVisible = $state(false);

    onMount(() => {
        const timer1 = setTimeout(() => (visible = true), 200);
        const timer2 = setTimeout(() => (rankChangeVisible = true), 600);

        return () => {
            clearTimeout(timer1);
            clearTimeout(timer2);
        };
    });

    function getRankByPoints(points: number): Rank {
        for (let i = RANKS.length - 1; i >= 0; i--) {
            if (points >= RANKS[i].minPoints) {
                return RANKS[i];
            }
        }
        return RANKS[0];
    }

    function getNextRank(currentRank: Rank): Rank | null {
        const currentIndex = RANKS.findIndex(
            (r) => r.name === currentRank.name,
        );
        if (currentIndex < RANKS.length - 1) {
            return RANKS[currentIndex + 1];
        }
        return null;
    }

    function calculateProgress(points: number, currentRank: Rank): number {
        const nextRank = getNextRank(currentRank);
        if (!nextRank) return 100;

        const currentMin = currentRank.minPoints;
        const nextMin = nextRank.minPoints;
        const range = nextMin - currentMin;
        const progress = points - currentMin;

        return Math.floor((progress / range) * 100);
    }

    let pointsChange = $derived(
        gameStatus === "won" ? pointsGained : -Math.abs(pointsGained),
    );
    let previousPoints = $derived(currentTotalPoints - pointsChange);
    let newPoints = $derived(currentTotalPoints);

    let previousRank = $derived(getRankByPoints(previousPoints));
    let newRank = $derived(getRankByPoints(newPoints));

    let rankChanged = $derived(previousRank.name !== newRank.name);
    let rankIncreased = $derived(
        rankChanged && newRank.minPoints > previousRank.minPoints,
    );
    let rankDecreased = $derived(
        rankChanged && newRank.minPoints < previousRank.minPoints,
    );

    let progress = $derived(calculateProgress(newPoints, newRank));
    let nextRank = $derived(getNextRank(newRank));
</script>

<div
    class={`w-full h-full transition-all duration-500 ${
        visible ? "opacity-100 translate-y-0" : "opacity-0 translate-y-4"
    }`}
>
    <div class="flex items-center justify-between mb-6">
        <h2 class="text-sm tracking-widest text-cyan-400/80">
            CLEARANCE REPORT
        </h2>
        <div class="text-xs text-cyan-500/60">SYS-EVAL</div>
    </div>

    <!-- Current Rank -->
    <div class="mb-6">
        <div
            class="text-[10px] text-cyan-500/60 tracking-widest uppercase mb-2"
        >
            Current Clearance
        </div>
        <div class="text-lg text-cyan-300 font-mono tracking-[0.2em] font-bold">
            {previousRank.name}
        </div>
    </div>

    <!-- Points Impact -->
    <div class="mb-6 pb-6 border-b border-cyan-900/30">
        <div
            class="text-[10px] text-cyan-500/60 tracking-widest uppercase mb-2"
        >
            {gameStatus === "won" ? "Points Added" : "Points Deducted"}
        </div>
        <div
            class={`text-base font-mono font-bold animate-[pointsFlash_300ms_ease-out] ${
                gameStatus === "won" ? "text-green-400" : "text-red-400"
            }`}
        >
            {gameStatus === "won" ? "+" : "−"}{Math.abs(pointsChange)} PTS
        </div>
    </div>

    <!-- Rank Change Status -->
    <div
        class={`mb-6 transition-all duration-500 delay-400 ${
            rankChangeVisible
                ? "opacity-100 translate-x-0"
                : "opacity-0 -translate-x-2"
        }`}
    >
        {#if rankIncreased}
            <div class="flex items-center gap-2 mb-2">
                <div
                    class="w-2 h-2 rounded-full bg-green-500 animate-pulse"
                ></div>
                <span class="text-xs tracking-wider text-green-400 uppercase"
                    >Rank Increased</span
                >
            </div>
            <div
                class="text-[10px] text-green-500/60 tracking-widest uppercase mb-3"
            >
                Access Level Upgraded
            </div>
            <div
                class="text-lg text-green-300 font-mono tracking-[0.2em] font-bold animate-[rankGlow_600ms_ease-out]"
            >
                {newRank.name}
            </div>
        {/if}

        {#if rankDecreased}
            <div
                class="flex items-center gap-2 mb-2 animate-[alertFlash_200ms_ease-out]"
            >
                <div
                    class="w-2 h-2 rounded-full bg-red-500 animate-pulse"
                ></div>
                <span class="text-xs tracking-wider text-red-400 uppercase"
                    >Rank Reduced</span
                >
            </div>
            <div
                class="text-[10px] text-red-500/60 tracking-widest uppercase mb-3"
            >
                Access Level Revoked
            </div>
            <div
                class="text-lg text-red-300 font-mono tracking-[0.2em] font-bold"
            >
                {newRank.name}
            </div>
        {/if}

        {#if !rankChanged}
            <div class="flex items-center gap-2 mb-2">
                <div class="w-2 h-2 rounded-full bg-amber-500"></div>
                <span class="text-xs tracking-wider text-amber-400 uppercase"
                    >Rank Unchanged</span
                >
            </div>
            <div
                class="text-lg text-cyan-300 font-mono tracking-[0.2em] font-bold mt-3"
            >
                {newRank.name}
            </div>
        {/if}
    </div>

    <!-- Progress Indicator -->
    {#if nextRank}
        <div class="pt-6 border-t border-cyan-900/30">
            <div
                class="text-[10px] text-cyan-500/60 tracking-widest uppercase mb-2"
            >
                Progress to Next Clearance
            </div>
            <div class="text-sm text-cyan-400 font-mono font-bold mb-2">
                {progress}%
            </div>
            <div class="text-[10px] text-cyan-500/50 font-mono">
                {nextRank.minPoints - newPoints} PTS to {nextRank.name}
            </div>
        </div>
    {/if}

    {#if !nextRank}
        <div class="pt-6 border-t border-cyan-900/30">
            <div
                class="text-[10px] text-cyan-500/60 tracking-widest uppercase mb-2"
            >
                Maximum Clearance Achieved
            </div>
            <div class="text-xs text-green-400/60 font-mono">
                ROOT ACCESS GRANTED
            </div>
        </div>
    {/if}
</div>
