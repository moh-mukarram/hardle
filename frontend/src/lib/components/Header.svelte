<script lang="ts">
    import { Menu } from "lucide-svelte";
    import SessionTimer from "./SessionTimer.svelte";

    interface Props {
        timeRemaining: number;
        sessionTimeLimit: number;
        onLeaderboardOpen?: () => void;
    }

    let {
        timeRemaining,
        sessionTimeLimit,
        onLeaderboardOpen = () => {},
    }: Props = $props();
</script>

<header class="border-b border-cyan-900/40 bg-slate-900/30 backdrop-blur-sm">
    <div
        class="max-w-[1600px] mx-auto px-4 lg:px-6 py-3 lg:py-4 flex items-center justify-between"
    >
        <!-- Left - Logo -->
        <div class="flex items-center gap-3">
            <Menu class="w-5 h-5 text-cyan-500/60" />
            <h1
                class="text-xl lg:text-2xl font-bold tracking-[0.3em] text-cyan-400"
            >
                HARDLE
            </h1>
        </div>

        <!-- Center - Timer (Desktop only) -->
        <div class="hidden lg:block">
            <SessionTimer {timeRemaining} {sessionTimeLimit} />
        </div>

        <!-- Right - Leaderboard Button -->
        <div>
            <button
                onclick={onLeaderboardOpen}
                class="px-3 py-1.5 lg:px-4 lg:py-2 border border-cyan-900/60 bg-slate-900/40 text-cyan-400 font-mono text-xs lg:text-sm tracking-wider uppercase rounded hover:bg-slate-800/60 hover:border-cyan-700 transition-all hover:shadow-[0_0_8px_rgba(6,182,212,0.3)]"
            >
                Leaderboard
            </button>
        </div>
    </div>
</header>
