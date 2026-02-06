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
    class="bg-[#161616] border border-gray-800 rounded-2xl p-6 space-y-6 w-full"
>
    <h2 class="text-2xl font-semibold text-white">Leaderboard</h2>

    <div class="space-y-1">
        <!-- Header -->
        <div class="grid grid-cols-2 pb-3 border-b border-gray-800">
            <div class="text-sm font-medium text-gray-400">User</div>
            <div class="text-sm font-medium text-gray-400 text-right">
                Points
            </div>
        </div>

        <!-- Entries -->
        <div class="space-y-0.5">
            {#if loading}
                <div class="text-gray-500 py-4 text-center">Loading...</div>
            {:else if leaderboard.length === 0}
                <div class="text-gray-500 py-4 text-center">
                    No players yet.
                </div>
            {:else}
                {#each leaderboard as entry, index}
                    <div
                        class="grid grid-cols-2 py-3 border-b border-gray-800/50 last:border-0 {index <
                        3
                            ? 'text-white'
                            : 'text-gray-400'}"
                    >
                        <div class={index < 3 ? "text-[#d4a933]" : ""}>
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
