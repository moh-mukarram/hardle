<script lang="ts">
    import { onMount } from "svelte";
    import { X } from "lucide-svelte";
    import { fly, fade } from "svelte/transition";
    import { cubicOut } from "svelte/easing";
    import { API_BASE } from "$lib/utils/api";
    import { getAuthStore } from "$lib/state/auth.svelte";

    interface Props {
        isOpen: boolean;
        onClose: () => void;
        currentPlayerPoints: number;
        onRefresh?: () => void;
    }

    let { isOpen, onClose, currentPlayerPoints, onRefresh }: Props = $props();

    const auth = getAuthStore();

    interface LeaderboardRow {
        username: string;
        points: number;
        rank: string;
    }

    let leaderboard = $state<LeaderboardRow[]>([]);
    let loading = $state(true);
    let error = $state("");

    async function fetchLeaderboard() {
        loading = true;
        error = "";
        try {
            const res = await fetch(`${API_BASE}/api/leaderboard`, {
                credentials: "include",
            });
            if (res.ok) {
                leaderboard = await res.json();
            } else {
                error = "FAILED TO LOAD";
            }
        } catch (e) {
            error = "CONNECTION ERROR";
        } finally {
            loading = false;
        }
    }

    // Fetch when panel opens
    $effect(() => {
        if (isOpen) {
            fetchLeaderboard();
        }
    });

    // Expose refresh capability
    export function refresh() {
        fetchLeaderboard();
    }

    function isCurrentUser(entry: LeaderboardRow): boolean {
        if (!auth.isAuthenticated || !auth.user) return false;
        return entry.username === auth.user.username;
    }

    function getRankLabel(rank: string): string {
        const rankMap: Record<string, string> = {
            Bronze: "CLEARANCE I",
            Silver: "CLEARANCE II",
            Gold: "CLEARANCE III",
            Platinum: "SECURE ACCESS",
            Diamond: "ROOT ACCESS",
        };
        return rankMap[rank] || rank.toUpperCase();
    }

    // Derive current user rank from leaderboard data
    let currentUserRank = $derived(() => {
        if (!auth.isAuthenticated || !auth.user) return "UNVERIFIED";
        const entry = leaderboard.find(
            (e) => e.username === auth.user!.username,
        );
        if (entry) return getRankLabel(entry.rank);
        return "CLEARANCE I";
    });

    // Calculate days until month reset
    let daysUntilReset = $derived(() => {
        const now = new Date();
        const lastDay = new Date(now.getFullYear(), now.getMonth() + 1, 0);
        return lastDay.getDate() - now.getDate();
    });
</script>

{#if isOpen}
    <!-- Backdrop -->
    <!-- svelte-ignore a11y_click_events_have_key_events -->
    <!-- svelte-ignore a11y_no_static_element_interactions -->
    <div
        class="fixed inset-0 bg-black/80 z-50 backdrop-blur-sm transition-opacity"
        onclick={onClose}
        transition:fade={{ duration: 200 }}
    ></div>

    <!-- Panel -->
    <div
        class="fixed inset-y-0 right-0 w-full md:w-[600px] bg-[#0a0e1a] border-l border-cyan-900/40 z-50 flex flex-col shadow-[-10px_0_30px_-5px_rgba(0,0,0,0.5)]"
        transition:fly={{ x: 600, duration: 300, easing: cubicOut }}
    >
        <!-- Header -->
        <div class="border-b border-cyan-900/40 p-4 md:p-6 bg-slate-900/30">
            <div class="flex items-start justify-between mb-4">
                <h2
                    class="text-lg md:text-xl text-cyan-400 font-mono tracking-widest font-bold"
                >
                    GLOBAL CLEARANCE LEADERBOARD
                </h2>
                <button
                    onclick={onClose}
                    class="text-cyan-400 hover:text-cyan-300 transition-colors p-1"
                    aria-label="Close leaderboard"
                >
                    <X class="w-5 h-5" />
                </button>
            </div>

            <div class="space-y-2 text-sm font-mono">
                <div class="flex items-center justify-between">
                    <span class="text-cyan-500/60 tracking-wider"
                        >CURRENT CLEARANCE</span
                    >
                    <span class="text-cyan-300 font-bold tracking-wider"
                        >{currentUserRank()}</span
                    >
                </div>
                <div class="flex items-center justify-between">
                    <span class="text-cyan-500/60 tracking-wider">RESET IN</span
                    >
                    <span class="text-cyan-300 font-bold"
                        >{daysUntilReset()} DAYS</span
                    >
                </div>
            </div>
        </div>

        <!-- Table Header -->
        <div
            class="border-b border-cyan-900/40 px-4 md:px-6 py-3 bg-slate-900/20"
        >
            <div
                class="grid grid-cols-[60px_1fr_100px] gap-4 text-xs text-cyan-500/60 tracking-widest font-mono"
            >
                <div>POSITION</div>
                <div>USERNAME</div>
                <div class="text-right">POINTS</div>
            </div>
        </div>

        <!-- Table Content -->
        <div class="flex-1 overflow-y-auto">
            <div class="px-4 md:px-6">
                {#if loading}
                    <div
                        class="py-8 text-center text-cyan-500/60 font-mono text-xs tracking-widest animate-pulse"
                    >
                        LOADING CLEARANCE DATA...
                    </div>
                {:else if error}
                    <div
                        class="py-8 text-center text-red-400/80 font-mono text-xs tracking-widest"
                    >
                        {error}
                    </div>
                {:else if leaderboard.length === 0}
                    <div
                        class="py-8 text-center text-cyan-500/60 font-mono text-xs tracking-widest"
                    >
                        NO OPERATIVES FOUND
                    </div>
                {:else}
                    {#each leaderboard as entry, index}
                        {@const isCurrent = isCurrentUser(entry)}
                        <div
                            class={`grid grid-cols-[60px_1fr_100px] gap-4 py-3 border-b border-cyan-900/20 font-mono text-sm ${
                                isCurrent
                                    ? "bg-cyan-900/10 text-cyan-300 font-bold"
                                    : "text-cyan-400/80"
                            }`}
                        >
                            <div class="text-cyan-500/60 font-mono">
                                {String(index + 1).padStart(2, "0")}
                            </div>
                            <div class="truncate">
                                {entry.username}
                                {#if isCurrent}
                                    <span
                                        class="ml-2 text-xs text-cyan-500/60 tracking-wider"
                                        >[YOU]</span
                                    >
                                {/if}
                            </div>
                            <div class="text-right tabular-nums tracking-wider">
                                {entry.points}
                            </div>
                        </div>
                    {/each}
                {/if}
            </div>
        </div>

        <!-- Footer Info -->
        <div
            class="border-t border-cyan-900/40 px-4 md:px-6 py-3 bg-slate-900/30"
        >
            <p class="text-xs text-cyan-500/50 font-mono tracking-wide">
                LIVE DATA — {leaderboard.length} OPERATIVES RANKED
            </p>
        </div>
    </div>
{/if}
