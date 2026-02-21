<script lang="ts">
    import { onMount } from "svelte";
    import { getLeaderboard, type LeaderboardEntry } from "$lib/utils/api";

    let leaderboard = $state<LeaderboardEntry[]>([]);
    let loading = $state(true);

    onMount(async () => {
        try {
            leaderboard = await getLeaderboard();
        } catch (e) {
            console.error(e);
        } finally {
            loading = false;
        }
    });
</script>

<div
    class="bg-slate-900/30 backdrop-blur-sm border border-cyan-900/40 shadow-[var(--glow-cyan)] rounded-lg p-6 space-y-6 w-full font-mono"
>
    <h2
        class="text-lg md:text-xl text-cyan-400 font-mono tracking-widest font-bold"
    >
        LEADERBOARD
    </h2>

    <div class="space-y-1">
        <!-- Header -->
        <div class="grid grid-cols-2 pb-3 border-b border-cyan-900/40">
            <div
                class="text-sm font-bold text-cyan-500/60 tracking-wider uppercase"
            >
                User
            </div>
            <div
                class="text-sm font-bold text-cyan-500/60 text-right tracking-wider uppercase"
            >
                Points
            </div>
        </div>

        <!-- Entries -->
        <div class="space-y-0.5">
            {#if loading}
                <div class="text-slate-500 py-4 text-center">Loading...</div>
            {:else if leaderboard.length === 0}
                <div class="text-slate-500 py-4 text-center">
                    No players yet.
                </div>
            {:else}
                {#each leaderboard as entry, index}
                    <div
                        class="grid grid-cols-2 py-3 border-b border-cyan-900/20 last:border-0 {index <
                        3
                            ? 'text-cyan-300'
                            : 'text-cyan-500/80'}"
                    >
                        <div
                            class={index < 3
                                ? "text-amber-400 drop-shadow-[0_0_8px_rgba(251,191,36,0.5)]"
                                : ""}
                        >
                            {entry.username}
                        </div>
                        <div
                            class="text-right {index < 3 ? 'font-medium' : ''}"
                        >
                            {entry.points}
                        </div>
                    </div>
                {/each}
            {/if}
        </div>
    </div>
</div>
